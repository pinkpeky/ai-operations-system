param(
    [string]$Profile = "local-dev"
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Push-Location (Join-Path $repoRoot "admin_dashboard")
try {
    Write-Host "Starting Admin Dashboard for profile: $Profile"
    Write-Host "Set VITE_AI_SERVER_API / VITE_WORKSPACE_ID / VITE_USER_ID as needed."
    npm install
    npm run dev
} finally {
    Pop-Location
}

