param(
    [string]$BaseUrl = "http://127.0.0.1:9100"
)

$ErrorActionPreference = "Stop"
Write-Host "[worker-client] Stopping heartbeat and runtime through local API: $BaseUrl"
try {
    Invoke-RestMethod -Method Post -Uri "$BaseUrl/local/heartbeat/stop" | Out-Null
} catch {
    Write-Host "[worker-client] Heartbeat stop request skipped: $($_.Exception.Message)"
}
Invoke-RestMethod -Method Post -Uri "$BaseUrl/local/runtime/stop" | Out-Null
Write-Host "[worker-client] Stop request sent."
