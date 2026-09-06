"""Exercise the real installer main function without touching installed apps."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def run_install(self, existing):
        source = (ROOT / 'install.sh').read_text().removesuffix('main "$@"\n')
        source = source.replace('readonly DESTINATION_APP=', 'readonly UNUSED_DESTINATION_APP=')
        source = source.replace('readonly DESTINATION_HELPER=', 'readonly UNUSED_DESTINATION_HELPER=')
        harness = source + '''
DESTINATION_APP="$ROUTER_TEST_DIRECTORY/app"
DESTINATION_HELPER="$ROUTER_TEST_DIRECTORY/helper"
require_prerequisites() { :; }
resolve_source_dir() { printf '%s\\n' "$PWD"; }
npm() { :; }
stop_bundle_processes() { printf 'stopped:%s\\n' "$1"; }
python3() { printf 'patch-arg:%s\\n' "$@"; }
open() { :; }
main
'''
        with tempfile.TemporaryDirectory() as directory:
            if existing:
                (Path(directory) / 'app').mkdir()
                (Path(directory) / 'helper').mkdir()
            result = subprocess.run(['/bin/bash'], input=harness, text=True, capture_output=True,
                env=dict(os.environ, ROUTER_TEST_DIRECTORY=directory))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('patch-arg:scripts/patch_app.py', result.stdout)
        return result.stdout

    def test_fresh_install_with_macos_bash(self):
        output = self.run_install(False)
        self.assertNotIn('patch-arg:--force', output)
        self.assertNotIn('stopped:', output)

    def test_existing_install_keeps_force_backup_path(self):
        output = self.run_install(True)
        self.assertIn('patch-arg:--force', output)
        self.assertEqual(output.count('stopped:'), 2)
