param(
    [string]$OllamaExe = "C:\Users\Administrator\AppData\Local\Programs\Ollama\ollama.exe",
    [string]$ModelsRoot = "D:\ollama\models",
    [string]$HostAddress = "0.0.0.0:11434",
    [string]$HealthUrl = "http://127.0.0.1:11434/api/tags",
    [string]$LogDir = "D:\ollama\logs",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $OllamaExe)) {
    throw "Ollama executable does not exist: $OllamaExe"
}
if (!(Test-Path $ModelsRoot)) {
    throw "Ollama models root does not exist: $ModelsRoot"
}
if (!(Test-Path (Join-Path $ModelsRoot "manifests"))) {
    throw "Ollama models root is missing manifests: $ModelsRoot"
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$env:OLLAMA_MODELS = $ModelsRoot
$env:OLLAMA_HOST = $HostAddress
$env:OLLAMA_SCHED_SPREAD = "true"
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $ModelsRoot, "User")
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", $HostAddress, "User")
[Environment]::SetEnvironmentVariable("OLLAMA_SCHED_SPREAD", "true", "User")

if (!$Force) {
    try {
        $tags = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 5
        if ($tags.models -and $tags.models.Count -gt 0) {
            Write-Host "Ollama already responds with $($tags.models.Count) models at $HealthUrl"
            exit 0
        }
        Write-Host "Ollama responds but has no visible models; restarting with OLLAMA_MODELS=$ModelsRoot"
    } catch {
        Write-Host "Ollama is not reachable yet; starting it now."
    }
}

Get-Process | Where-Object { $_.ProcessName -like "ollama*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

$stdoutLog = Join-Path $LogDir "ollama_stdout.log"
$stderrLog = Join-Path $LogDir "ollama_stderr.log"

$process = Start-Process `
    -FilePath $OllamaExe `
    -ArgumentList @("serve") `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -WindowStyle Hidden `
    -PassThru

Write-Host "Started Ollama pid=$($process.Id) models=$ModelsRoot host=$HostAddress"
Write-Host "stdout=$stdoutLog"
Write-Host "stderr=$stderrLog"
