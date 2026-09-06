import hashlib
import plistlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import patch_app


class AsarIntegrityTests(unittest.TestCase):
    def test_info_plist_hashes_header_not_whole_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.mkdir()
            (source / 'index.js').write_text('console.log("fixture");')
            archive = root / 'app.asar'
            subprocess.run(['node', '--input-type=module', '-e',
                'import {createPackage} from "@electron/asar"; await createPackage(process.argv[1],process.argv[2]);',
                str(source), str(archive)], cwd=patch_app.PROJECT_ROOT, check=True)
            app = root / 'Fixture.app'
            (app / 'Contents').mkdir(parents=True)
            info = app / 'Contents/Info.plist'
            info.write_bytes(plistlib.dumps({}))
            patch_app.patch_info_plist(app, archive, 'TEAM123456')
            actual = plistlib.loads(info.read_bytes())['ElectronAsarIntegrity']['Resources/app.asar']['hash']
            data = archive.read_bytes()
            header = data[16:16+int.from_bytes(data[12:16], 'little')]
            self.assertEqual(actual, hashlib.sha256(header).hexdigest())
            self.assertNotEqual(actual, hashlib.sha256(data).hexdigest())
