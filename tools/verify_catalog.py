#!/usr/bin/env python3
"""Independently validate the bundled Hot 100 catalog and its reference programs.

Run from any directory: python tools/verify_catalog.py
Use --id 1 49 to focus on selected problems. Expected outputs are never generated
from reference programs. Each execution is a fresh Python process (3 s default).
Only run this developer utility with the trusted, bundled problem modules.
"""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.util
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
# Official study plan, checked 2026-10-12. The old 2cktkvj list differs.
SOURCE = "https://leetcode.cn/studyplan/top-100-liked/"
OFFICIAL_GROUPS = {
    "哈希": (1, 49, 128),
    "双指针": (283, 11, 15, 42),
    "滑动窗口": (3, 438),
    "子串": (560, 239, 76),
    "普通数组": (53, 56, 189, 238, 41),
    "矩阵": (73, 54, 48, 240),
    "链表": (160, 206, 234, 141, 142, 21, 2, 19, 24, 25, 138, 148, 23, 146),
    "二叉树": (94, 104, 226, 101, 543, 102, 108, 98, 230, 199, 114, 105, 437, 236, 124),
    "图论": (200, 994, 207, 208),
    "回溯": (46, 78, 17, 39, 22, 79, 131, 51),
    "二分查找": (35, 74, 34, 33, 153, 4),
    "栈": (20, 155, 394, 739, 84),
    "堆": (215, 347, 295),
    "贪心算法": (121, 55, 45, 763),
    "动态规划": (70, 118, 198, 279, 322, 139, 300, 152, 416, 32),
    "多维动态规划": (62, 64, 5, 1143, 72),
    "技巧": (136, 169, 75, 31, 287),
}
EASY = {1, 283, 160, 206, 234, 141, 21, 94, 104, 226, 101, 543,
        108, 35, 20, 121, 70, 118, 136, 169}
HARD = {42, 239, 76, 41, 25, 23, 124, 51, 4, 84, 295, 32}
OFFICIAL = {pid: (category, "Easy" if pid in EASY else
                  "Hard" if pid in HARD else "Medium")
            for category, ids in OFFICIAL_GROUPS.items() for pid in ids}
TEXT_FIELDS = ("title", "slug", "difficulty", "category", "description",
               "input_format", "output_format", "starter", "solution", "explanation")
MODES = {"tokens", "float", "unordered_lines", "unordered_tokens"}
GARBAGE = "__THIS_IS_NOT_A_VALID_ANSWER__\n"


def compare(actual, expected, mode):
    """Independent implementation of the documented output contract."""
    if mode == "tokens":
        return actual.split() == expected.split()
    if mode == "unordered_tokens":
        return Counter(actual.split()) == Counter(expected.split())
    if mode == "unordered_lines":
        def lines(value):
            return Counter(" ".join(line.split()) for line in value.splitlines()
                           if line.strip())
        return lines(actual) == lines(expected)
    if mode == "float":
        got, wanted = actual.split(), expected.split()
        if len(got) != len(wanted):
            return False
        for left, right in zip(got, wanted):
            try:
                a, b = float(left), float(right)
            except ValueError:
                if left != right:
                    return False
            else:
                if not math.isfinite(a) or not math.isfinite(b):
                    return False
                if not math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-6):
                    return False
        return True
    raise ValueError("unsupported comparison mode: " + str(mode))


def load_parts():
    problems, checkers, owners, errors = [], {}, {}, []
    # Do not use catalog.__init__: verify duplicates before any aggregation hides them.
    for path in sorted((ROOT / "catalog").glob("part_*.py")):
        try:
            spec = importlib.util.spec_from_file_location("verify_" + path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            entries = module.PROBLEMS
            if not isinstance(entries, list):
                raise ValueError("PROBLEMS must be a list")
            for problem in entries:
                if not isinstance(problem, dict):
                    errors.append(path.name + ": non-dictionary problem")
                    continue
                pid = problem.get("id")
                if type(pid) is not int:
                    errors.append(path.name + ": id must be an integer")
                    continue
                if pid in owners:
                    errors.append("#%s: duplicate ID in %s and %s" %
                                  (pid, owners[pid], path.name))
                owners[pid] = path.name
                problems.append(problem)
            for pid, checker in getattr(module, "CHECKERS", {}).items():
                if type(pid) is not int or not callable(checker):
                    errors.append(path.name + ": invalid checker entry " + repr(pid))
                elif pid in checkers:
                    errors.append("#%s: duplicate checker" % pid)
                else:
                    checkers[pid] = checker
        except Exception as exc:
            errors.append("%s: import failed: %s: %s" %
                          (path.name, type(exc).__name__, exc))
    return problems, checkers, owners, errors


def schema_errors(problem):
    errors = []
    pid = problem["id"]
    for key in TEXT_FIELDS:
        if not isinstance(problem.get(key), str) or not problem[key].strip():
            errors.append(key + " must be a nonempty string")
        elif "\ufffd" in problem[key]:
            errors.append(key + " contains a Unicode replacement character")
    if pid not in OFFICIAL:
        errors.append("ID is not in the official Hot 100 study plan")
    else:
        category, difficulty = OFFICIAL[pid]
        if problem.get("category") != category:
            errors.append("category must be " + category)
        if problem.get("difficulty") != difficulty:
            errors.append("difficulty must be " + difficulty)
    if problem.get("compare", "tokens") not in MODES:
        errors.append("invalid comparison mode")
    constraints = problem.get("constraints")
    if not isinstance(constraints, list) or not constraints or not all(
            isinstance(value, str) and value.strip() for value in constraints):
        errors.append("constraints must be a nonempty list of nonempty strings")
    for key, minimum in (("examples", 1), ("tests", 5)):
        cases = problem.get(key)
        if not isinstance(cases, list) or len(cases) < minimum:
            errors.append("%s must have at least %d entries" % (key, minimum))
            continue
        for i, case in enumerate(cases, 1):
            if not isinstance(case, dict):
                errors.append("%s[%d] must be a dictionary" % (key, i))
                continue
            for field in ("input", "output"):
                if not isinstance(case.get(field), str):
                    errors.append("%s[%d].%s must be a string" % (key, i, field))
            if key == "examples" and (not isinstance(case.get("explanation"), str)
                                      or not case["explanation"].strip()):
                errors.append("examples[%d].explanation must be nonempty" % i)
        if key == "tests" and all(isinstance(case, dict) and
                                   isinstance(case.get("input"), str) for case in cases):
            if len({case["input"] for case in cases}) < 5:
                errors.append("tests must include at least five distinct inputs")
    for key in ("starter", "solution"):
        try:
            compile(problem.get(key, ""), "#%s %s" % (pid, key), "exec")
        except (SyntaxError, TypeError, ValueError) as exc:
            errors.append("%s does not compile: %s" % (key, exc))
    return errors


def accepted(problem, checker, stdin, actual, expected):
    if checker is not None:
        result = checker(stdin, actual, expected)
        if type(result) is not bool:
            raise TypeError("custom checker must return bool, got " + type(result).__name__)
        return result
    return compare(actual, expected, problem.get("compare", "tokens"))


def short(value, limit=220):
    result = repr(value)
    return result if len(result) <= limit else result[:limit] + "..."


def verify_problem(problem, checker, timeout):
    errors = schema_errors(problem)
    if errors:
        return 0, errors
    cases = [("test %d" % i, case) for i, case in enumerate(problem["tests"], 1)]
    # Examples can have different content from hidden tests and must also execute.
    existing = {(case["input"], case["output"]) for case in problem["tests"]}
    cases.extend(("example %d" % i, case)
                 for i, case in enumerate(problem["examples"], 1)
                 if (case["input"], case["output"]) not in existing)
    constants = {"empty": "", "zero": "0\n", "one": "1\n", "true": "true\n",
                 "false": "false\n", "null": "null\n"}
    constant_accepts = Counter()
    executed = 0
    with tempfile.TemporaryDirectory(prefix="hot100-verify-") as directory:
        script = Path(directory) / "solution.py"
        script.write_text(problem["solution"], encoding="utf-8")
        for label, case in cases:
            stdin, expected = case["input"], case["output"]
            try:
                if not accepted(problem, checker, stdin, expected, expected):
                    errors.append(label + ": fixed expected output rejected by checker")
                if accepted(problem, checker, stdin, GARBAGE, expected):
                    errors.append(label + ": checker accepts arbitrary garbage")
                for name, value in constants.items():
                    if accepted(problem, checker, stdin, value, expected):
                        constant_accepts[name] += 1
                if expected.split() and accepted(problem, checker, stdin, "", expected):
                    errors.append(label + ": checker accepts empty output for nonempty answer")
            except Exception as exc:
                errors.append(label + ": checker raised " + repr(exc))
            options = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
            try:
                run = subprocess.run([sys.executable, "-I", "-X", "utf8", str(script)],
                                     input=stdin, capture_output=True, text=True,
                                     encoding="utf-8", errors="replace", cwd=directory,
                                     timeout=timeout, **options)
                executed += 1
                if run.returncode:
                    errors.append(label + ": reference runtime error " + short(run.stderr))
                elif not accepted(problem, checker, stdin, run.stdout, expected):
                    errors.append(label + ": reference wrong answer; expected=" +
                                  short(expected) + "; actual=" + short(run.stdout))
            except subprocess.TimeoutExpired:
                executed += 1
                errors.append(label + ": reference exceeded %.2f s" % timeout)
            except Exception as exc:
                errors.append(label + ": execution/checker raised " + repr(exc))
    for name, count in constant_accepts.items():
        if count == len(cases):
            errors.append("all cases accept constant %s output; insufficient discriminating tests" % name)
    return executed, errors


def manual_checker_probes(by_id, checkers):
    """Hand-written alternative answers, independent of the reference programs.

    Protocols are documented in each problem's input_format/output_format.
    These fixtures use the actual authored ACM protocols: tree #108 emits a
    level-order line, with null placeholders and no leading token count.
    """
    probes = [
        (1, "4 9\n2 7 11 15\n", "1 0\n", "0 1\n", True,
         "reversed two-sum indices"),
        (1, "4 9\n2 7 11 15\n", "0 0\n", "0 1\n", False,
         "same two-sum index twice"),
        (49, "6\neat\ntea\ntan\nate\nnat\nbat\n",
         "3\n1\nbat\n2\nnat\ntan\n3\nate\ntea\neat\n",
         "3\n3\neat\ntea\nate\n2\ntan\nnat\n1\nbat\n", True,
         "reordered groups and reordered words"),
        (49, "3\na\na\nb\n", "2\n1\na\n1\nb\n",
         "2\n2\na\na\n1\nb\n", False, "lost duplicate word"),
        (49, "2\nab\nba\n", "2\n1\nab\n1\nba\n", "1\n2\nab\nba\n",
         False, "one anagram class incorrectly split"),
        (5, "babad\n", "aba\n", "bab\n", True,
         "another longest palindrome"),
        (5, "abc\n", "c\n", "a\n", True,
         "another length-one maximum"),
        (5, "babad\n", "a\n", "bab\n", False,
         "palindrome is not longest"),
        (5, "babad\n", "bad\n", "bab\n", False,
         "same-length substring is not a palindrome"),
        (5, "babad\n", "aaa\n", "bab\n", False,
         "same-length palindrome absent from input"),
        (108, "5\n-10 -3 0 5 9\n", "0 -10 5 null -3 null 9\n",
         "0 -3 9 -10 null 5\n", True, "different valid balanced BST"),
        (108, "2\n1 2\n", "1 null 2\n", "2 1\n", True,
         "lower midpoint with two nodes"),
        (108, "4\n1 2 3 4\n", "1 null 2 null 3 null 4\n",
         "3 2 4 1\n", False, "ordered but unbalanced BST"),
        (108, "3\n1 2 3\n", "2 3 1\n", "2 1 3\n", False,
         "balanced tree violates BST ordering"),
        (108, "3\n1 2 3\n", "2 1 3 null null null null 9\n",
         "2 1 3\n", False, "unreachable extra tree node"),
    ]
    errors, total = [], 0
    for pid, stdin, actual, expected, want, label in probes:
        if pid not in by_id:
            continue
        total += 1
        try:
            got = accepted(by_id[pid], checkers.get(pid), stdin, actual, expected)
            if got != want:
                errors.append("#%s: manual %s: expected acceptance %s, got %s" %
                              (pid, label, want, got))
        except Exception as exc:
            errors.append("#%s: manual %s: raised %r" % (pid, label, exc))
    return total, errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", type=int, nargs="+", help="only verify these problem IDs")
    parser.add_argument("--timeout", type=float, default=3.0,
                        help="fresh subprocess timeout in seconds per case (default 3)")
    parser.add_argument("--workers", type=int, default=4,
                        help="parallel problem verifications (default 4)")
    args = parser.parse_args(argv)
    if args.timeout <= 0 or args.workers < 1:
        parser.error("timeout and workers must be positive")
    started = time.monotonic()
    problems, checkers, owners, errors = load_parts()
    all_ids = {p["id"] for p in problems}
    if args.id:
        missing = set(args.id) - all_ids
        if missing:
            errors.append("requested IDs absent: " + str(sorted(missing)))
        problems = [p for p in problems if p["id"] in args.id]
    else:
        missing, extra = set(OFFICIAL) - all_ids, all_ids - set(OFFICIAL)
        if missing:
            errors.append("missing official IDs: " + str(sorted(missing)))
        if extra:
            errors.append("unexpected IDs: " + str(sorted(extra)))
        if len(problems) != 100:
            errors.append("expected exactly 100 problems, found %d" % len(problems))
        counts = Counter(p.get("category") for p in problems)
        wanted = Counter({category: len(ids) for category, ids in OFFICIAL_GROUPS.items()})
        if counts != wanted:
            errors.append("category counts differ: actual=" + str(dict(counts)))
        difficulty = Counter(p.get("difficulty") for p in problems)
        if difficulty != Counter(Easy=20, Medium=68, Hard=12):
            errors.append("difficulty totals must be Easy=20, Medium=68, Hard=12; actual=" +
                          str(dict(difficulty)))
        for pid in checkers.keys() - all_ids:
            errors.append("checker without problem: #%s" % pid)
    slugs = [p.get("slug") for p in problems if isinstance(p.get("slug"), str)]
    if len(slugs) != len(set(slugs)):
        errors.append("duplicate problem slugs")
    total_cases = 0
    completed = 0
    failed_problems = set()
    print("Verifying %d problems with %d workers, %.1f s per case..." %
          (len(problems), args.workers, args.timeout), flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        future_ids = {pool.submit(verify_problem, problem, checkers.get(problem["id"]),
                                  args.timeout): problem["id"] for problem in problems}
        for future in as_completed(future_ids):
            pid = future_ids[future]
            completed += 1
            try:
                count, failures = future.result()
                total_cases += count
            except Exception as exc:
                failures = ["verification raised " + repr(exc)]
            if failures:
                failed_problems.add(pid)
                errors.extend("#%s (%s): %s" % (pid, owners[pid], item) for item in failures)
            if completed % 10 == 0 or completed == len(problems):
                print("  %d/%d problems; %d subprocess cases; %d problem failures" %
                      (completed, len(problems), total_cases, len(failed_problems)), flush=True)
    by_id = {problem["id"]: problem for problem in problems}
    manual_count, manual_errors = manual_checker_probes(by_id, checkers)
    errors.extend(manual_errors)
    print("Problems: %d | Cases executed: %d | Manual probes: %d | Categories: %d" %
          (len(problems), total_cases, manual_count,
           len({problem.get("category") for problem in problems})))
    print("Difficulty: " + str(dict(Counter(p.get("difficulty") for p in problems))))
    print("Elapsed: %.2f s" % (time.monotonic() - started))
    if errors:
        print("FAIL (%d findings):" % len(errors))
        for item in errors:
            print(" - " + item)
        return 1
    print("PASS: fixed expectations, reference solutions, and checker probes agree.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
