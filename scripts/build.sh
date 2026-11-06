#!/usr/bin/env sh
# Build the CV to build/cv.pdf.
# Usage:  ./scripts/build.sh [--watch|--clean]
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/bin:$HOME/.TinyTeX/bin/x86_64-linux:$HOME/.TinyTeX/bin/aarch64-linux:$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"

cd "$root/src"
case "${1:-}" in
  --clean) exec latexmk -C cv.tex ;;
  --watch) exec latexmk -pvc -view=none cv.tex ;;
  *)       latexmk cv.tex ;;
esac
echo
echo "Built: $root/build/cv.pdf"
