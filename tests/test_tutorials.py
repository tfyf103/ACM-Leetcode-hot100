"""Check tutorial coverage and independently challenge optimized algorithms."""
import contextlib
import io
import itertools
import json
from pathlib import Path
import random
import unittest
from unittest.mock import patch

import catalog

SOURCES = json.loads((Path(catalog.__file__).parent / 'optimal_solutions.json').read_text(encoding='utf-8'))


def program(pid):
    namespace = {'__name__': 'reference_test'}
    exec(compile(SOURCES[str(pid)], '<trusted bundled reference>', 'exec'), namespace)
    return namespace


def run(namespace, text):
    output = io.StringIO()
    with patch('sys.stdin', io.StringIO(text)), contextlib.redirect_stdout(output):
        namespace['solve']()
    return output.getvalue().strip()


class TutorialTests(unittest.TestCase):
    def test_complete_problem_specific_tutorials_match_shipped_solutions(self):
        for problem in catalog.PROBLEMS:
            with self.subTest(id=problem['id']):
                tutorial = problem['tutorial']
                self.assertTrue(tutorial['approach'])
                self.assertEqual(len(tutorial['sections']), 8)
                self.assertEqual(len({s['title'] for s in tutorial['sections']}), 8)
                self.assertGreaterEqual(sum(len(s['text']) for s in tutorial['sections']), 400)
                self.assertEqual(problem['explanation'], '\n\n'.join(s['title']+'\n'+s['text'] for s in tutorial['sections']))
                if str(problem['id']) in SOURCES:
                    self.assertEqual(problem['solution'], SOURCES[str(problem['id'])])

    def test_manacher_against_exhaustive_substrings(self):
        code = program(5)
        for size in range(1, 9):
            for chars in itertools.product('ab', repeat=size):
                text = ''.join(chars)
                answer = run(code, text+'\n')
                longest = max(len(text[i:j]) for i in range(size) for j in range(i+1, size+1)
                              if text[i:j] == text[i:j][::-1])
                self.assertIn(answer, text)
                self.assertEqual(answer, answer[::-1])
                self.assertEqual(len(answer), longest)

    def test_selection_on_adversarial_orders_and_duplicates(self):
        select = program(215)['select']
        rng = random.Random(215)
        for values in (list(range(100000)), list(range(99999, -1, -1)), [7]*100000,
                       [rng.randrange(-100, 101) for _ in range(10000)]):
            expected = sorted(values)
            for rank in (0, len(values)//2, len(values)-1):
                self.assertEqual(select(values, rank), expected[rank])

    def test_parentheses_against_balanced_substring_enumeration(self):
        code = program(32)
        for size in range(11):
            for chars in itertools.product('()', repeat=size):
                text, longest = ''.join(chars), 0
                for start in range(size):
                    balance = 0
                    for end in range(start, size):
                        balance += 1 if text[end] == '(' else -1
                        if balance < 0:
                            break
                        if balance == 0:
                            longest = max(longest, end-start+1)
                self.assertEqual(int(run(code, text+'\n')), longest)

    def test_square_theorems_against_independent_dynamic_programming(self):
        code = program(279)
        dp = [0]+[10000]*1000
        squares = [i*i for i in range(1, 32)]
        for value in range(1, 1001):
            dp[value] = 1+min(dp[value-square] for square in squares if square <= value)
            self.assertEqual(int(run(code, str(value)+'\n')), dp[value])

    def test_fast_doubling_matches_simple_recurrence(self):
        code = program(70)
        previous, current = 1, 1
        for n in range(1, 46):
            self.assertEqual(int(run(code, str(n)+'\n')), current)
            previous, current = current, previous+current

    def test_decode_preserves_nesting_order_and_compresses_unary_groups(self):
        code = program(394)
        cases = {'3[a2[c]]': 'accaccacc', '2[ab]3[cd]ef': 'ababcdcdcdef',
                 '2[a3[b]c]': 'abbbcabbbc', '1['*1000+'a'+']'*1000: 'a',
                 '100[1[2[ab]]]': 'ab'*200, '3[]a': 'a'}
        for source, expected in cases.items():
            self.assertEqual(run(code, source+'\n'), expected)

    def test_random_list_clone_is_disjoint_and_restores_original_links(self):
        namespace = program(138)
        Node, clone = namespace['Node'], namespace['clone']
        nodes = [Node(value) for value in (7, 7, 0, -1)]
        for left, right in zip(nodes, nodes[1:]):
            left.next = right
        randoms = (2, 0, 2, None)
        for node, index in zip(nodes, randoms):
            node.random = nodes[index] if index is not None else None
        copied, current = [], clone(nodes[0])
        while current:
            copied.append(current)
            current = current.next
        self.assertEqual(len(copied), len(nodes))
        self.assertEqual([node.val for node in copied], [node.val for node in nodes])
        self.assertFalse(set(copied) & set(nodes))
        for i, node in enumerate(nodes):
            self.assertIs(node.next, nodes[i+1] if i+1<len(nodes) else None)
            self.assertIs(node.random, nodes[randoms[i]] if randoms[i] is not None else None)
            self.assertIs(copied[i].random, copied[randoms[i]] if randoms[i] is not None else None)
        self.assertIsNone(clone(None))


if __name__ == '__main__':
    unittest.main()
