# Steven Wang CV

The CV for Steven Wang. The content lives in one file, [cv.yaml](cv.yaml), and is rendered to:

- **PDF** through LaTeX
- **Web page** published with GitHub Pages: <https://steven-g-w.github.io/steven-g-w-cv/> (with the PDF at [`/cv.pdf`](https://steven-g-w.github.io/steven-g-w-cv/cv.pdf))

Every push validates `cv.yaml` and builds both in GitHub Actions. Pushes to `main` also deploy the site.

## Setup (once)

Installs [TinyTeX](https://yihui.org/tinytex/) (a small TeX Live, user-level, no admin), the TeX packages in [tex-packages.txt](tex-packages.txt), and a Python venv (`.venv`) with the generator's dependencies. Needs Python 3.10+.

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```

macOS / Linux:

```bash
sh scripts/setup.sh
```

If you already have TeX Live or MiKTeX with `lualatex`, setup skips the TinyTeX install and only adds missing packages.

## Build

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build.ps1
```

```bash
sh scripts/build.sh
```

Outputs `build/cv.pdf` and the web page in `build/site/`. Options: `-Watch` / `--watch` rebuilds whenever `cv.yaml` changes, `-NoPdf` / `--no-pdf` skips LaTeX, and `-Clean` / `--clean` wipes the output.

## Private details: `.env`

Your phone number is never committed. Put it in `.env`, which setup creates from [.env.example](.env.example) and git ignores:

```
CV_PHONE=+61 4xx xxx xxx
```

Local builds include it. Builds without it, including CI and the public web page, show "Available upon request".

## Editing in VS Code

1. Open the folder and install the recommended extensions: **YAML** (validates `cv.yaml` against [cv.schema.json](cv.schema.json) with autocomplete) and **vscode-pdf**.
2. Run **Terminal → Run Task → CV: watch** and edit `cv.yaml`. Each save rebuilds the PDF and page; open `build/cv.pdf` in a side tab.

In `cv.yaml`: use `**bold**` for emphasis. Set `hidden: true` to hide a section or entry, or comment out a line to hide one bullet.

## Layout

| Path | What |
| --- | --- |
| `cv.yaml` | **All CV content.** The only file you normally edit |
| `cv.schema.json` | Schema for `cv.yaml`, used by VS Code and the build |
| `generator/build.py` | Validates `cv.yaml`, renders the templates, runs LaTeX |
| `generator/templates/` | `cv.tex.j2` (PDF) and `index.html.j2` (web page) |
| `latex/` | Class file (layout, colours, macros), bundled Source Sans Pro fonts, latexmk config |
| `.github/workflows/build.yml` | CI: setup, build, upload the PDF, deploy Pages from `main` |

## Credits

Template: [YAAC: Another Awesome CV](https://github.com/darwiin/yaac-another-awesome-cv) by Christophe Roger (LPPL 1.3c), adapted by Sabrina Benge (CC BY-SA 4.0).
Font: Source Sans Pro by Adobe (SIL OFL).
