import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('installer', Path(__file__).resolve().parents[1] / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallationTests(unittest.TestCase):
    def test_apply_repeat_restore_preserves_originals_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / '.bashrc'
            old.write_bytes(b'original bashrc\n')
            old.chmod(0o600)
            shared = root / 'shared'
            shared.write_bytes(b'original target\n')
            link = root / 'linked'
            link.symlink_to('shared')
            new = root / '.config/new'
            changes = [(old, b'new bashrc\n'), (new, b'new config\n'), (link, b'new linked config\n')]
            state = root / 'state'
            manifest = installer.apply(changes, state)
            self.assertIsNone(installer.apply(changes, state))
            self.assertEqual(Path((state / 'latest').read_text()), manifest)
            self.assertEqual(shared.read_bytes(), b'original target\n')
            installer.restore(manifest)
            installer.restore(manifest)  # Repeating restore is also safe.
            self.assertEqual(old.read_bytes(), b'original bashrc\n')
            self.assertEqual(old.stat().st_mode & 0o777, 0o600)
            self.assertFalse(new.exists())
            self.assertTrue(link.is_symlink())
            self.assertEqual(os.readlink(link), 'shared')

    def test_restore_refuses_later_edits_without_partial_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            a, b = root / 'a', root / 'b'
            a.write_bytes(b'old a')
            b.write_bytes(b'old b')
            manifest = installer.apply([(a, b'new a'), (b, b'new b')], root / 'state')
            b.write_bytes(b'user edits')
            with self.assertRaises(ValueError):
                installer.restore(manifest)
            self.assertEqual(a.read_bytes(), b'new a')
            self.assertEqual(b.read_bytes(), b'user edits')

    def test_terminal_merge_preserves_other_profiles_and_jsonc_strings(self):
        raw = r'''{
          // Settings with comments, trailing commas, and escaped quotes.
          "url": "https://example.com/},/*keep*/",
          "text": "quote: \" ,}",
          "defaultProfile": "powershell",
          "profiles": {"list": [
            {"guid": "ubuntu", "name": "Ubuntu", "font": {"weight": "normal"}},
            {"guid": "powershell", "name": "PowerShell", "opacity": 46},
          ]},
          "schemes": [{"name": "Unrelated"}],
        }'''
        preset = {'scheme': {'name': 'Violet Afterdark'}, 'profile': {'font': {'face': '0xProto Nerd Font Mono'}, 'opacity': 90}}
        original = installer.jsonc_loads(raw)
        merged = json.loads(installer.merge_terminal(raw, preset, 'ubuntu'))
        self.assertEqual(merged['profiles']['list'][1], original['profiles']['list'][1])
        self.assertEqual(merged['defaultProfile'], 'powershell')
        self.assertEqual(merged['url'], original['url'])
        self.assertEqual(merged['text'], original['text'])
        self.assertEqual(merged['profiles']['list'][0]['font']['weight'], 'normal')
        self.assertEqual(merged['schemes'][0], {'name': 'Unrelated'})
        repeated = json.loads(installer.merge_terminal(json.dumps(merged), preset, 'ubuntu'))
        self.assertEqual(repeated, merged)
        with self.assertRaises(ValueError):
            installer.merge_terminal(raw, preset, 'missing')


if __name__ == '__main__':
    unittest.main()
