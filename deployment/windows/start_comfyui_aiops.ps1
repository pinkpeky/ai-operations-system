param(
    [string]$ComfyRoot = "E:\ComfyUI_cu130\ComfyUI",
    [string]$Listen = "127.0.0.1",
    [int]$Port = 8188,
    [int]$CudaDevice = 0,
    [string]$FfmpegDir = "",
    [string[]]$ExtraArgs = @("--preview-method", "auto", "--use-sage-attention", "--cuda-malloc", "--enable-manager"),
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Resolve-FfmpegDirectory {
    param([string]$RequestedDir)

    if ($RequestedDir -and (Test-Path $RequestedDir)) {
        return (Resolve-Path $RequestedDir).Path
    }

    $knownWingetDir = "C:\Users\Administrator\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"
    if (Test-Path (Join-Path $knownWingetDir "ffmpeg.exe")) {
        return $knownWingetDir
    }

    $ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if ($ffmpeg) {
        return Split-Path -Parent $ffmpeg.Source
    }

    return $null
}

$logDir = Join-Path $ComfyRoot "logs"
$stdoutLog = Join-Path $logDir "comfyui_stdout.log"
$stderrLog = Join-Path $logDir "comfyui_stderr.log"

if (!(Test-Path $ComfyRoot)) {
    throw "ComfyUI root does not exist: $ComfyRoot"
}

$pythonCandidates = @(
    (Join-Path $ComfyRoot "venv\Scripts\python.exe"),
    (Join-Path (Split-Path -Parent $ComfyRoot) "python\python.exe")
)
$pythonExe = $pythonCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (!$pythonExe) {
    throw "ComfyUI Python does not exist. Checked: $($pythonCandidates -join ', ')"
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$resolvedFfmpegDir = Resolve-FfmpegDirectory -RequestedDir $FfmpegDir
if ($resolvedFfmpegDir) {
    $env:FFMPEG_PATH = $resolvedFfmpegDir
    if ($env:PATH -notlike "*$resolvedFfmpegDir*") {
        $env:PATH = "$resolvedFfmpegDir;$env:PATH"
    }
}

if (!$Force) {
    try {
        Invoke-RestMethod -Uri "http://${Listen}:$Port/system_stats" -TimeoutSec 3 | Out-Null
        Write-Host "ComfyUI already responds on http://${Listen}:$Port"
        exit 0
    } catch {
        Write-Host "ComfyUI is not reachable yet; starting it now."
    }
}

Set-Location $ComfyRoot

$process = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList (@("main.py", "--listen", $Listen, "--port", "$Port", "--disable-auto-launch", "--cuda-device", "$CudaDevice") + $ExtraArgs) `
    -WorkingDirectory $ComfyRoot `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -WindowStyle Hidden `
    -PassThru

Write-Host "Started ComfyUI pid=$($process.Id) root=$ComfyRoot url=http://${Listen}:$Port"
Write-Host "stdout=$stdoutLog"
Write-Host "stderr=$stderrLog"
