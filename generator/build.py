"""Build the CV from cv.yaml: validate it, render LaTeX -> PDF and the HTML web page.

Usage (normally via scripts/build.ps1 or scripts/build.sh):
    python generator/build.py            # validate + PDF + site
    python generator/build.py --no-pdf   # validate + site only (no LaTeX needed)
    python generator/build.py --watch    # rebuild whenever cv.yaml, templates or the class change
    python generator/build.py --clean    # remove build/ and generated files

Outputs:
    build/cv.pdf            the PDF
    build/site/index.html   the web page (plus build/site/cv.pdf)

The phone number comes from the CV_PHONE environment variable or a local .env file;
when it is not set the CV shows "Available upon request".
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

import jinja2
from markupsafe import Markup, escape
import jsonschema
import yaml

ROOT = Path(__file__).resolve().parent.parent
CV_YAML = ROOT / "cv.yaml"
SCHEMA = ROOT / "cv.schema.json"
TEMPLATES = Path(__file__).resolve().parent / "templates"
LATEX_DIR = ROOT / "latex"
GENERATED_TEX = LATEX_DIR / "cv.tex"
BUILD = ROOT / "build"
SITE = BUILD / "site"
PHONE_PLACEHOLDER = "Available upon request"


# --------------------------------------------------------------------------- inputs

def load_env_file() -> None:
    """Load KEY=VALUE pairs from .env into os.environ (without overriding real env vars)."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_cv() -> dict:
    data = yaml.safe_load(CV_YAML.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if errors:
        lines = []
        for err in errors:
            where = "/".join(str(p) for p in err.absolute_path) or "(root)"
            lines.append(f"  cv.yaml: {where}: {err.message}")
        raise SystemExit("cv.yaml is invalid:\n" + "\n".join(lines))
    return strip_hidden(data)


def strip_hidden(node):
    """Drop every mapping marked `hidden: true`, recursively."""
    if isinstance(node, dict):
        return {k: strip_hidden(v) for k, v in node.items() if k != "hidden"}
    if isinstance(node, list):
        return [strip_hidden(x) for x in node if not (isinstance(x, dict) and x.get("hidden"))]
    return node


# --------------------------------------------------------------------------- text filters

_LATEX_ESCAPES = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}
_LATEX_RE = re.compile("|".join(re.escape(k) for k in _LATEX_ESCAPES))
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def latex(text) -> str:
    """Escape plain text for LaTeX and apply the small markup we support."""
    s = _LATEX_RE.sub(lambda m: _LATEX_ESCAPES[m.group()], str(text))
    s = _BOLD_RE.sub(r"\\textbf{\1}", s)
    s = re.sub(r"\bLaTeX\b", r"\\LaTeX{}", s)
    return s.replace("\n", r"\par ")


def html(text) -> Markup:
    s = str(escape(text))
    s = _BOLD_RE.sub(r"<strong>\1</strong>", s)
    return Markup(s.replace("\n", "<br>"))


def fa_latex(name: str) -> str:
    """Font Awesome 4 icon name (kebab-case) -> fontawesome.sty macro, e.g. mortar-board -> \\faMortarBoard."""
    return "\\fa" + "".join(part.capitalize() for part in name.split("-"))


def entry_header(entry: dict) -> str:
    return ", ".join(x for x in (entry.get("organization"), entry.get("location"), entry.get("title")) if x)


# --------------------------------------------------------------------------- rendering

def environment(**kwargs) -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        **kwargs,
    )
    env.filters.update(latex=latex, html=html, fa_latex=fa_latex)
    env.globals.update(entry_header=entry_header)
    return env


def render(cv: dict, phone: str) -> None:
    context = {"cv": cv, "basics": cv["basics"], "phone": phone, "updated": date.today()}

    # LaTeX uses ((* *)) / ((( ))) delimiters so braces in the template stay readable.
    tex_env = environment(
        block_start_string="((*", block_end_string="*))",
        variable_start_string="(((", variable_end_string=")))",
        comment_start_string="((#", comment_end_string="#))",
    )
    GENERATED_TEX.write_text(tex_env.get_template("cv.tex.j2").render(context), encoding="utf-8")

    html_env = environment(autoescape=True)
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "index.html").write_text(html_env.get_template("index.html.j2").render(context), encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")


def tex_path() -> dict:
    """PATH with TinyTeX's bin dir added, in case the shell was opened before setup."""
    env = dict(os.environ)
    home = Path.home()
    candidates = [
        Path(os.environ.get("APPDATA", "")) / "TinyTeX" / "bin" / "windows",
        Path(os.environ.get("ProgramData", "")) / "TinyTeX" / "bin" / "windows",
        home / "bin",
        home / "Library" / "TinyTeX" / "bin" / "universal-darwin",
        *sorted((home / ".TinyTeX" / "bin").glob("*")),
    ]
    extra = [str(p) for p in candidates if p.is_dir()]
    env["PATH"] = os.pathsep.join(extra + [env.get("PATH", "")])
    return env


def build_pdf() -> None:
    env = tex_path()
    latexmk = shutil.which("latexmk", path=env["PATH"])
    if not latexmk:
        raise SystemExit("latexmk not found. Run the setup script first (see README).")
    result = subprocess.run([latexmk, "cv.tex"], cwd=LATEX_DIR, env=env)
    if result.returncode:
        raise SystemExit("LaTeX build failed (see build/cv.log)")
    shutil.copy2(BUILD / "cv.pdf", SITE / "cv.pdf")


def build(pdf: bool) -> None:
    load_env_file()
    phone = os.environ.get("CV_PHONE", "").strip() or PHONE_PLACEHOLDER
    cv = load_cv()
    render(cv, phone)
    print(f"Rendered {GENERATED_TEX.relative_to(ROOT)} and {(SITE / 'index.html').relative_to(ROOT)}")
    if pdf:
        build_pdf()
        print(f"Built {(BUILD / 'cv.pdf').relative_to(ROOT)}")


def watched_files() -> list[Path]:
    files = [CV_YAML, SCHEMA, ROOT / ".env", LATEX_DIR / "documentMETADATA.cls"]
    return files + list(TEMPLATES.glob("*"))


def watch(pdf: bool) -> None:
    def snapshot():
        return {f: f.stat().st_mtime for f in watched_files() if f.exists()}

    last = None
    print("Watching cv.yaml, templates and the class file. Ctrl+C to stop.")
    while True:
        current = snapshot()
        if current != last:
            last = current
            try:
                build(pdf)
            except SystemExit as err:  # keep watching after a bad edit
                print(err, file=sys.stderr)
        time.sleep(1)


def clean() -> None:
    shutil.rmtree(BUILD, ignore_errors=True)
    GENERATED_TEX.unlink(missing_ok=True)
    print("Removed build/ and latex/cv.tex")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--watch", action="store_true", help="rebuild on changes")
    parser.add_argument("--clean", action="store_true", help="remove build output")
    parser.add_argument("--no-pdf", action="store_true", help="skip LaTeX; only validate and render the site")
    args = parser.parse_args()
    if args.clean:
        clean()
    elif args.watch:
        watch(pdf=not args.no_pdf)
    else:
        build(pdf=not args.no_pdf)


if __name__ == "__main__":
    main()
