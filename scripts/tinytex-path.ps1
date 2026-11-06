# Put TinyTeX on PATH for this session if it is installed but the shell was opened before setup.
foreach ($base in @($env:APPDATA, $env:ProgramData)) {
    foreach ($arch in @('windows', 'win32')) {
        $bin = Join-Path $base "TinyTeX\bin\$arch"
        if ((Test-Path $bin) -and ($env:PATH -notlike "*$bin*")) { $env:PATH = "$bin;$env:PATH" }
    }
}
