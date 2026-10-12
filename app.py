#!/usr/bin/env python3
"""ACM Hot 100: offline, single-user Python practice on 127.0.0.1."""

import argparse
import hashlib
import hmac
import json
import math
import mimetypes
import os
import secrets
import socket
import sqlite3
import sys
import threading
import webbrowser
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

import catalog
import judge

ROOT = Path(__file__).resolve().parent
MAX_CODE = 64 * 1024
MAX_NOTES = 16 * 1024
# The largest catalog inputs contain 200,000 signed integers (about 2.4 MB).
MAX_STDIN = 4 * 1024 * 1024
MAX_BODY = 8 * 1024 * 1024
MAX_BACKUP = 32 * 1024 * 1024
MAX_IMPORT_SUBMISSIONS = 100000
SUBMISSION_STATUSES = {
    "Accepted", "Wrong Answer", "Runtime Error", "Time Limit Exceeded",
    "Output Limit Exceeded",
}
PROGRESS_STATUSES = {"unseen", "attempted", "solved"}
JUDGE_LOCK = threading.BoundedSemaphore(1)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class ApiError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def bounded_text(value, field, limit):
    if not isinstance(value, str):
        raise ApiError("%s 必须是字符串" % field)
    try:
        size = len(value.encode("utf-8"))
    except UnicodeEncodeError:
        raise ApiError("%s 包含无效 Unicode 字符" % field)
    if size > limit:
        raise ApiError("%s 超出大小限制（%s KB）" % (field, limit // 1024), 413)
    return value


def integer(value, field, minimum=0, maximum=10**9):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ApiError("%s 必须是范围内的整数" % field)
    return value


def timestamp(value):
    if not isinstance(value, str) or len(value) > 40:
        raise ApiError("无效的备份时间")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or not 1970 <= parsed.year <= 2200:
            raise ValueError()
        return parsed.astimezone(timezone.utc).isoformat(timespec="milliseconds")
    except ValueError:
        raise ApiError("无效的备份时间")


def fingerprint(item):
    keys = ("problem_id", "status", "passed", "total", "elapsed_ms", "created_at", "code")
    raw = json.dumps({key: item[key] for key in keys}, ensure_ascii=False,
                     sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class Store:
    def __init__(self, directory):
        Path(directory).mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.connection = sqlite3.connect(str(Path(directory) / "progress.sqlite3"),
                                          check_same_thread=False, timeout=10)
        self.connection.row_factory = sqlite3.Row
        with self.connection:
            self.connection.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS progress (
                    problem_id INTEGER PRIMARY KEY,
                    status TEXT NOT NULL DEFAULT 'unseen',
                    code TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL DEFAULT '',
                    favorite INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    passed INTEGER NOT NULL,
                    total INTEGER NOT NULL,
                    elapsed_ms REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    code TEXT NOT NULL,
                    fingerprint TEXT UNIQUE NOT NULL
                );
                CREATE INDEX IF NOT EXISTS submissions_problem
                    ON submissions(problem_id, id DESC);
            """)

    def close(self):
        with self.lock:
            self.connection.close()

    def progress(self):
        with self.lock:
            rows = self.connection.execute("SELECT * FROM progress").fetchall()
        result = {}
        for row in rows:
            entry = dict(row)
            problem_id = entry.pop("problem_id")
            entry["favorite"] = bool(entry["favorite"])
            result[str(problem_id)] = entry
        return result

    def _save_progress(self, problem_id, updates):
        self.connection.execute(
            "INSERT OR IGNORE INTO progress(problem_id, updated_at) VALUES (?, ?)",
            (problem_id, now()),
        )
        if updates:
            fields = [key for key in ("status", "code", "notes", "favorite", "updated_at")
                      if key in updates]
            sql = "UPDATE progress SET %s WHERE problem_id = ?" % ", ".join(
                "%s = ?" % field for field in fields)
            self.connection.execute(sql, [updates[field] for field in fields] + [problem_id])

    def save_progress(self, problem_id, updates):
        with self.lock, self.connection:
            self._save_progress(problem_id, dict(updates, updated_at=now()))

    def _add_submission(self, item):
        fields = ("problem_id", "status", "passed", "total", "elapsed_ms", "created_at", "code")
        cursor = self.connection.execute(
            "INSERT OR IGNORE INTO submissions (%s, fingerprint) VALUES (%s)" %
            (", ".join(fields), ", ".join("?" for _ in range(len(fields) + 1))),
            [item[field] for field in fields] + [fingerprint(item)],
        )
        return cursor.lastrowid

    def save_submission(self, problem_id, code, result):
        item = {key: result[key] for key in ("status", "passed", "total", "elapsed_ms")}
        item.update(problem_id=problem_id, code=code, created_at=now())
        with self.lock, self.connection:
            submission_id = self._add_submission(item)
            current = self.connection.execute(
                "SELECT status FROM progress WHERE problem_id = ?", (problem_id,)
            ).fetchone()
            solved = result["status"] == "Accepted" or (current and current["status"] == "solved")
            self._save_progress(problem_id, {
                "status": "solved" if solved else "attempted", "updated_at": now(),
            })
        return submission_id

    def submissions(self, problem_id=None):
        with self.lock:
            if problem_id is None:
                rows = self.connection.execute("SELECT * FROM submissions ORDER BY id").fetchall()
            else:
                rows = self.connection.execute(
                    "SELECT * FROM submissions WHERE problem_id = ? ORDER BY id DESC", (problem_id,)
                ).fetchall()
        return [{key: row[key] for key in row.keys() if key != "fingerprint"} for row in rows]

    def export(self):
        with self.lock:
            return {"version": 1, "progress": self.progress(), "submissions": self.submissions()}

    def merge(self, progress, submissions):
        with self.lock, self.connection:
            existing = self.progress()
            for problem_id, incoming in progress.items():
                current = existing.get(problem_id)
                chosen = dict(incoming if not current or
                              incoming["updated_at"] >= current["updated_at"] else current)
                ranks = {"unseen": 0, "attempted": 1, "solved": 2}
                chosen["status"] = max(incoming["status"],
                                       current["status"] if current else "unseen",
                                       key=ranks.__getitem__)
                self._save_progress(int(problem_id), chosen)
            for item in submissions:
                self._add_submission(item)
                current = self.connection.execute(
                    "SELECT status FROM progress WHERE problem_id = ?", (item["problem_id"],)
                ).fetchone()
                if item["status"] == "Accepted":
                    self._save_progress(item["problem_id"], {"status": "solved"})
                elif not current or current["status"] == "unseen":
                    self._save_progress(item["problem_id"], {"status": "attempted"})


class Application:
    def __init__(self, data_dir, problems=None, checkers=None):
        self.problems = catalog.BY_ID if problems is None else {p["id"]: p for p in problems}
        self.checkers = catalog.CHECKERS if checkers is None else checkers
        self.token = secrets.token_urlsafe(32)
        self.store = Store(data_dir)
        self.assets = {}
        static_root = ROOT / "static"
        allowed_extensions = {".html", ".css", ".js", ".svg", ".png", ".ico", ".woff", ".woff2"}
        for path in static_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in allowed_extensions:
                continue
            relative = path.relative_to(static_root)
            if any(part.startswith(".") for part in relative.parts):
                continue
            if not path.resolve().is_relative_to(static_root.resolve()):
                continue
            self.assets["/static/" + relative.as_posix()] = path.resolve()
        if "/static/index.html" in self.assets:
            self.assets["/"] = self.assets["/static/index.html"]
            self.assets["/index.html"] = self.assets["/static/index.html"]

    def problem(self, problem_id):
        integer(problem_id, "problem_id", 1)
        if problem_id not in self.problems:
            raise ApiError("题目不存在", 404)
        return self.problems[problem_id]

    def validate_backup(self, data):
        if type(data.get("version")) is not int or data.get("version") != 1:
            raise ApiError("不支持的备份版本")
        progress, submissions = data.get("progress"), data.get("submissions")
        if not isinstance(progress, dict) or len(progress) > len(self.problems):
            raise ApiError("备份进度格式或数量无效")
        if not isinstance(submissions, list) or len(submissions) > MAX_IMPORT_SUBMISSIONS:
            raise ApiError("备份提交记录格式无效或超过 %s 条" % MAX_IMPORT_SUBMISSIONS)
        validated_progress = {}
        for key, entry in progress.items():
            if not isinstance(key, str) or len(key) > 9 or not key.isascii() or not key.isdecimal() or \
                    str(int(key)) != key or not isinstance(entry, dict):
                raise ApiError("备份题目编号无效")
            self.problem(int(key))
            if not isinstance(entry.get("status"), str) or entry["status"] not in PROGRESS_STATUSES:
                raise ApiError("备份进度状态无效")
            if type(entry.get("favorite")) is not bool:
                raise ApiError("备份收藏状态无效")
            validated_progress[key] = {
                "status": entry["status"],
                "code": bounded_text(entry.get("code"), "code", MAX_CODE),
                "notes": bounded_text(entry.get("notes"), "notes", MAX_NOTES),
                "favorite": entry["favorite"],
                "updated_at": timestamp(entry.get("updated_at")),
            }
        validated_submissions = []
        for entry in submissions:
            if not isinstance(entry, dict):
                raise ApiError("备份提交记录无效")
            problem_id = entry.get("problem_id")
            self.problem(problem_id)
            if not isinstance(entry.get("status"), str) or entry["status"] not in SUBMISSION_STATUSES:
                raise ApiError("备份判题状态无效")
            total = integer(entry.get("total"), "total", 1, 10000)
            passed = integer(entry.get("passed"), "passed", 0, total)
            if (entry["status"] == "Accepted") != (passed == total):
                raise ApiError("备份通过数量与状态不一致")
            elapsed = entry.get("elapsed_ms")
            if type(elapsed) not in (int, float) or not 0 <= elapsed <= 3600000 or not math.isfinite(elapsed):
                raise ApiError("备份运行时间无效")
            validated_submissions.append({
                "problem_id": problem_id, "status": entry["status"], "passed": passed,
                "total": total, "elapsed_ms": float(elapsed),
                "created_at": timestamp(entry.get("created_at")),
                "code": bounded_text(entry.get("code"), "code", MAX_CODE),
            })
        return validated_progress, validated_submissions


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    # Windows SO_REUSEADDR permits two live servers to share a port. Repeated
    # double-clicks must fail clearly instead of serving unpredictable instances.
    allow_reuse_address = os.name != "nt"

    def __init__(self, port, application):
        self.application = application
        super().__init__(("127.0.0.1", port), Handler)

    def server_bind(self):
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


class Handler(BaseHTTPRequestHandler):
    server_version = "ACMHot100/1.0"

    @property
    def app(self):
        return self.server.application

    def log_message(self, format_string, *args):
        # No program source or request bodies in server logs.
        pass

    def headers_ok(self):
        hosts = {"127.0.0.1:%s" % self.server.server_port,
                 "localhost:%s" % self.server.server_port}
        if self.server.server_port == 80:
            hosts.update(("127.0.0.1", "localhost"))
        host_headers = self.headers.get_all("Host", [])
        if len(host_headers) != 1 or host_headers[0].lower() not in hosts:
            raise ApiError("仅允许本机访问，请使用启动时显示的网址", 403)
        origin_headers = self.headers.get_all("Origin", [])
        if len(origin_headers) > 1 or (origin_headers and origin_headers[0] not in
                                      {"http://" + host for host in hosts}):
            raise ApiError("拒绝跨站请求", 403)
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            raise ApiError("拒绝跨站请求", 403)

    def respond(self, data, status=200, content_type="application/json; charset=utf-8"):
        body = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8") \
            if not isinstance(data, bytes) else data
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                         "img-src 'self' data:; font-src 'self' data:; connect-src 'self'; "
                         "frame-ancestors 'none'; base-uri 'none'; form-action 'none'; object-src 'none'")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _dispatch(self, post=False):
        try:
            self.headers_ok()
            parsed = urlsplit(self.path)
            if parsed.scheme or parsed.netloc:
                raise ApiError("无效的请求路径", 400)
            path = unquote(parsed.path)
            if post:
                self.handle_post(path)
            else:
                self.handle_get(path)
        except ApiError as error:
            self.respond({"error": str(error)}, error.status)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        except Exception as error:
            print("Request failed: %s" % type(error).__name__, file=sys.stderr)
            try:
                self.respond({"error": "本地服务处理失败，请查看终端并重试"}, 500)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass

    def do_GET(self):
        self._dispatch()

    def do_HEAD(self):
        self._dispatch()

    def do_POST(self):
        self._dispatch(post=True)

    def handle_get(self, path):
        if path == "/api/bootstrap":
            return self.respond({
                "problems": [catalog.summary(problem) for problem in
                             sorted(self.app.problems.values(), key=catalog.order_key)],
                "progress": self.app.store.progress(), "token": self.app.token,
                "python_version": "%d.%d.%d" % sys.version_info[:3],
            })
        if path == "/api/export":
            backup = self.app.store.export()
            if len(backup["submissions"]) > MAX_IMPORT_SUBMISSIONS:
                raise ApiError("历史记录超出可导入备份的数量限制，请直接备份数据目录", 413)
            encoded = json.dumps(backup, ensure_ascii=False, allow_nan=False).encode("utf-8")
            if len(encoded) > MAX_BACKUP:
                raise ApiError("备份超过 32 MB，请直接备份数据目录", 413)
            return self.respond(encoded)
        parts = path.strip("/").split("/")
        if len(parts) in (3, 4) and parts[:2] == ["api", "problems"]:
            if not parts[2].isascii() or not parts[2].isdecimal() or len(parts[2]) > 9:
                raise ApiError("题目不存在", 404)
            problem = self.app.problem(int(parts[2]))
            if len(parts) == 3:
                return self.respond(catalog.public_problem(problem))
            if parts[3] == "solution":
                return self.respond({key: problem[key] for key in ("solution", "explanation", "tutorial") if key in problem})
            if parts[3] == "submissions":
                return self.respond({"submissions": self.app.store.submissions(problem["id"])})
        asset = self.app.assets.get(path)
        if asset is not None:
            kind = mimetypes.guess_type(str(asset))[0] or "application/octet-stream"
            if asset.suffix == ".js":
                kind = "text/javascript"
            if kind.startswith("text/") or kind == "image/svg+xml":
                kind += "; charset=utf-8"
            return self.respond(asset.read_bytes(), content_type=kind)
        raise ApiError("未找到请求的内容", 404)

    def body(self, maximum):
        if self.headers.get("Transfer-Encoding"):
            raise ApiError("不支持此请求编码")
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1 or len(lengths[0]) > 10 or not lengths[0].isascii() or not lengths[0].isdecimal():
            raise ApiError("缺少有效的 Content-Length", 411)
        length = int(lengths[0])
        if length > maximum:
            raise ApiError("请求体超出大小限制", 413)
        if self.headers.get_content_type() != "application/json":
            raise ApiError("请求必须使用 application/json", 415)
        self.connection.settimeout(10)
        raw = self.rfile.read(length)
        if len(raw) != length:
            raise ApiError("请求体不完整")
        try:
            data = json.loads(raw.decode("utf-8"), parse_constant=lambda value:
                              (_ for _ in ()).throw(ValueError(value)))
        except (ValueError, UnicodeError, RecursionError):
            raise ApiError("JSON 格式错误")
        if not isinstance(data, dict):
            raise ApiError("请求体必须是 JSON 对象")
        return data

    def handle_post(self, path):
        provided_tokens = self.headers.get_all("X-Local-Token", [])
        if len(provided_tokens) != 1 or not hmac.compare_digest(
                provided_tokens[0].encode("utf-8"), self.app.token.encode("ascii")):
            raise ApiError("本地会话已失效，请刷新页面", 403)
        if path not in ("/api/progress", "/api/run", "/api/submit", "/api/import"):
            raise ApiError("未找到请求的内容", 404)
        data = self.body(MAX_BACKUP if path == "/api/import" else MAX_BODY)
        if path == "/api/import":
            progress, submissions = self.app.validate_backup(data)
            self.app.store.merge(progress, submissions)
            return self.respond({"ok": True})
        problem = self.app.problem(data.get("problem_id"))
        if path == "/api/progress":
            updates = {}
            for field, limit in (("code", MAX_CODE), ("notes", MAX_NOTES)):
                if field in data:
                    updates[field] = bounded_text(data[field], field, limit)
            if "favorite" in data:
                if type(data["favorite"]) is not bool:
                    raise ApiError("favorite 必须为布尔值")
                updates["favorite"] = data["favorite"]
            self.app.store.save_progress(problem["id"], updates)
            return self.respond({"ok": True})
        code = bounded_text(data.get("code"), "code", MAX_CODE)
        stdin = bounded_text(data.get("stdin", ""), "stdin", MAX_STDIN)
        if not JUDGE_LOCK.acquire(blocking=False):
            raise ApiError("已有程序正在运行，请等待完成后重试", 409)
        try:
            if path == "/api/run":
                result = judge.execute(code, stdin,
                                       timeout=problem.get("case_timeout", judge.CASE_TIMEOUT),
                                       output_limit=problem.get("output_limit", judge.OUTPUT_LIMIT))
            else:
                # Persist this submission before execution. Later autosaved drafts
                # must survive a judging result that arrives after further edits.
                self.app.store.save_progress(problem["id"], {"code": code})
                result = judge.submit(problem, code, self.app.checkers.get(problem["id"]))
                result["submission_id"] = self.app.store.save_submission(problem["id"], code, result)
        finally:
            JUDGE_LOCK.release()
        self.respond(result)


def create_server(port=8765, data_dir=None, problems=None, checkers=None):
    application = Application(data_dir or ROOT / ".local", problems, checkers)
    try:
        return LocalServer(port, application)
    except Exception:
        application.store.close()
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description="ACM Hot 100 本地 Python3 刷题网页")
    parser.add_argument("--port", type=int, default=8765, help="端口号（默认 8765）")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--data-dir", type=Path, default=ROOT / ".local", help="进度数据库目录")
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error("port 必须为 0 到 65535")
    if not catalog.PROBLEMS:
        parser.error("未找到题库，请确认 catalog/part_*.py 完整")
    try:
        server = create_server(args.port, args.data_dir)
    except OSError as error:
        command = "start.bat --port 8766" if os.name == "nt" else "python3 app.py --port 8766"
        parser.exit(1, "无法启动服务：%s\n请关闭已有服务，或尝试 %s\n" % (error, command))
    url = "http://127.0.0.1:%s" % server.server_port
    print("ACM Hot 100 — %s 道题 · Python %s" % (len(catalog.PROBLEMS), sys.version.split()[0]))
    print("打开：%s" % url)
    print("程序以当前用户权限在本机运行，请只运行可信代码。按 Ctrl+C 停止服务。")
    if not args.no_browser:
        timer = threading.Timer(0.3, webbrowser.open, args=(url,))
        timer.daemon = True
        timer.start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止，学习进度已保存。")
    finally:
        server.server_close()
        server.application.store.close()


if __name__ == "__main__":
    main()
