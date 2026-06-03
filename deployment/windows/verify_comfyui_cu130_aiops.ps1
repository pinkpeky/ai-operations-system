param(
    [string]$RepoRoot = "D:\ai-operations-system",
    [string]$ComfyRoot = "E:\ComfyUI_cu130\ComfyUI",
    [string]$ComfyBaseUrl = "http://127.0.0.1:8188"
)

$ErrorActionPreference = "Stop"
$failures = 0

function Report {
    param([string]$Name, [bool]$Ok, [string]$Detail = "")
    if ($Ok) {
        Write-Host "[OK] $Name $Detail"
    } else {
        Write-Host "[FAIL] $Name $Detail"
        $script:failures += 1
    }
}

function Get-Json {
    param([string]$Uri)
    Invoke-RestMethod -Uri $Uri -TimeoutSec 30
}

Report "ComfyUI root" (Test-Path $ComfyRoot) $ComfyRoot
Report "models root" (Test-Path (Join-Path $ComfyRoot "models")) (Join-Path $ComfyRoot "models")
Report "workflow root" (Test-Path (Join-Path $ComfyRoot "user\default\workflows")) (Join-Path $ComfyRoot "user\default\workflows")

try {
    $stats = Get-Json "$ComfyBaseUrl/system_stats"
    $gpu = $stats.devices | Select-Object -First 1
    Report "ComfyUI /system_stats" $true "$($stats.system.comfyui_version), $($stats.system.pytorch_version), $($gpu.name)"
} catch {
    Report "ComfyUI /system_stats" $false $_.Exception.Message
}

try {
    $queue = Get-Json "$ComfyBaseUrl/queue"
    Report "ComfyUI /queue" ($null -ne $queue.queue_running -and $null -ne $queue.queue_pending) "running=$(@($queue.queue_running).Count) pending=$(@($queue.queue_pending).Count)"
} catch {
    Report "ComfyUI /queue" $false $_.Exception.Message
}

try {
    $objectInfoRaw = (Invoke-WebRequest -UseBasicParsing -Uri "$ComfyBaseUrl/object_info" -TimeoutSec 30).Content
    foreach ($node in @("LoadVideo", "VHS_LoadVideo", "AILab_Qwen3ASR", "AILab_QwenVL", "SAM3_Detect", "DepthAnything_V2")) {
        Report "node $node" ($objectInfoRaw -match ('"' + [regex]::Escape($node) + '"\s*:'))
    }
} catch {
    Report "ComfyUI /object_info" $false $_.Exception.Message
}

$requiredModelHints = @(
    "models\Qwen3-ASR",
    "models\whisper",
    "models\text_encoders\qwen_2.5_vl_7b_fp8_scaled.safetensors",
    "models\sam3\sam3.pt",
    "models\sam3\sam3.1_multiplex.pt",
    "models\sam2\sam2.1_hiera_base_plus-fp16.safetensors",
    "models\depthanything\depth_anything_v2_vitl_fp16.safetensors",
    "models\diffusion_models\Wan\Wan2.2_Animate_14B_Q6_K.gguf",
    "models\model_patches\Wan2_1-infiniTetalk-single_fp16.safetensors"
)

foreach ($relative in $requiredModelHints) {
    $path = Join-Path $ComfyRoot $relative
    Report "model hint $relative" (Test-Path $path)
}

$pythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$auditScript = Join-Path $RepoRoot "scripts\audit_comfyui_cu130_runtime.py"
if ((Test-Path $pythonExe) -and (Test-Path $auditScript)) {
    try {
        Push-Location $RepoRoot
        & $pythonExe $auditScript | Write-Host
        if ($LASTEXITCODE -ne 0) {
            Report "runtime audit script" $false "exit=$LASTEXITCODE"
        } else {
            Report "runtime audit script" $true
        }
    } catch {
        Report "runtime audit script" $false $_.Exception.Message
    } finally {
        Pop-Location
    }
} else {
    Report "runtime audit script" $false "missing python or audit script"
}

if ($failures -gt 0) {
    throw "$failures ComfyUI_cu130 verification check(s) failed."
}

Write-Host "ComfyUI_cu130 AI Ops verification completed successfully."
