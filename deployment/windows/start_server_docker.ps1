param(
    [string]$Profile = "server-docker",
    [switch]$Build
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Push-Location $repoRoot
try {
    Write-Host "Starting server Docker profile: $Profile"
    if ($Build) {
        docker compose up --build -d
    } else {
        docker compose up -d
    }
    Write-Host "Next: python deployment/scripts/verify_environment.py --profile $Profile"
} finally {
    Pop-Location
}

