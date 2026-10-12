"""Exercise Windows interpreter discovery and argument forwarding without a server."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


@unittest.skipUnless(os.name == "nt", "Windows launcher")
class WindowsLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="acm-launcher-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "中文 project (offline)"
        (self.root / "tools").mkdir(parents=True)
        source = Path(__file__).resolve().parents[1]
        shutil.copyfile(source / "tools/start_windows.ps1", self.root / "tools/start_windows.ps1")
        shutil.copyfile(source / "start.bat", self.root / "start.bat")
        shutil.copyfile(source / "start.ps1", self.root / "start.ps1")
        self.profile = Path(self.temp.name) / "profile"
        (self.profile / ".conda").mkdir(parents=True)
        self.env = dict(os.environ)
        self.env.pop("ACM_PYTHON", None)
        self.env.pop("CONDA_PREFIX", None)
        self.env["USERPROFILE"] = str(self.profile)
        self.env["PATH"] = os.pathsep.join([
            str(Path(os.environ["SystemRoot"]) / "System32"),
            str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0"),
        ])
        self.powershell = str(Path(os.environ["SystemRoot"]) /
                              "System32/WindowsPowerShell/v1.0/powershell.exe")

    def invoke(self, *arguments):
        return subprocess.run(
            [self.powershell, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(self.root / "tools/start_windows.ps1"), *arguments],
            env=self.env, cwd=self.temp.name, capture_output=True,
            text=True, errors="replace", timeout=30,
        )

    def test_conda_registration_without_python_on_path(self):
        (self.profile / ".conda/environments.txt").write_text(
            str(Path(sys.executable).parent) + "\n", encoding="utf-8")
        result = self.invoke("--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(sys.executable, result.stdout)

    def test_active_conda_environment(self):
        self.env["CONDA_PREFIX"] = str(Path(sys.executable).parent)
        result = self.invoke("--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(sys.executable, result.stdout)

    def test_explicit_invalid_interpreter_does_not_silently_fallback(self):
        self.env["ACM_PYTHON"] = str(self.root / "missing python.exe")
        result = self.invoke("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("No working Python 3.9+", result.stdout)

    def test_arguments_project_directory_and_exit_code(self):
        self.env["ACM_PYTHON"] = sys.executable
        destination = self.root / "arguments.json"
        (self.root / "app.py").write_text(
            "import json, os, pathlib, sys\n"
            "pathlib.Path('arguments.json').write_text(json.dumps({'argv': sys.argv[1:], "
            "'cwd': os.getcwd(), 'python': sys.executable}), encoding='utf-8')\n"
            "sys.exit(7)\n", encoding="utf-8")
        result = self.invoke("--port", "8766", "--data-dir", "my progress", "--no-browser")
        self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
        saved = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(saved["argv"], ["--port", "8766", "--data-dir", "my progress", "--no-browser"])
        self.assertEqual(saved["cwd"], str(self.root))
        self.assertEqual(saved["python"], sys.executable)

    def test_batch_entrypoint_from_unicode_directory(self):
        self.env["ACM_PYTHON"] = sys.executable
        result = subprocess.run(
            [os.environ["COMSPEC"], "/d", "/c", "start.bat", "--check"],
            env=self.env, cwd=self.root, capture_output=True,
            text=True, errors="replace", timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(sys.executable, result.stdout)


if __name__ == "__main__":
    unittest.main()
