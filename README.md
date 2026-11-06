# Steven Wang CV

The CV for Steven Wang, written in LaTeX (LuaLaTeX, same as the original Overleaf project).
Every push builds the PDF in GitHub Actions; download it from the run's **cv-pdf** artifact.

## Setup (once)

Installs [TinyTeX](https://yihui.org/tinytex/) (a small TeX Live distribution, user-level, no admin) plus the packages in [tex-packages.txt](tex-packages.txt).

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

Output: `build/cv.pdf`. Add `-Watch` / `--watch` to rebuild on every change, `-Clean` / `--clean` to wipe intermediates.

## Editing in VS Code

1. Open the folder and install the recommended **LaTeX Workshop** extension.
2. Restart VS Code after the first setup so it sees TinyTeX on `PATH`.
3. Edit anything under `src/` and save — the PDF rebuilds and opens in a side tab (`Ctrl+Alt+V`). Ctrl+click in the PDF jumps to the source.

Tasks are also available via **Terminal → Run Task** (`CV: setup`, `CV: build PDF`, `CV: watch`).

## Layout

| Path | What |
| --- | --- |
| `src/cv.tex` | Main file: header, contact info, which sections are included |
| `src/sections/` | One file per section — comment `\input` lines in `cv.tex` to hide a section |
| `src/documentMETADATA.cls` | Template class (YAAC: Another Awesome CV) — layout, colours, macros |
| `src/fonts/` | Source Sans Pro (bundled so builds look the same everywhere) |
| `src/.latexmkrc` | Build config shared by scripts, VS Code and CI |
| `.github/workflows/build.yml` | CI: runs the same setup + build scripts, uploads the PDF |

## Credits

Template: [YAAC: Another Awesome CV](https://github.com/darwiin/yaac-another-awesome-cv) by Christophe Roger (LPPL 1.3c), adapted by Sabrina Benge (CC BY-SA 4.0).
Font: Source Sans Pro by Adobe (SIL OFL).
