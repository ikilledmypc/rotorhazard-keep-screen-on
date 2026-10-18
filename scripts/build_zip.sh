#!/usr/bin/env bash
# Builds dist/keep_screen_on.zip, ready to unzip into ~/rh-data/plugins/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOMAIN="keep_screen_on"
SRC="$ROOT/custom_plugins/$DOMAIN"
OUT="$ROOT/dist/$DOMAIN.zip"

VERSION="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['version'])" "$SRC/manifest.json")"

mkdir -p "$ROOT/dist"
rm -f "$OUT"
cd "$ROOT/custom_plugins"
zip -r -q -X "$OUT" "$DOMAIN" -x '*/__pycache__/*' '*.pyc' '*/.DS_Store'

echo "Built $OUT (version $VERSION)"
unzip -l "$OUT"
