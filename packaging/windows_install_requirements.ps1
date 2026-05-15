param(
    [string]$ConfigPath = "worker_client\worker_config.yaml"
)

$ErrorActionPreference = "Stop"
Write-Host "[worker-client] Installing Python requirements..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Write-Host "[worker-client] Requirements installed. Config path: $ConfigPath"
