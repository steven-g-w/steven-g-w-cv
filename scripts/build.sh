#!/usr/bin/env sh
# Build the CV from cv.yaml: build/cv.pdf and the web page in build/site/.
# Usage:  sh scripts/build.sh [--watch] [--clean] [--no-pdf]
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
python="$root/.venv/bin/python"
[ -x "$python" ] || { echo "No .venv found. Run scripts/setup.sh first." >&2; exit 1; }
exec "$python" "$root/generator/build.py" "$@"
