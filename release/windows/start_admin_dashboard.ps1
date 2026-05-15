$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Push-Location (Join-Path $repoRoot "admin_dashboard")
try {
    npm install
    npm run dev
} finally {
    Pop-Location
}

