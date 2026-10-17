"""Standard-library regression tests: python -m unittest discover -s tests -v."""

import copy
import http.client
import json
import math
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from pathlib import Path

import app
import catalog
import judge


SOLUTION = "import sys\nprint(sum(map(int, sys.stdin.read().split())))\n"
PROBLEM = {
    "id": 1, "title": "整数求和", "slug": "sum", "difficulty": "Easy", "category": "数组",
    "description": "输出输入整数之和。", "input_format": "若干整数", "output_format": "一个整数",
    "constraints": ["整数绝对值不超过 10^9"],
    "examples": [{"input": "1 2\n", "output": "3\n", "explanation": "1 + 2 = 3"}],
    "tests": [{"input": "1 2\n", "output": "3\n"}, {"input": "0\n", "output": "0\n"},
              {"input": "-2 -3\n", "output": "-5\n"}, {"input": "4\n", "output": "4\n"},
              {"input": "999 1\n", "output": "1000\n"}],
    "starter": "def solve():\n    pass\n", "solution": SOLUTION,
    "explanation": "求和，时间 O(n)，空间 O(n)。", "compare": "tokens",
}


class JudgeTests(unittest.TestCase):
    def test_acm_stdio_unicode(self):
        result = judge.execute("print(input() + '，完成')", "你好\n")
        self.assertEqual(result["status"], "Finished")
        self.assertEqual(result["stdout"], "你好，完成\n")

    def test_runtime_error(self):
        result = judge.execute("raise ValueError('bad')", "")
        self.assertEqual(result["status"], "Runtime Error")
        self.assertIn("ValueError", result["stderr"])

    def test_timeout(self):
        started = time.monotonic()
        result = judge.execute("while True: pass", "", timeout=0.2)
        self.assertEqual(result["status"], "Time Limit Exceeded")
        self.assertLess(time.monotonic() - started, 5)

    def test_bounded_stdout_and_stderr(self):
        code = "import sys\nwhile True:\n sys.stdout.write('x' * 8192)\n sys.stderr.write('y' * 8192)\n"
        result = judge.execute(code, "", timeout=1, output_limit=16384)
        self.assertEqual(result["status"], "Output Limit Exceeded")
        self.assertLessEqual(len(result["stdout"].encode()) + len(result["stderr"].encode()), 16384)

    def test_finite_large_output_is_still_rejected(self):
        result = judge.execute("print('x' * 200000)", "", output_limit=128 * 1024)
        self.assertEqual(result["status"], "Output Limit Exceeded")
        self.assertLessEqual(len(result["stdout"]), 128 * 1024)

    def test_valid_large_output_is_supported(self):
        result = judge.execute("print('x' * 2400000)", "")
        self.assertEqual(result["status"], "Finished")
        self.assertEqual(result["stdout"], "x" * 2400000 + "\n")

    def test_submission_uses_problem_output_limit(self):
        problem = dict(PROBLEM, tests=[{"input": "", "output": "x" * 1024 + "\n"}],
                       output_limit=128)
        result = judge.submit(problem, "print('x' * 1024)")
        self.assertEqual(result["status"], "Output Limit Exceeded")
        self.assertLessEqual(len(result["case"]["actual"]), 128)

    def test_submission_uses_problem_time_limit(self):
        problem = dict(PROBLEM, tests=[{"input": "", "output": "done\n"}],
                       case_timeout=0.1)
        result = judge.submit(problem, "import time; time.sleep(0.5); print('done')")
        self.assertEqual(result["status"], "Time Limit Exceeded")

    def test_stdin_not_consumed_cannot_deadlock(self):
        result = judge.execute("while True: pass", "x" * 131072, timeout=0.2)
        self.assertEqual(result["status"], "Time Limit Exceeded")

    def test_comparison_modes(self):
        self.assertTrue(judge.matches(" 1 2\n", "1\n2"))
        self.assertFalse(judge.matches("2 1", "1 2"))
        self.assertTrue(judge.matches("b a\nc", "c\nb a", "unordered_lines"))
        self.assertFalse(judge.matches("a b\nc", "c\nb a", "unordered_lines"))
        self.assertTrue(judge.matches("2 1 2", "1 2 2", "unordered_tokens"))
        self.assertFalse(judge.matches("2 1", "1 2 2", "unordered_tokens"))
        self.assertTrue(judge.matches("0.333333333", "0.333333", "float"))
        self.assertFalse(judge.matches("nan", "nan", "float"))
        self.assertFalse(judge.matches("inf", "inf", "float"))

    def test_all_cases_required_and_failure_index(self):
        result = judge.submit(PROBLEM, SOLUTION)
        self.assertEqual((result["status"], result["passed"], result["total"]), ("Accepted", 5, 5))
        result = judge.submit(PROBLEM, "print(3)")
        self.assertEqual((result["status"], result["passed"], result["total"]), ("Wrong Answer", 1, 5))
        self.assertEqual(result["case"]["index"], 2)
        self.assertEqual(result["case"]["expected"], "0\n")

    def test_special_checker(self):
        checker = lambda stdin, actual, expected: actual.strip() == "valid"
        result = judge.submit(PROBLEM, "print('valid')", checker)
        self.assertEqual(result["status"], "Accepted")

    def test_child_tree_is_cleaned_after_parent_finishes(self):
        code = "import subprocess, sys\nsubprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)'])\nprint('done')\n"
        started = time.monotonic()
        result = judge.execute(code, "")
        self.assertEqual(result["status"], "Finished")
        self.assertEqual(result["stdout"], "done\n")
        self.assertLess(time.monotonic() - started, 2)

    def test_child_tree_without_inherited_output_is_cleaned(self):
        # A descendant can keep the temporary working directory open even after
        # the parent and both output readers have already finished.
        code = ("import subprocess, sys\n"
                "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)'], "
                "stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
                "print('done')\n")
        started = time.monotonic()
        for _ in range(5):
            result = judge.execute(code, "")
            self.assertEqual(result["status"], "Finished")
            self.assertEqual(result["stdout"], "done\n")
        self.assertLess(time.monotonic() - started, 5)


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix="acm-test-")
        cls.server = app.create_server(0, cls.directory.name, [PROBLEM], {})
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server.application.store.close()
        cls.thread.join(timeout=2)
        cls.directory.cleanup()

    def setUp(self):
        self.token = self.server.application.token
        with self.server.application.store.lock, self.server.application.store.connection:
            self.server.application.store.connection.execute("DELETE FROM progress")
            self.server.application.store.connection.execute("DELETE FROM submissions")

    def request(self, method, path, data=None, headers=None, raw=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=10)
        merged = {"Content-Type": "application/json", "X-Local-Token": self.token}
        merged.update(headers or {})
        body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
        try:
            connection.request(method, path, body, merged)
            response = connection.getresponse()
            content = response.read()
            return response.status, dict(response.getheaders()), json.loads(content) if content else None
        finally:
            connection.close()

    def test_bootstrap_and_public_fields(self):
        status, headers, data = self.request("GET", "/api/bootstrap")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["problems"]), 1)
        self.assertEqual(data["problems"][0]["test_count"], 5)
        self.assertEqual(data["token"], self.token)
        self.assertEqual(headers["Cache-Control"], "no-store")
        _, _, problem = self.request("GET", "/api/problems/1")
        self.assertNotIn("tests", problem)
        self.assertNotIn("solution", problem)
        self.assertEqual(problem["test_count"], 5)
        _, _, solution = self.request("GET", "/api/problems/1/solution")
        self.assertEqual(solution["solution"], SOLUTION)

    def test_solution_exposes_structured_tutorial_without_private_cases(self):
        tutorial = catalog.BY_ID[1]['tutorial']
        with patch.dict(PROBLEM, {'tutorial': tutorial}):
            status, _, solution = self.request('GET', '/api/problems/1/solution')
        self.assertEqual(status, 200)
        self.assertEqual(solution['tutorial'], tutorial)
        self.assertEqual(solution['solution'], SOLUTION)
        self.assertNotIn('tests', solution)

    def test_host_origin_and_token(self):
        for headers in ({"Host": "evil.example"}, {"Origin": "https://evil.example"},
                        {"Origin": "null"}, {"Sec-Fetch-Site": "cross-site"}):
            self.assertEqual(self.request("GET", "/api/bootstrap", headers=headers)[0], 403)
        for token in ("", "invalid"):
            self.assertEqual(self.request("POST", "/api/progress", {"problem_id": 1},
                                          {"X-Local-Token": token})[0], 403)
        origin = "http://127.0.0.1:%s" % self.server.server_port
        self.assertEqual(self.request("POST", "/api/progress", {"problem_id": 1},
                                      {"Origin": origin})[0], 200)

    def test_private_files_and_path_traversal(self):
        for path in ("/app.py", "/judge.py", "/catalog/part_one.py", "/.local/progress.sqlite3",
                     "/static/../app.py", "/static/%2e%2e/app.py", "/static/%2fapp.py", "/api/nope"):
            self.assertEqual(self.request("GET", path)[0], 404, path)

    def test_bad_requests(self):
        for data in ([], None, {"problem_id": True}, {"problem_id": "1"}, {"problem_id": 1, "favorite": 1}):
            self.assertEqual(self.request("POST", "/api/progress", raw=json.dumps(data).encode())[0], 400)
        self.assertEqual(self.request("POST", "/api/run", {"problem_id": 1, "code": "x" * (app.MAX_CODE + 1)})[0], 413)
        self.assertEqual(self.request("POST", "/api/progress", raw=b'{"problem_id":NaN}')[0], 400)
        self.assertEqual(self.request("GET", "/api/problems/999")[0], 404)

    def test_progress_partial_updates_and_literal_html(self):
        literal = "<script>alert('x')</script> & 中文"
        self.request("POST", "/api/progress", {"problem_id": 1, "code": literal, "notes": literal})
        self.request("POST", "/api/progress", {"problem_id": 1, "favorite": True})
        _, headers, result = self.request("GET", "/api/bootstrap")
        entry = result["progress"]["1"]
        self.assertEqual((entry["code"], entry["notes"], entry["favorite"]), (literal, literal, True))
        self.assertIn("application/json", headers["Content-Type"])
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(entry["status"], "unseen")

    def test_run_does_not_mark_solved(self):
        status, _, result = self.request("POST", "/api/run", {"problem_id": 1, "code": SOLUTION, "stdin": "2 4"})
        self.assertEqual((status, result["status"], result["stdout"]), (200, "Finished", "6\n"))
        self.assertEqual(self.request("GET", "/api/bootstrap")[2]["progress"], {})

    def test_maximum_catalog_array_input_can_run(self):
        # Problem 4 allows two arrays of 100,000 values in [-10^9, 10^9].
        stdin = "100000 100000\n" + ("-1000000000 " * 100000 + "\n") * 2
        status, _, result = self.request("POST", "/api/run", {
            "problem_id": 1, "code": "import sys; print(len(sys.stdin.read().split()))", "stdin": stdin,
        })
        self.assertEqual((status, result["status"], result["stdout"]), (200, "Finished", "200002\n"))

    def test_custom_input_remains_bounded(self):
        status = self.request("POST", "/api/run", {
            "problem_id": 1, "code": "print(1)", "stdin": "x" * (app.MAX_STDIN + 1),
        })[0]
        self.assertEqual(status, 413)

    def test_run_uses_problem_output_limit(self):
        with patch.dict(self.server.application.problems[1], {"output_limit": 128}):
            status, _, result = self.request("POST", "/api/run", {
                "problem_id": 1, "code": "print('x' * 1024)",
            })
        self.assertEqual((status, result["status"]), (200, "Output Limit Exceeded"))
        self.assertLessEqual(len(result["stdout"]), 128)

    def test_run_uses_problem_time_limit(self):
        with patch.dict(self.server.application.problems[1], {"case_timeout": 0.1}):
            status, _, result = self.request("POST", "/api/run", {
                "problem_id": 1, "code": "import time; time.sleep(0.5); print('done')",
            })
        self.assertEqual((status, result["status"]), (200, "Time Limit Exceeded"))

    def test_submit_history_and_solved_is_cumulative(self):
        _, _, result = self.request("POST", "/api/submit", {"problem_id": 1, "code": SOLUTION})
        self.assertEqual((result["status"], result["passed"], result["total"]), ("Accepted", 5, 5))
        self.assertIsInstance(result["submission_id"], int)
        _, _, wrong = self.request("POST", "/api/submit", {"problem_id": 1, "code": "print(3)"})
        self.assertEqual(wrong["case"]["index"], 2)
        self.assertEqual(self.request("GET", "/api/bootstrap")[2]["progress"]["1"]["status"], "solved")
        records = self.request("GET", "/api/problems/1/submissions")[2]["submissions"]
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["status"], "Wrong Answer")
        self.assertEqual(records[1]["code"], SOLUTION)
        self.assertNotIn("fingerprint", records[0])

    def test_wrong_submit_marks_attempted(self):
        self.request("POST", "/api/submit", {"problem_id": 1, "code": "print(0)"})
        self.assertEqual(self.request("GET", "/api/bootstrap")[2]["progress"]["1"]["status"], "attempted")

    def test_completed_submission_does_not_overwrite_new_draft(self):
        store = self.server.application.store
        store.save_progress(1, {"code": "old submitted code"})
        store.save_progress(1, {"code": "new draft typed during judging"})
        store.save_submission(1, "old submitted code", {
            "status": "Accepted", "passed": 5, "total": 5, "elapsed_ms": 1.0,
        })
        self.assertEqual(store.progress()["1"]["code"], "new draft typed during judging")
        self.assertEqual(store.progress()["1"]["status"], "solved")
        self.assertEqual(store.submissions(1)[0]["code"], "old submitted code")

    def test_judging_concurrency(self):
        self.assertTrue(app.JUDGE_LOCK.acquire(blocking=False))
        try:
            status = self.request("POST", "/api/run", {"problem_id": 1, "code": "print(1)"})[0]
            self.assertEqual(status, 409)
        finally:
            app.JUDGE_LOCK.release()

    def test_backup_roundtrip_and_deduplication(self):
        self.request("POST", "/api/submit", {"problem_id": 1, "code": SOLUTION})
        self.request("POST", "/api/progress", {"problem_id": 1, "notes": "笔记", "favorite": True})
        backup = self.request("GET", "/api/export")[2]
        for _ in range(2):
            self.assertEqual(self.request("POST", "/api/import", backup)[0], 200)
        exported = self.request("GET", "/api/export")[2]
        self.assertEqual(len(exported["submissions"]), 1)
        self.assertEqual(exported["progress"], backup["progress"])
        with tempfile.TemporaryDirectory() as folder:
            restored = app.Application(folder, [PROBLEM], {})
            try:
                restored.store.merge(*restored.validate_backup(backup))
                self.assertEqual(restored.store.progress(), backup["progress"])
                self.assertEqual(len(restored.store.submissions()), 1)
            finally:
                restored.store.close()

    def test_retired_practice_records_remain_restorable_without_reopening_exercises(self):
        store = self.server.application.store
        store.save_progress(1, {"code": "Hot100 draft", "notes": "原有笔记"})
        for pid in app.RETIRED_PROBLEM_IDS:
            store.save_progress(pid, {"code": "archived draft %s" % pid})
        store.save_submission(10008, "archived submitted code", {
            "status": "Accepted", "passed": 3, "total": 3, "elapsed_ms": 0.1,
        })
        backup = self.request("GET", "/api/export")[2]
        self.assertEqual(len(backup["progress"]), 13)
        for _ in range(2):
            self.assertEqual(self.request("POST", "/api/import", backup)[0], 200)
        self.assertEqual(self.request("GET", "/api/export")[2], backup)
        with tempfile.TemporaryDirectory() as folder:
            restored = app.Application(folder, [PROBLEM], {})
            try:
                restored.store.merge(*restored.validate_backup(backup))
                self.assertEqual(restored.store.progress(), backup["progress"])
                self.assertEqual(restored.store.submissions()[0]["code"], "archived submitted code")
            finally:
                restored.store.close()
        self.assertEqual([p["id"] for p in self.request("GET", "/api/bootstrap")[2]["problems"]], [1])
        for suffix in ("", "/solution", "/submissions"):
            self.assertEqual(self.request("GET", "/api/problems/10008" + suffix)[0], 404)
        for path in ("/api/progress", "/api/run", "/api/submit"):
            self.assertEqual(self.request("POST", path, {"problem_id": 10008, "code": "print(1)"})[0], 404)
        invalid = copy.deepcopy(backup)
        invalid["progress"]["10008"]["favorite"] = 1
        self.assertEqual(self.request("POST", "/api/import", invalid)[0], 400)
        self.assertEqual(self.request("GET", "/api/export")[2], backup)

    def test_export_reports_backups_that_cannot_be_imported(self):
        with patch.object(app, "MAX_BACKUP", 1):
            self.assertEqual(self.request("GET", "/api/export")[0], 413)
        self.request("POST", "/api/submit", {"problem_id": 1, "code": "print(0)"})
        with patch.object(app, "MAX_IMPORT_SUBMISSIONS", 0):
            self.assertEqual(self.request("GET", "/api/export")[0], 413)

    def test_more_than_five_thousand_small_records_are_importable(self):
        row = {"problem_id": 1, "status": "Wrong Answer", "passed": 0, "total": 5,
               "elapsed_ms": 0.1, "created_at": app.now(), "code": "print(0)"}
        backup = {"version": 1, "progress": {}, "submissions": [row] * 5001}
        progress, submissions = self.server.application.validate_backup(backup)
        self.assertEqual(len(submissions), 5001)

    def test_bad_backup_is_atomic(self):
        entry = {"status": "solved", "code": "saved", "notes": "note", "favorite": True, "updated_at": app.now()}
        invalid = {"version": 1, "progress": {"1": entry}, "submissions": [{"problem_id": 999}]}
        self.assertEqual(self.request("POST", "/api/import", invalid)[0], 404)
        self.assertEqual(self.request("GET", "/api/bootstrap")[2]["progress"], {})
        for mutate in (
            lambda b: b.update(version=True),
            lambda b: b["progress"]["1"].update(status=[]),
            lambda b: b["progress"]["1"].update(favorite=1),
            lambda b: b["progress"]["1"].update(updated_at="yesterday"),
        ):
            bad = {"version": 1, "progress": {"1": copy.deepcopy(entry)}, "submissions": []}
            mutate(bad)
            self.assertEqual(self.request("POST", "/api/import", bad)[0], 400)
        self.assertEqual(self.request("GET", "/api/bootstrap")[2]["progress"], {})

    def test_import_cannot_downgrade_attempted_status(self):
        self.request("POST", "/api/submit", {"problem_id": 1, "code": "print(0)"})
        backup = {"version": 1, "submissions": [], "progress": {"1": {
            "status": "unseen", "code": "new draft", "notes": "", "favorite": False,
            "updated_at": "2199-01-01T00:00:00+00:00",
        }}}
        self.assertEqual(self.request("POST", "/api/import", backup)[0], 200)
        progress = self.request("GET", "/api/bootstrap")[2]["progress"]["1"]
        self.assertEqual(progress["status"], "attempted")
        self.assertEqual(progress["code"], "new draft")

    def test_backup_rejects_huge_elapsed_time_without_server_error(self):
        backup = {"version": 1, "progress": {}, "submissions": [{
            "problem_id": 1, "status": "Wrong Answer", "passed": 0, "total": 5,
            "elapsed_ms": 10 ** 1000, "created_at": app.now(), "code": "print(0)",
        }]}
        self.assertEqual(self.request("POST", "/api/import", backup)[0], 400)
        self.assertEqual(self.request("GET", "/api/export")[2]["submissions"], [])

    def test_second_server_cannot_bind_existing_port(self):
        with tempfile.TemporaryDirectory() as directory:
            second = None
            try:
                with self.assertRaises(OSError):
                    second = app.create_server(self.server.server_port, directory, [PROBLEM], {})
            finally:
                if second is not None:
                    second.server_close()
                    second.application.store.close()

    def test_persistence_can_be_reopened(self):
        with tempfile.TemporaryDirectory() as directory:
            store = app.Store(directory)
            store.save_progress(1, {"code": "print(42)", "notes": "中文", "favorite": True})
            store.close()
            reopened = app.Store(directory)
            try:
                self.assertEqual(reopened.progress()["1"]["notes"], "中文")
            finally:
                reopened.close()


if __name__ == "__main__":
    unittest.main()
