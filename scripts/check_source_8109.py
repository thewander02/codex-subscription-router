#!/usr/bin/env python3
"""Validate the build-8109 patch against a local ASAR extraction, without signing.

Usage: python3 scripts/check_source_8109.py /path/to/extracted-asar
Only disposable copies are patched. No official binaries are included in tests.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from renderer_8109 import patch_renderer_8109
from patch_app import patch_desktop_profile


def main():
    source = Path(sys.argv[1])
    with tempfile.TemporaryDirectory(prefix='router-8109-test-') as directory:
        root = Path(directory)
        shutil.copytree(source / 'webview', root / 'webview')
        shutil.copytree(source / '.vite', root / '.vite')
        patch_desktop_profile(root, root / 'Computer Use.app')
        patch_renderer_8109(root, '0' * 64)
        for file in (root / 'webview/assets').glob('*.js'):
            if 'CodexMux' in file.read_text():
                subprocess.run(['node', '--check', str(file)], check=True, capture_output=True)
        for file in (root / '.vite/build').glob('*.js'):
            if file.name.startswith(('bootstrap-', 'main-')):
                subprocess.run(['node', '--check', str(file)], check=True, capture_output=True)
    print('8109 desktop and renderer patches: PASS')


if __name__ == '__main__':
    main()
