#!/usr/bin/env bash
set -euo pipefail

# Deterministic environment
export TZ=UTC
export LC_ALL=C
export LANG=C
export PYTHONHASHSEED=0
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git log -1 --pretty=%ct || date +%s)}"
umask 0022

# Clean & build wheel/sdist (for SBOM, reproducibility)
uv pip install --system --upgrade pip build
rm -rf dist && uv run --no-project python -m build

# Make a .pyz from the installed package sources
rm -rf build/pyz && mkdir -p build/pyz/src
rsync -a --delete src/ build/pyz/src/
# Create zipapp (module entry: demo_cli.cli:main) with reproducible timestamps
uv run --no-project python -c "
import zipfile
import os
import time
from pathlib import Path

sde = int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))
date_time = time.gmtime(sde)[:6]

with zipfile.ZipFile('dist/provenance-demo.pyz', 'w', zipfile.ZIP_DEFLATED) as zf:
    # Add __main__.py with deterministic timestamp
    main_content = 'from demo_cli.cli import main\nmain()\n'
    zinfo = zipfile.ZipInfo('__main__.py', date_time=date_time)
    zinfo.external_attr = 0o644 << 16
    zf.writestr(zinfo, main_content, compress_type=zipfile.ZIP_DEFLATED)

    # Add all source files in sorted order with deterministic timestamps
    src_dir = Path('build/pyz/src')
    for file_path in sorted(src_dir.rglob('*')):
        if file_path.is_file():
            arcname = str(file_path.relative_to(src_dir))
            zinfo = zipfile.ZipInfo(arcname, date_time=date_time)
            zinfo.external_attr = 0o644 << 16
            with open(file_path, 'rb') as f:
                zf.writestr(zinfo, f.read(), compress_type=zipfile.ZIP_DEFLATED)

# Add shebang
with open('dist/provenance-demo.pyz', 'rb') as f:
    content = f.read()
with open('dist/provenance-demo.pyz', 'wb') as f:
    f.write(b'#!/usr/bin/env python3\n' + content)
"
chmod +x dist/provenance-demo.pyz

# Create build metadata with SOURCE_DATE_EPOCH for reproducibility verification
cat > dist/build-metadata.json <<EOF
{
  "SOURCE_DATE_EPOCH": "${SOURCE_DATE_EPOCH}",
  "build_timestamp": "$(date -u -d @${SOURCE_DATE_EPOCH} '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -r ${SOURCE_DATE_EPOCH} '+%Y-%m-%dT%H:%M:%SZ')",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "git_tag": "$(git describe --tags --exact-match 2>/dev/null || echo 'none')"
}
EOF
