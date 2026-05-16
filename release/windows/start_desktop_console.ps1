$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Push-Location (Join-Path $repoRoot "worker_console_desktop")
try {
    npm install
    npm run tauri dev
} finally {
    Pop-Location
}

