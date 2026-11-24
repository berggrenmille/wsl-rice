import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SHELL = Path(__file__).resolve().parents[1] / 'config/shell.bash'


class FreshShellTests(unittest.TestCase):
    def test_nvm_global_commands_available_before_lazy_initialization(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            nvm = home / '.nvm'
            (nvm / 'alias/lts').mkdir(parents=True)
            (nvm / 'nvm.sh').write_text('nvm() { :; }\n')
            for version in ['v20.9.0', 'v20.19.6', 'v22.22.3', 'v201.1.0']:
                bindir = nvm / 'versions/node' / version / 'bin'
                bindir.mkdir(parents=True)
                for command in ['node', 'codex']:
                    path = bindir / command
                    path.write_text('#!/bin/sh\nexit 0\n')
                    path.chmod(0o755)
            env = {'HOME': str(home), 'PATH': '/usr/bin:/bin', 'TERM': 'xterm-256color', 'VIOLET_GREETING': '0'}
            command = '. "$1"; command -v codex; declare -F _violet_load_nvm'
            for alias in ['20', 'v20.19', 'lts/test']:
                with self.subTest(alias=alias):
                    (nvm / 'alias/default').write_text(alias+'\n')
                    (nvm / 'alias/lts/test').write_text('v20.19.6\n')
                    result = subprocess.run(['bash', '--noprofile', '--norc', '-ic', command, 'bash', str(SHELL)], env=env, capture_output=True, text=True, check=True)
                    self.assertIn(str(nvm / 'versions/node/v20.19.6/bin/codex'), result.stdout)
                    self.assertIn('_violet_load_nvm', result.stdout)
            selected = str(nvm / 'versions/node/v22.22.3/bin')
            env['PATH'] = selected + ':/usr/bin:/bin'
            result = subprocess.run(['bash', '--noprofile', '--norc', '-ic', command, 'bash', str(SHELL)], env=env, capture_output=True, text=True, check=True)
            self.assertIn(selected+'/codex', result.stdout)


if __name__ == '__main__':
    unittest.main()
