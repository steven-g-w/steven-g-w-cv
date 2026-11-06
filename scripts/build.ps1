# Build the CV to build\cv.pdf.
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\build.ps1 [-Watch] [-Clean]
param([switch]$Watch, [switch]$Clean)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
. "$PSScriptRoot\tinytex-path.ps1"

Push-Location "$root\src"
try {
    if ($Clean) { & latexmk -C cv.tex; exit $LASTEXITCODE }
    $extra = if ($Watch) { @('-pvc', '-view=none') } else { @() }
    & latexmk @extra cv.tex
    if ($LASTEXITCODE) { throw "Build failed (see build\cv.log)" }
    Write-Host "`nBuilt: $root\build\cv.pdf"
} finally {
    Pop-Location
}
