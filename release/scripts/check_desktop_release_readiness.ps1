$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$desktopRoot = Join-Path $repoRoot "worker_console_desktop"
$tauriConfig = Join-Path $desktopRoot "src-tauri\tauri.conf.json"
$icon = Join-Path $desktopRoot "src-tauri\icons\icon.ico"
$packageJson = Join-Path $desktopRoot "package.json"

Write-Host "Checking Worker Console Desktop release readiness"
foreach ($path in @($tauriConfig, $icon, $packageJson)) {
    if (-not (Test-Path $path)) {
        throw "Missing desktop readiness file: $path"
    }
}

$iconInfo = Get-Item $icon
if ($iconInfo.Length -le 0) {
    throw "Desktop icon is empty: $icon"
}

$config = Get-Content $tauriConfig -Raw | ConvertFrom-Json
if (-not ($config.bundle.icon -contains "icons/icon.ico")) {
    throw "tauri.conf.json bundle.icon must include icons/icon.ico"
}

$cargo = Get-Command cargo -ErrorAction SilentlyContinue
if (-not $cargo) {
    Write-Warning "cargo not found. Native Tauri release build is pending until Rust/MSVC or platform toolchain is installed."
} else {
    Write-Host "cargo found at $($cargo.Source)"
}

Write-Host "Desktop release readiness checks complete. This does not sign or package an installer."

