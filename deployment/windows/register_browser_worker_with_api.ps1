param(
    [string]$RepoRoot = "D:\ai-operations-system",
    [string]$ApiBaseUrl = "http://127.0.0.1:8000",
    [string]$WorkspaceId = "",
    [string]$WorkerName = "local-browser-worker",
    [string]$WorkerBaseUrl = "http://127.0.0.1:9100",
    [string]$EnvPath = "",
    [string]$StatePath = ""
)

$ErrorActionPreference = "Stop"

function Read-DotEnvValue {
    param([string]$Path, [string]$Key)
    if (!(Test-Path $Path)) {
        return $null
    }
    $line = Get-Content -LiteralPath $Path | Where-Object { $_ -match "^$([regex]::Escape($Key))=" } | Select-Object -Last 1
    if (!$line) {
        return $null
    }
    return $line.Substring($Key.Length + 1).Trim().Trim('"').Trim("'")
}

if (!$EnvPath) {
    $EnvPath = Join-Path $RepoRoot ".env"
}
if (!$StatePath) {
    $StatePath = Join-Path $RepoRoot "worker_client\worker_state.json"
}

if (!$WorkspaceId) {
    $WorkspaceId = Read-DotEnvValue -Path $EnvPath -Key "BROWSER_WORKER_WORKSPACE_ID"
}

if (!$WorkspaceId) {
    throw "WorkspaceId is required. Pass -WorkspaceId or set BROWSER_WORKER_WORKSPACE_ID in .env."
}

$allowedDomainsRaw = Read-DotEnvValue -Path $EnvPath -Key "BROWSER_ALLOWED_DOMAINS"
if ($allowedDomainsRaw) {
    $allowedDomains = $allowedDomainsRaw.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
} else {
    $allowedDomains = @("localhost", "127.0.0.1")
}

$health = Invoke-RestMethod -Uri "$WorkerBaseUrl/health" -TimeoutSec 10
if ($health.success -ne $true -or $health.capabilities.browser_runtime -ne $true) {
    throw "Browser Worker is not healthy at $WorkerBaseUrl"
}

$body = @{
    worker_name = $WorkerName
    worker_type = "playwright"
    base_url = $WorkerBaseUrl
    capabilities = @{
        browser = "chromium"
        browser_runtime = $true
        screenshot = $true
        page_content = $true
        click = $true
        type_text = $true
        scroll = $true
        persistent_profile = $true
    }
    metadata = @{
        runtime = "windows-single-server"
        managed_by = "deployment/windows/register_browser_worker_with_api.ps1"
    }
    max_sessions = 5
    max_actions_per_minute = 60
    priority = 100
    allowed_domains = @($allowedDomains)
    generate_secret = $true
} | ConvertTo-Json -Depth 8

$headers = @{ "X-Workspace-Id" = $WorkspaceId }
$registered = Invoke-RestMethod `
    -Uri "$ApiBaseUrl/api/v1/browser-workers/register" `
    -Method Post `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $body `
    -TimeoutSec 30

if (!$registered.worker_secret) {
    throw "API did not return worker_secret. Local worker_state.json was not written."
}

$stateDir = Split-Path -Parent $StatePath
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
$state = @{
    worker_id = "$($registered.id)"
    worker_secret = "$($registered.worker_secret)"
    server_url = $ApiBaseUrl.TrimEnd("/")
    worker_name = "$($registered.worker_name)"
    workspace_id = "$($registered.workspace_id)"
    worker_base_url = "$($registered.base_url)"
    registered_at = [DateTimeOffset]::UtcNow.ToString("o")
} | ConvertTo-Json -Depth 8
Set-Content -LiteralPath $StatePath -Value $state -Encoding UTF8

Write-Host "[OK] Registered Browser Worker"
Write-Host "workspace_id=$($registered.workspace_id)"
Write-Host "worker_id=$($registered.id)"
Write-Host "worker_name=$($registered.worker_name)"
Write-Host "base_url=$($registered.base_url)"
Write-Host "status=$($registered.status)"
Write-Host "state_path=$StatePath"
