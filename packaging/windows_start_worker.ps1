param(
    [string]$ConfigPath = "worker_client\worker_config.yaml",
    [switch]$ForceRegister
)

$ErrorActionPreference = "Stop"
Write-Host "[worker-client] Starting local runtime and heartbeat with config: $ConfigPath"
if ($ForceRegister) {
    python -m worker_client.cli --config $ConfigPath start --force-register
} else {
    python -m worker_client.cli --config $ConfigPath start
}
