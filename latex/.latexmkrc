# latexmk config — used by scripts/build.*, VS Code (LaTeX Workshop) and CI.
# Run latexmk from this directory (src/) so the font path "fonts/" resolves.
$pdf_mode = 4;   # 4 = LuaLaTeX (same engine as the Overleaf project)
$lualatex = 'lualatex -interaction=nonstopmode -halt-on-error -file-line-error -synctex=1 %O %S';
$out_dir  = '../build';
