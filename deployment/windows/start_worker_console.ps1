param(
    [string]$Profile = "client-worker"
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Push-Location (Join-Path $repoRoot "worker_console")
try {
    Write-Host "Starting Worker Console for profile: $Profile"
    Write-Host "This UI talks to local worker API at VITE_LOCAL_WORKER_API."
    npm install
    npm run dev
} finally {
    Pop-Location
}

