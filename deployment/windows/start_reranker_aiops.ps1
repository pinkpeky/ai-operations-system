param(
    [string]$RepoRoot = "D:\ai-operations-system",
    [string]$Listen = "0.0.0.0",
    [int]$Port = 8002,
    [string]$OllamaBaseUrl = "http://127.0.0.1:11434",
    [string]$EmbeddingModel = "bge-m3",
    [string]$RuntimeModel = "bge-m3-embedding-reranker",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$pythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$logDir = Join-Path $RepoRoot "storage\logs"
$stdoutLog = Join-Path $logDir "reranker_worker_stdout.log"
$stderrLog = Join-Path $logDir "reranker_worker_stderr.log"
$healthUrl = "http://127.0.0.1:$Port/health"

if (!(Test-Path $RepoRoot)) {
    throw "Repository root does not exist: $RepoRoot"
}
if (!(Test-Path $pythonExe)) {
    throw "Repository virtualenv Python does not exist: $pythonExe"
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$env:RERANKER_RUNTIME_EMBEDDING_BASE_URL = $OllamaBaseUrl
$env:RERANKER_RUNTIME_EMBEDDING_MODEL = $EmbeddingModel
$env:RERANKER_RUNTIME_MODEL = $RuntimeModel
$env:RERANKER_RUNTIME_HOST = $Listen
$env:RERANKER_RUNTIME_PORT = "$Port"

if (!$Force) {
    try {
        $health = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 10
        if ($health.reachable -eq $true) {
            Write-Host "Reranker worker already responds at $healthUrl"
            exit 0
        }
        Write-Host "Reranker worker responds but is not reachable; restarting it."
    } catch {
        Write-Host "Reranker worker is not reachable yet; starting it now."
    }
}

Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    ForEach-Object {
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
    }
Start-Sleep -Seconds 2

$process = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList @("-m", "uvicorn", "worker.reranker_worker.main:app", "--host", $Listen, "--port", "$Port") `
    -WorkingDirectory $RepoRoot `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -WindowStyle Hidden `
    -PassThru

Write-Host "Started reranker worker pid=$($process.Id) url=http://${Listen}:$Port"
Write-Host "stdout=$stdoutLog"
Write-Host "stderr=$stderrLog"
