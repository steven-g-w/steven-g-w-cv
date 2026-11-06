# One-time setup on Windows: installs TinyTeX (a small TeX Live) and the packages the CV needs.
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
. "$PSScriptRoot\tinytex-path.ps1"

if (-not (Get-Command lualatex -ErrorAction SilentlyContinue)) {
    Write-Host '==> Installing TinyTeX (user-level, no admin needed)...'
    $installer = Join-Path $env:TEMP 'install-tinytex.ps1'
    Invoke-WebRequest 'https://tinytex.yihui.org/install-bin-windows.ps1' -OutFile $installer -UseBasicParsing
    & powershell -NoProfile -ExecutionPolicy Bypass -File $installer
    if ($LASTEXITCODE) { throw 'TinyTeX install failed' }
    Remove-Item $installer -ErrorAction SilentlyContinue
    . "$PSScriptRoot\tinytex-path.ps1"
} else {
    Write-Host "==> Found lualatex: $((Get-Command lualatex).Source)"
}

$packages = Get-Content "$root\tex-packages.txt" | ForEach-Object { $_.Trim() } | Where-Object { $_ -and -not $_.StartsWith('#') }
if (Get-Command tlmgr -ErrorAction SilentlyContinue) {
    # tlmgr refuses to install anything while it is out of date (and still exits 0), so update it first.
    Write-Host '==> Updating tlmgr...'
    & tlmgr update --self
    Write-Host '==> Installing TeX packages...'
    & tlmgr install @packages
    if ($LASTEXITCODE) { throw 'tlmgr install failed' }
    $installed = & tlmgr info --only-installed --data name
    $missing = $packages | Where-Object { $installed -notcontains $_ }
    if ($missing) { throw "TeX packages not installed: $($missing -join ', ')" }
} else {
    Write-Host '==> tlmgr not found (MiKTeX?). Packages will be installed on demand.'
}

Write-Host "`nSetup complete. Build with:  powershell -ExecutionPolicy Bypass -File scripts\build.ps1"
