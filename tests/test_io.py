"""Regression checks for the new IO topic, strict formatting and old progress."""
import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import textwrap
import unittest

import app
import catalog
from catalog.guide_schema import validate_guides
import judge


class IOTests(unittest.TestCase):
    def test_topic_precedes_hot100_and_preserves_original_ids_and_order(self):
        self.assertEqual([p['id'] for p in catalog.PROBLEMS[:12]], list(catalog.IO_ORDER))
        self.assertEqual([p['id'] for p in catalog.PROBLEMS[12:]], list(catalog.HOT100_ORDER))
        self.assertEqual(len(catalog.BY_ID), 112)
        self.assertEqual(len({p['category'] for p in catalog.PROBLEMS}), 18)
        for index, pid in enumerate(catalog.IO_ORDER, 1):
            p = catalog.BY_ID[pid]
            self.assertEqual(p['display_id'], 'IO-%02d' % index)
            self.assertEqual(p['track'], 'acm_io')
            self.assertEqual(p['compare'], 'exact')

    def test_io_lessons_cover_every_exercise(self):
        guides = {str(pid): catalog.BY_ID[pid]['tutorial']['guide'] for pid in catalog.IO_ORDER}
        validate_guides(guides, catalog.IO_ORDER)
        self.assertEqual(len({g['recall']['mnemonic'] for g in guides.values()}), 12)
        for guide in guides.values():
            for step in guide['recall']['steps']:
                self.assertNotIn("'\n'", step, 'Show the newline marker as a visible escape')

    def test_io_memory_skeletons_have_valid_python_syntax(self):
        for pid in catalog.IO_ORDER:
            with self.subTest(problem_id=pid):
                skeleton = catalog.BY_ID[pid]['tutorial']['guide']['recall']['skeleton']
                compile('def memory_sketch():\n'+textwrap.indent(skeleton, '    '),
                        '<IO memory skeleton>', 'exec')

    def test_format_checker_accepts_line_endings_but_not_wrong_layout(self):
        self.assertTrue(judge.matches('3\r\n7\r\n', '3\n7\n', 'exact'))
        self.assertTrue(judge.matches('3\n7', '3\n7\n', 'exact'))
        for actual, expected in [('3 7\n','3\n7\n'), ('3\n7\n\n','3\n7\n'),
                                 ('1, 2\n','1,2\n'), ('1.2\n','1.20\n'),
                                 ('Case 1: 3\n','Case #1: 3\n'), ('[a]\n','[ a ]\n'),
                                 ('\n',''), ('1 \n','1\n')]:
            with self.subTest(actual=actual):
                self.assertFalse(judge.matches(actual, expected, 'exact'))
        self.assertTrue(judge.matches('3 7\n', '3\n7\n', 'tokens'))

    def run_example(self, pid, stdin, expected):
        result = judge.execute(catalog.BY_ID[pid]['solution'], stdin)
        self.assertEqual(result['status'], 'Finished', result['stderr'])
        self.assertTrue(judge.matches(result['stdout'], expected, 'exact'), repr(result['stdout']))

    def test_eof_empty_input_and_zero_length_group_are_distinct(self):
        self.run_example(10004, '', '')
        self.run_example(10006, '0\n3\n1 2\n3\n0', '0\n6\n0\n')
        self.run_example(10012, '\n \t\n2 3\n\n-2 2', '5\n0\n')

    def test_sentinel_stops_before_later_data(self):
        self.run_example(10005, '1 -1\n0 0\n99 1\n', '0\n')

    def test_text_whitespace_empty_lines_and_unicode_survive(self):
        self.run_example(10008, '3\n 你好 \n\na b\n', '4\n[ 你好 ]\n0\n[]\n3\n[a b]\n')

    def test_developer_verifier_preserves_crlf_text_records(self):
        path = Path(catalog.__file__).parents[1] / 'tools/verify_catalog.py'
        spec = importlib.util.spec_from_file_location('io_verifier', path)
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        executed, failures = verifier.verify_problem(catalog.BY_ID[10008], None, 3)
        self.assertGreaterEqual(executed, 24)
        self.assertEqual(failures, [])

    def test_exact_decimal_rounding_and_negative_zero(self):
        self.run_example(10010, '1\n2.675\n', '2.68\n')
        self.run_example(10010, '2\n-0.004 0.000\n', '0.00\n')


class IOHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='acm-io-test-')
        cls.server = app.create_server(0, cls.directory.name)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server.application.store.close()
        cls.thread.join(timeout=2)
        cls.directory.cleanup()

    def request(self, method, path, data=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=10)
        body = json.dumps(data).encode() if data is not None else None
        headers = {'Content-Type':'application/json', 'X-Local-Token':self.server.application.token}
        try:
            connection.request(method, path, body, headers)
            response = connection.getresponse()
            content = json.loads(response.read())
            self.assertEqual(response.status, 200, content)
            return content
        finally:
            connection.close()

    def test_http_lists_new_topic_first_and_exposes_the_lesson(self):
        bootstrap = self.request('GET', '/api/bootstrap')
        self.assertEqual(len(bootstrap['problems']), 112)
        self.assertEqual([p['id'] for p in bootstrap['problems'][:12]], list(catalog.IO_ORDER))
        self.assertEqual(bootstrap['problems'][0]['display_id'], 'IO-01')
        problem = self.request('GET', '/api/problems/10008')
        self.assertEqual(problem['compare'], 'exact')
        self.assertNotIn('tests', problem)
        self.assertNotIn('solution', problem)
        lesson = self.request('GET', '/api/problems/10008/solution')
        self.assertEqual(lesson['tutorial']['guide']['version'], 2)

    def test_new_progress_does_not_overwrite_legacy_hot100_progress(self):
        self.request('POST', '/api/progress', {'problem_id':1, 'code':'old draft', 'notes':'old notes'})
        self.request('POST', '/api/progress', {'problem_id':10001, 'code':'new IO draft'})
        exported = self.request('GET', '/api/export')
        self.assertEqual(exported['progress']['1']['code'], 'old draft')
        self.assertEqual(exported['progress']['1']['notes'], 'old notes')
        self.assertEqual(exported['progress']['10001']['code'], 'new IO draft')
        self.request('POST', '/api/import', exported)
        self.assertEqual(self.request('GET', '/api/bootstrap')['progress']['1']['code'], 'old draft')


if __name__ == '__main__':
    unittest.main()
