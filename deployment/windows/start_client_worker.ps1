param(
    [string]$Profile = "client-worker",
    [string]$Config = "worker_client/worker_config.yaml"
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Push-Location $repoRoot
try {
    if (-not (Test-Path $Config)) {
        Write-Error "Missing worker config: $Config. Copy worker_config.example.yaml first."
    }
    Write-Host "Starting client worker for profile: $Profile"
    python -m worker_client.cli --config $Config start
} finally {
    Pop-Location
}

