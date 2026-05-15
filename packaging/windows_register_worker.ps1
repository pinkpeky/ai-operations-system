param(
    [string]$ConfigPath = "worker_client\worker_config.yaml",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
Write-Host "[worker-client] Registering worker with config: $ConfigPath"
if ($Force) {
    python -m worker_client.cli --config $ConfigPath register --force
} else {
    python -m worker_client.cli --config $ConfigPath register
}
