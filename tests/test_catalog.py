"""Exercise legal catalog boundaries through the same runner as the web app."""

import itertools
import io
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

from catalog import BY_ID
import judge


class CatalogRuntimeTests(unittest.TestCase):
    def test_verifier_preserves_original_stdin_bytes(self):
        path = Path(__file__).parents[1] / "tools/verify_catalog.py"
        spec = importlib.util.spec_from_file_location("catalog_verifier", path)
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        problem = dict(BY_ID[1], examples=[], compare="tokens",
                       solution="import sys; print(sys.stdin.buffer.read().hex())",
                       tests=[{"input": text, "output": text.encode("utf-8").hex() + "\n"}
                              for text in ("a\r\n\r\nb", "你好\n\nb\n")])
        with patch.object(verifier, "schema_errors", return_value=[]):
            executed, errors = verifier.verify_problem(problem, None, 3)
        self.assertEqual(executed, 2)
        self.assertEqual(errors, [])

    def run_reference(self, problem_id, stdin):
        problem = BY_ID[problem_id]
        result = judge.execute(problem["solution"], stdin,
                               timeout=problem.get("case_timeout", judge.CASE_TIMEOUT),
                               output_limit=problem.get("output_limit", judge.OUTPUT_LIMIT))
        self.assertEqual(result["status"], "Finished",
                         "problem #%s: %s, %.2f ms, stderr=%r" %
                         (problem_id, result["status"], result["elapsed_ms"],
                          result["stderr"][:1000]))
        self.assertEqual(result["stderr"], "")
        return result["stdout"]

    def test_maximum_color_array_is_not_truncated(self):
        # Even this smallest possible output for 100,000 items exceeds 128 KiB.
        values = " ".join(["0"] * 100000) + "\n"
        self.assertEqual(self.run_reference(75, "100000\n" + values), values)

    def test_maximum_permutation_output(self):
        values = [-100, -99, -98, -97, -96, -95, -94]
        stdin = "7\n" + " ".join(map(str, values)) + "\n"
        lines = self.run_reference(46, stdin).splitlines()
        answers = [tuple(map(int, line.split())) for line in lines[1:]]
        expected = set(itertools.permutations(values))
        self.assertEqual(int(lines[0]), len(expected))
        self.assertEqual(len(answers), len(expected))
        self.assertEqual(set(answers), expected)

    def test_maximum_palindrome_partition_output(self):
        word = "a" * 15
        lines = self.run_reference(131, word + "\n").splitlines()
        # Every subset of the fourteen inter-character cuts is a valid answer.
        self.assertEqual(int(lines[0]), 2 ** 14)
        self.assertEqual(len(lines) - 1, 2 ** 14)
        self.assertEqual(len(set(lines[1:])), 2 ** 14)
        for line in lines[1:]:
            parts = line.split()
            self.assertEqual("".join(parts), word)
            self.assertTrue(all(part == part[::-1] for part in parts))

    def test_maximum_median_input(self):
        row = " ".join(["-1000000000"] * 100000) + "\n"
        result = self.run_reference(4, "100000 100000\n" + row + row)
        self.assertEqual(float(result.strip()), -1000000000)

    def test_large_three_sum_enumeration(self):
        stdin = "3000\n" + " ".join(map(str, range(-1500, 1500))) + "\n"
        output = io.StringIO(self.run_reference(15, stdin))
        # For each a, count b with a < b < -a-b <= 1499 independently.
        expected_count = sum(max(0, (-a - 1) // 2 - max(a + 1, -a - 1499) + 1)
                             for a in range(-1500, 0))
        self.assertEqual(int(output.readline()), expected_count)
        # A bitset of b values for each a checks uniqueness without retaining
        # more than a million tuples alongside the approximately 15 MB output.
        seen, count = {}, 0
        for line in output:
            a, b, c = sorted(map(int, line.split()))
            self.assertTrue(-1500 <= a < b < c <= 1499)
            self.assertEqual(a + b + c, 0)
            bit = 1 << (b + 1500)
            previous = seen.get(a, 0)
            self.assertFalse(previous & bit, "duplicate three-sum answer")
            seen[a] = previous | bit
            count += 1
        self.assertEqual(count, expected_count)


if __name__ == "__main__":
    unittest.main()
