#!/usr/bin/env python3
"""Install checksum-pinned upstream binaries without sudo (Linux x86_64)."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import shutil
import tarfile
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--with-gh', action='store_true', help='Also install GitHub CLI')
    args = parser.parse_args()
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        parser.error('Pinned binaries support Linux x86_64; install tools with your package manager on other systems.')
    dest = Path.home() / '.local/bin'
    dest.mkdir(parents=True, exist_ok=True)
    for name, entry in json.loads((ROOT / 'tools.lock.json').read_text()).items():
        if name == 'gh' and not args.with_gh:
            continue
        existing = shutil.which(name) or (str(dest / name) if (dest / name).exists() else None)
        if existing:
            print(f'Keep {name}: {existing}', flush=True)
            continue
        print(f'Download {name} {entry["version"]}', flush=True)
        req = urllib.request.Request(entry['url'], headers={'User-Agent': 'violet-afterdark-setup'})
        with urllib.request.urlopen(req, timeout=120) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise RuntimeError(f'Checksum mismatch for {name}; nothing installed for this tool')
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
            members = [m for m in archive.getmembers() if m.isfile() and Path(m.name).name == name]
            if len(members) != 1:
                raise RuntimeError(f'Expected exactly one {name} executable')
            binary = archive.extractfile(members[0]).read()
        # Never extract archive paths into the filesystem.
        fd, temporary = tempfile.mkstemp(prefix=f'.{name}-', dir=dest)
        try:
            with os.fdopen(fd, 'wb') as out:
                out.write(binary)
            os.chmod(temporary, 0o755)
            os.replace(temporary, dest / name)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    print('Tools ready. Config installation is a separate step.')


if __name__ == '__main__':
    main()
