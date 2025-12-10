#!/usr/bin/env bash
# Check licenses of dependencies for compliance
# Fails if any non-approved license is found

set -euo pipefail

echo "Checking dependency licenses..."

# Install pip-licenses if not available
if ! command -v pip-licenses &> /dev/null; then
    echo "Installing pip-licenses..."
    pip install pip-licenses==5.0.0
fi

# Approved licenses (permissive open source)
APPROVED_LICENSES=(
    "MIT"
    "Apache-2.0"
    "Apache Software License"
    "BSD"
    "BSD-3-Clause"
    "BSD-2-Clause"
    "ISC"
    "Python Software Foundation"
    "PSF"
    "Mozilla Public License 2.0 (MPL 2.0)"
)

# Generate license report
pip-licenses --format=json --with-urls --with-description > licenses.json

# Check for non-approved licenses
echo "Scanning for non-approved licenses..."

# Parse JSON and check licenses
non_approved=$(python3 <<EOF
import json
import sys

approved = set([
    "MIT License",
    "MIT",
    "Apache Software License",
    "Apache 2.0",
    "Apache-2.0",
    "BSD License",
    "BSD",
    "BSD-3-Clause",
    "BSD-2-Clause",
    "ISC License",
    "ISC",
    "Python Software Foundation License",
    "PSF",
    "Mozilla Public License 2.0 (MPL 2.0)",
    "MPL-2.0",
])

with open("licenses.json") as f:
    licenses = json.load(f)

non_approved = []
for pkg in licenses:
    lic = pkg.get("License", "UNKNOWN")
    if lic not in approved and "UNKNOWN" not in lic:
        # Check if it's a variant of approved license
        lic_lower = lic.lower()
        is_approved = any(
            app.lower() in lic_lower
            for app in approved
        )
        if not is_approved:
            non_approved.append({
                "name": pkg["Name"],
                "version": pkg["Version"],
                "license": lic,
                "url": pkg.get("URL", "N/A")
            })

if non_approved:
    print("❌ Non-approved licenses found:")
    for pkg in non_approved:
        print(f"  - {pkg['name']} {pkg['version']}: {pkg['license']}")
        print(f"    URL: {pkg['url']}")
    sys.exit(1)
else:
    print("✅ All licenses approved")
    sys.exit(0)
EOF
)

rm -f licenses.json

echo "License check complete!"
