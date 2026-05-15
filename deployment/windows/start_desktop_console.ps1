param(
    [string]$Profile = "desktop-client"
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Push-Location (Join-Path $repoRoot "worker_console_desktop")
try {
    Write-Host "Starting Worker Console Desktop for profile: $Profile"
    Write-Host "This controls only the worker runtime on this local machine."
    npm install
    npm run tauri dev
} finally {
    Pop-Location
}

