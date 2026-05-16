param(
    [switch]$Build
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Push-Location $repoRoot
try {
    if ($Build) {
        docker compose up --build -d
    } else {
        docker compose up -d
    }
    Write-Host "AI Server started via docker compose. This is a release foundation helper, not production HA orchestration."
} finally {
    Pop-Location
}

