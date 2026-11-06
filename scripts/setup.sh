#!/usr/bin/env sh
# One-time setup on macOS/Linux: installs TinyTeX (a small TeX Live) and the packages the CV needs.
# Usage:  ./scripts/setup.sh
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/bin:$HOME/.TinyTeX/bin/x86_64-linux:$HOME/.TinyTeX/bin/aarch64-linux:$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"

if ! command -v lualatex >/dev/null 2>&1; then
  echo "==> Installing TinyTeX (user-level, no sudo needed)..."
  curl -fsSL https://tinytex.yihui.org/install-bin-unix.sh | sh
else
  echo "==> Found lualatex: $(command -v lualatex)"
fi

packages="$(grep -v '^[[:space:]]*#' "$root/tex-packages.txt" | tr -d '\r' | xargs)"

# tlmgr refuses to install anything while it is out of date (and may still exit 0), so update it first.
echo "==> Updating tlmgr..."
tlmgr update --self

echo "==> Installing TeX packages..."
# shellcheck disable=SC2086
tlmgr install $packages

installed="$(tlmgr info --only-installed --data name)"
missing=""
for p in $packages; do
  echo "$installed" | grep -qx "$p" || missing="$missing $p"
done
if [ -n "$missing" ]; then
  echo "TeX packages not installed:$missing" >&2
  exit 1
fi

echo "==> Setting up Python environment (.venv)..."
command -v python3 >/dev/null 2>&1 || { echo "python3 (3.10+) not found; install it and re-run." >&2; exit 1; }
[ -x "$root/.venv/bin/python" ] || python3 -m venv "$root/.venv"
"$root/.venv/bin/python" -m pip install --quiet --disable-pip-version-check -r "$root/requirements.txt"

if [ ! -f "$root/.env" ] && [ -z "${CI:-}" ]; then
  cp "$root/.env.example" "$root/.env"
  echo "==> Created .env: put your real phone number in it (it is git-ignored)."
fi

echo
echo "Setup complete. Build with:  ./scripts/build.sh"
