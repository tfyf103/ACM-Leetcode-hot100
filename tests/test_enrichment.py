"""Guard the enhanced catalog contract and fixed fixture integrity."""
import copy
import json
from pathlib import Path
import unittest

import catalog
from catalog.enrichment import apply_enrichment


class EnrichmentTests(unittest.TestCase):
    def test_all_problems_have_rules_examples_and_diverse_inputs(self):
        for problem in catalog.PROBLEMS:
            with self.subTest(problem_id=problem['id']):
                minimum = {22: 8, 51: 9}.get(problem['id'], 20)
                self.assertGreaterEqual(len({c['input'] for c in problem['tests']}), minimum)
                self.assertGreaterEqual(len(problem['examples']), 3)
                self.assertGreaterEqual(len(problem['clarifications']), 3)
                self.assertNotIn('按题目要求读取输入，输出上述结果', str(problem['examples']))
                self.assertIn('\n\n', problem['description'])

    def test_finite_parameter_domains_are_complete(self):
        for problem_id, maximum in ((22, 8), (51, 9)):
            values = {int(case['input']) for case in catalog.BY_ID[problem_id]['tests']}
            self.assertEqual(values, set(range(1, maximum + 1)))

    def test_loading_twice_does_not_duplicate_tests(self):
        copied = copy.deepcopy(catalog.PROBLEMS)
        apply_enrichment(copied)
        self.assertEqual(copied, catalog.PROBLEMS)

    def test_public_problem_exposes_rules_but_keeps_tests_private(self):
        problem = catalog.public_problem(catalog.BY_ID[1])
        self.assertEqual(problem['clarifications'], catalog.BY_ID[1]['clarifications'])
        self.assertNotIn('tests', problem)
        self.assertNotIn('solution', problem)

    def test_fixed_extra_cases_have_no_conflicting_expectations(self):
        entries = json.loads((Path(catalog.__file__).parent / 'enrichment.json').read_text(encoding='utf-8'))
        self.assertEqual(len(entries), 100)
        for problem in catalog.PROBLEMS:
            seen = {}
            for case in problem['tests']:
                if case['input'] in seen:
                    self.assertEqual(seen[case['input']], case['output'])
                seen[case['input']] = case['output']
            self.assertTrue(entries[str(problem['id'])]['tests'])


if __name__ == '__main__':
    unittest.main()
