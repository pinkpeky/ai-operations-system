param(
    [string]$Profile = "server-docker"
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Push-Location $repoRoot
try {
    python deployment/scripts/check_dependencies.py --profile $Profile
    python deployment/scripts/check_ports.py --profile $Profile
    python deployment/scripts/verify_environment.py --profile $Profile
} finally {
    Pop-Location
}

