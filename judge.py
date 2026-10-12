"""Bounded local Python execution. This is NOT an OS security sandbox.

Submitted programs run with the current user's permissions. Only run code you
trust. -I isolates Python imports/environment, not filesystem or network access.
"""

import math
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path

# Allow time for large valid inputs and output on desktop systems.
CASE_TIMEOUT = 5.0
SUBMISSION_TIMEOUT = 35.0
# Large arrays and interval lists can legitimately print several megabytes.
# Enumeration problems may opt into a larger per-problem limit.
OUTPUT_LIMIT = 4 * 1024 * 1024


def _terminate(process):
    if os.name == "nt":
        if process.poll() is None:
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    timeout=3, creationflags=subprocess.CREATE_NO_WINDOW,
                )
            except (OSError, subprocess.TimeoutExpired):
                pass
            if process.poll() is None:
                process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)


def _windows_job(process):
    """Best-effort child tree cleanup on Windows, including exited parents."""
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class BasicLimits(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_longlong),
                ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            ]

        class IoCounters(ctypes.Structure):
            _fields_ = [(name, ctypes.c_ulonglong) for name in
                        ("ReadOperationCount", "WriteOperationCount",
                         "OtherOperationCount", "ReadTransferCount",
                         "WriteTransferCount", "OtherTransferCount")]

        class ExtendedLimits(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", BasicLimits),
                        ("IoInfo", IoCounters),
                        ("ProcessMemoryLimit", ctypes.c_size_t),
                        ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t),
                        ("PeakJobMemoryUsed", ctypes.c_size_t)]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        kernel.CreateJobObjectW.restype = wintypes.HANDLE
        kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                                   ctypes.c_void_p, wintypes.DWORD]
        kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.CreateJobObjectW(None, None)
        if not handle:
            return None
        limits = ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = 0x2000  # KILL_ON_JOB_CLOSE
        if not kernel.SetInformationJobObject(handle, 9, ctypes.byref(limits),
                                              ctypes.sizeof(limits)) or not \
                kernel.AssignProcessToJobObject(handle, int(process._handle)):
            kernel.CloseHandle(handle)
            return None
        return lambda: kernel.CloseHandle(handle)
    except (ImportError, OSError, AttributeError):
        return None


@contextmanager
def _working_directory():
    directory = tempfile.TemporaryDirectory(prefix="acm-hot100-")
    try:
        yield directory.name
    finally:
        # Closing a Windows job kills its children asynchronously. Even a child
        # that closed its output pipes can briefly retain the working directory.
        deadline = time.monotonic() + 3
        while True:
            try:
                directory.cleanup()
                break
            except PermissionError:
                if os.name != "nt" or time.monotonic() >= deadline:
                    raise
                time.sleep(0.02)


def execute(code, stdin, timeout=CASE_TIMEOUT, output_limit=OUTPUT_LIMIT):
    started = time.monotonic()
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    output_size = 0
    output_lock = threading.Lock()
    exceeded = threading.Event()
    status = "Finished"
    with _working_directory() as directory:
        script = Path(directory) / "main.py"
        script.write_text(code, encoding="utf-8")
        options = {"start_new_session": True} if os.name != "nt" else {
            "creationflags": subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
        }
        process = subprocess.Popen(
            # Batch programs should retain normal stdout buffering: unbuffered
            # print(*values) performs a pipe write for every token and separator.
            [sys.executable, "-I", "-X", "utf8", str(script)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=directory, **options
        )
        close_job = _windows_job(process)

        def read_output(name, stream):
            nonlocal output_size
            try:
                while True:
                    chunk = os.read(stream.fileno(), 8192)
                    if not chunk:
                        break
                    with output_lock:
                        remaining = max(0, output_limit - output_size)
                        buffers[name].extend(chunk[:remaining])
                        output_size += len(chunk)
                        if output_size > output_limit:
                            exceeded.set()
            except (OSError, ValueError):
                pass
            finally:
                stream.close()

        def write_input():
            try:
                process.stdin.write(stdin.encode("utf-8"))
                process.stdin.flush()
            except (BrokenPipeError, OSError, ValueError):
                pass
            finally:
                process.stdin.close()

        workers = [threading.Thread(target=read_output,
                                    args=(name, getattr(process, name)), daemon=True)
                   for name in ("stdout", "stderr")]
        workers.append(threading.Thread(target=write_input, daemon=True))
        for worker in workers:
            worker.start()
        try:
            deadline = started + max(0.01, timeout)
            while process.poll() is None:
                if exceeded.is_set():
                    status = "Output Limit Exceeded"
                    break
                if time.monotonic() >= deadline:
                    status = "Time Limit Exceeded"
                    break
                exceeded.wait(min(0.01, max(0, deadline - time.monotonic())))
        finally:
            # Terminate the job/group, including children of a finished parent.
            if close_job is not None:
                close_job()
            _terminate(process)
            for worker in workers:
                worker.join(timeout=1)
        if exceeded.is_set():
            status = "Output Limit Exceeded"
        elif status == "Finished" and process.returncode:
            status = "Runtime Error"
    return {
        "status": status,
        "stdout": bytes(buffers["stdout"]).decode("utf-8", errors="replace").replace("\r\n", "\n"),
        "stderr": bytes(buffers["stderr"]).decode("utf-8", errors="replace").replace("\r\n", "\n"),
        "elapsed_ms": round((time.monotonic() - started) * 1000, 2),
    }


def matches(actual, expected, mode="tokens"):
    if mode == "unordered_lines":
        normalize = lambda value: sorted(" ".join(line.split()) for line in
                                         value.splitlines() if line.strip())
        return normalize(actual) == normalize(expected)
    if mode == "unordered_tokens":
        return sorted(actual.split()) == sorted(expected.split())
    if mode == "float":
        got, wanted = actual.split(), expected.split()
        if len(got) != len(wanted):
            return False
        for left, right in zip(got, wanted):
            try:
                number, target = float(left), float(right)
            except ValueError:
                if left != right:
                    return False
                continue
            if not (math.isfinite(number) and math.isfinite(target)) or not \
                    math.isclose(number, target, rel_tol=1e-6, abs_tol=1e-6):
                return False
        return True
    if mode != "tokens":
        raise ValueError("Unknown comparison mode: %s" % mode)
    return actual.split() == expected.split()


def submit(problem, code, checker=None):
    started = time.monotonic()
    tests = problem["tests"]
    result = {"status": "Accepted", "passed": 0, "total": len(tests)}
    if not tests:
        raise ValueError("Cannot judge a problem with no tests")
    for index, case in enumerate(tests, 1):
        remaining = SUBMISSION_TIMEOUT - (time.monotonic() - started)
        if remaining <= 0:
            run = {"status": "Time Limit Exceeded", "stdout": "", "stderr": ""}
        else:
            run = execute(code, case["input"],
                          timeout=min(problem.get("case_timeout", CASE_TIMEOUT), remaining),
                          output_limit=problem.get("output_limit", OUTPUT_LIMIT))
        status = run["status"]
        if status == "Finished":
            try:
                correct = checker(case["input"], run["stdout"], case["output"]) \
                    if checker else matches(run["stdout"], case["output"],
                                           problem.get("compare", "tokens"))
            except (ValueError, TypeError, IndexError, KeyError, OverflowError):
                correct = False
            status = "Accepted" if correct else "Wrong Answer"
        if status != "Accepted":
            result["status"] = status
            result["case"] = {"index": index, "input": case["input"],
                              "expected": case["output"], "actual": run["stdout"],
                              "stderr": run["stderr"]}
            break
        result["passed"] += 1
    result["elapsed_ms"] = round((time.monotonic() - started) * 1000, 2)
    return result
