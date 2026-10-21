#!/bin/bash
# 作業中の docs を別の場所にコピーして、そこでビルドする（作業を続けながら確かめるため）。
# 使い方: tools/stl/snapbuild.sh [--strict]
# 結果: $TEMP/kdocs_snap/build.log （最後の行に EXIT n）
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SNAP="${TEMP:-/tmp}/kdocs_snap"
rm -rf "$SNAP"
mkdir -p "$SNAP"
cp -r "$ROOT/docs" "$ROOT/hooks" "$ROOT/mkdocs.yml" "$ROOT/autolinks.yml" "$ROOT/glossary.yml" "$ROOT/ratings.yml" "$SNAP/" 2>/dev/null
cd "$SNAP"
MK="$TEMP/kvenv/Scripts/mkdocs.exe"
if [ "${1:-}" = "--strict" ]; then
  "$MK" build --strict -q -d "$SNAP/site" > "$SNAP/build.log" 2>&1
else
  "$MK" build -q -d "$SNAP/site" > "$SNAP/build.log" 2>&1
fi
echo "EXIT $?" >> "$SNAP/build.log"
