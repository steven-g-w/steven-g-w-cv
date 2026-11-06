# Build the CV from cv.yaml: build\cv.pdf and the web page in build\site\.
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\build.ps1 [-Watch] [-Clean] [-NoPdf]
param([switch]$Watch, [switch]$Clean, [switch]$NoPdf)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$python = "$root\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw 'No .venv found. Run scripts\setup.ps1 first.' }

$opts = @()
if ($Watch) { $opts += '--watch' }
if ($Clean) { $opts += '--clean' }
if ($NoPdf) { $opts += '--no-pdf' }
& $python "$root\generator\build.py" @opts
exit $LASTEXITCODE
