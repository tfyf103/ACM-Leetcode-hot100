"""Exercise the actual Windows launcher without starting a long-running server."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == "nt", "Windows launcher")
class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hot100-launcher-")
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / "中文 path with spaces"
        self.project.mkdir()
        for name in ("start.bat", "start.ps1"):
            shutil.copyfile(ROOT / name, self.project / name)
        (self.project / "app.py").write_text(
            "import json, os, sys\n"
            "print(json.dumps({'argv': sys.argv[1:], 'cwd': os.getcwd(), "
            "'executable': sys.executable}))\n", encoding="utf-8")
        self.environment = dict(os.environ, ACM_PYTHON=sys.executable,
                                ACM_NO_PAUSE="1", PYTHONIOENCODING="utf-8")

    def launch(self, *arguments):
        return subprocess.run(
            [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", "start.bat", *arguments],
            cwd=self.project, env=self.environment, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
            timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)

    def test_explicit_python_and_diagnostic_mode(self):
        result = self.launch("--check")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn(sys.executable, result.stdout)
        self.assertNotIn('"argv"', result.stdout)

    def test_arguments_and_project_directory(self):
        result = self.launch("--port", "8766", "--data-dir", "progress with spaces", "--no-browser")
        self.assertEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(payload["argv"], ["--port", "8766", "--data-dir", "progress with spaces", "--no-browser"])
        self.assertEqual(Path(payload["cwd"]), self.project)
        self.assertEqual(Path(payload["executable"]), Path(sys.executable))

    def test_config_file_without_python_on_path(self):
        self.environment.pop("ACM_PYTHON")
        self.environment["PATH"] = os.path.join(os.environ["SystemRoot"], "System32")
        (self.project / "python-path.txt").write_text(sys.executable + "\n", encoding="utf-8")
        result = self.launch("--check")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn(sys.executable, result.stdout)

    def test_invalid_override_does_not_silently_fall_back(self):
        self.environment["ACM_PYTHON"] = str(self.project / "missing" / "python.exe")
        result = self.launch("--check")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Invalid Python override", result.stdout)

    def test_application_exit_status_is_preserved(self):
        (self.project / "app.py").write_text("raise SystemExit(7)\n", encoding="utf-8")
        result = self.launch()
        self.assertEqual(result.returncode, 7, result.stdout)


if __name__ == "__main__":
    unittest.main()
