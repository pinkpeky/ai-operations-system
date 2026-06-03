param(
    [string]$RepoRoot = "D:\ai-operations-system",
    [string]$Listen = "0.0.0.0",
    [int]$Port = 9100,
    [string]$EnvPath = "",
    [switch]$SkipHeartbeat,
    [switch]$Force
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

function Stop-ExistingBrowserWorkerOnPort {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    $owners = $connections | Select-Object LocalAddress, OwningProcess -Unique
    foreach ($owner in $owners) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($owner.OwningProcess)" -ErrorAction SilentlyContinue
        if (!$process) {
            continue
        }
        $name = [string]$process.Name
        $commandLine = [string]$process.CommandLine
        $isPythonWorker = ($name -match "python|uvicorn") -and ($commandLine -match "worker\.main:app")
        if ($isPythonWorker) {
            Stop-Process -Id $owner.OwningProcess -Force -ErrorAction SilentlyContinue
            continue
        }
        $isDockerProxy = ($name -match "com\.docker\.backend|wslrelay") -or ($commandLine -match "Docker|wslrelay")
        if ($isDockerProxy -and ($owner.LocalAddress -eq "::" -or $owner.LocalAddress -eq "::1")) {
            Write-Host "[WARN] Port $Port also has Docker/WSL IPv6 relay pid=$($owner.OwningProcess); not stopping it."
            continue
        }
        throw "Port $Port is owned by pid=$($owner.OwningProcess) name=$name. Stop the conflicting service first; this script only stops worker.main Python processes."
    }
}

function Start-WorkerHeartbeatLoop {
    param(
        [string]$PythonExe,
        [string]$RepoRoot,
        [string]$LogDir
    )

    $escapedRoot = [regex]::Escape($RepoRoot)
    $existing = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -match "python" -and
            $_.CommandLine -match "worker_client\.cli" -and
            $_.CommandLine -match "heartbeat" -and
            $_.CommandLine -match $escapedRoot
        } |
        Select-Object -First 1

    if ($existing) {
        Write-Host "Browser worker heartbeat already running pid=$($existing.ProcessId)"
        return
    }

    $stdoutLog = Join-Path $LogDir "browser_worker_heartbeat_stdout.log"
    $stderrLog = Join-Path $LogDir "browser_worker_heartbeat_stderr.log"
    $configPath = Join-Path $RepoRoot "worker_client\worker_config.yaml"

    $process = Start-Process `
        -FilePath $PythonExe `
        -ArgumentList @("-m", "worker_client.cli", "--config", $configPath, "heartbeat") `
        -WorkingDirectory $RepoRoot `
        -RedirectStandardOutput $stdoutLog `
        -RedirectStandardError $stderrLog `
        -WindowStyle Hidden `
        -PassThru

    Write-Host "Started browser worker heartbeat pid=$($process.Id)"
    Write-Host "heartbeat_stdout=$stdoutLog"
    Write-Host "heartbeat_stderr=$stderrLog"
}

if (!$EnvPath) {
    $EnvPath = Join-Path $RepoRoot ".env"
}

$pythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$logDir = Join-Path $RepoRoot "storage\logs"
$stdoutLog = Join-Path $logDir "browser_worker_stdout.log"
$stderrLog = Join-Path $logDir "browser_worker_stderr.log"
$healthUrl = "http://127.0.0.1:$Port/health"

if (!(Test-Path $RepoRoot)) {
    throw "Repository root does not exist: $RepoRoot"
}
if (!(Test-Path $pythonExe)) {
    throw "Repository virtualenv Python does not exist: $pythonExe"
}

$secret = Read-DotEnvValue -Path $EnvPath -Key "BROWSER_WORKER_SHARED_SECRET"
if (!$secret) {
    $secret = Read-DotEnvValue -Path $EnvPath -Key "BROWSER_WORKER_SECRET"
}
if (!$secret -or $secret.Length -lt 16) {
    throw "BROWSER_WORKER_SHARED_SECRET is missing or too short in $EnvPath"
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$env:WORKER_HOST = $Listen
$env:WORKER_PORT = "$Port"
$env:BROWSER_WORKER_AUTH_ENABLED = "true"
$env:BROWSER_WORKER_AUTH_STRICT = "true"
$env:BROWSER_WORKER_SECRET = $secret
$env:WORKER_BROWSER_TYPE = "chromium"
$env:WORKER_HEADLESS = "true"
$env:WORKER_SCREENSHOT_DIR = Join-Path $RepoRoot "worker\screenshots"
$env:WORKER_PROFILE_DIR = Join-Path $RepoRoot "worker\profiles"

if (!$Force) {
    try {
        Invoke-RestMethod -Uri $healthUrl -TimeoutSec 5 | Out-Null
        Write-Host "Browser worker already responds at $healthUrl"
        if (!$SkipHeartbeat) {
            Start-WorkerHeartbeatLoop -PythonExe $pythonExe -RepoRoot $RepoRoot -LogDir $logDir
        }
        exit 0
    } catch {
        Write-Host "Browser worker is not reachable yet; starting it now."
    }
}

Stop-ExistingBrowserWorkerOnPort -Port $Port
Start-Sleep -Seconds 2

$process = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList @("-m", "uvicorn", "worker.main:app", "--host", $Listen, "--port", "$Port") `
    -WorkingDirectory $RepoRoot `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -WindowStyle Hidden `
    -PassThru

Write-Host "Started browser worker pid=$($process.Id) url=http://${Listen}:$Port"
Write-Host "stdout=$stdoutLog"
Write-Host "stderr=$stderrLog"

if (!$SkipHeartbeat) {
    Start-WorkerHeartbeatLoop -PythonExe $pythonExe -RepoRoot $RepoRoot -LogDir $logDir
}
