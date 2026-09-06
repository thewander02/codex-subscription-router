import sys
import plistlib
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import patch_app


class SigningTests(unittest.TestCase):
    def test_apple_development_person_id_is_not_team_id(self):
        with patch.object(patch_app, 'run'), patch.object(patch_app, 'signed_code_metadata', return_value=('true', 'TEAM123456')):
            self.assertEqual(patch_app.signing_team_identifier('Apple Development: Example (PERSON1234)'), 'TEAM123456')

    def test_adhoc_has_no_team(self):
        self.assertIsNone(patch_app.signing_team_identifier('-'))

    def test_removes_vendor_push_entitlement_preserving_runtime(self):
        payload = plistlib.dumps({'com.apple.developer.aps-environment':'production', 'com.apple.security.cs.allow-jit':True})
        result = subprocess.CompletedProcess([], 0, stdout=payload, stderr=b'')
        with patch.object(patch_app.subprocess, 'run', return_value=result):
            self.assertEqual(patch_app.sanitized_runtime_entitlements(Path('fixture')), {'com.apple.security.cs.allow-jit':True})
