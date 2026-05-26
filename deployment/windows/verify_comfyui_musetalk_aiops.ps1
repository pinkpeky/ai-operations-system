param(
    [string]$ComfyRoot = "E:\ComfyUI",
    [string]$ComfyBaseUrl = "http://127.0.0.1:8188",
    [string]$ApiBaseUrl = "http://localhost:8000",
    [string]$WorkspaceId = "video-smoke",
    [switch]$SkipApi
)

$ErrorActionPreference = "Stop"
$failures = 0

function Report {
    param(
        [string]$Name,
        [bool]$Ok,
        [string]$Detail = ""
    )
    if ($Ok) {
        Write-Host "[OK] $Name $Detail"
    } else {
        Write-Host "[FAIL] $Name $Detail"
        $script:failures += 1
    }
}

function Get-Json {
    param([string]$Uri, [hashtable]$Headers = @{})
    Invoke-RestMethod -Uri $Uri -Headers $Headers -TimeoutSec 30
}

$modelsRoot = Join-Path $ComfyRoot "custom_nodes\ComfyUI-MuseTalk_FSH\models"
$expectedModels = @(
    @{ Rel = "musetalk\musetalk.json"; Size = 748 },
    @{ Rel = "musetalk\pytorch_model.bin"; Size = 3400076549 },
    @{ Rel = "dwpose\dw-ll_ucoco_384.pth"; Size = 406878486 },
    @{ Rel = "face-parse-bisent\79999_iter.pth"; Size = 53289463 },
    @{ Rel = "face-parse-bisent\resnet18-5c106cde.pth"; Size = 46827520 },
    @{ Rel = "sd-vae-ft-mse\config.json"; Size = 547 },
    @{ Rel = "sd-vae-ft-mse\diffusion_pytorch_model.bin"; Size = 334707217 },
    @{ Rel = "whisper\tiny.pt"; Size = 75572083 }
)

Report "ComfyUI root" (Test-Path $ComfyRoot) $ComfyRoot
Report "MuseTalk models root" (Test-Path $modelsRoot) $modelsRoot

foreach ($model in $expectedModels) {
    $path = Join-Path $modelsRoot $model.Rel
    if (Test-Path $path) {
        $item = Get-Item $path
        Report "model $($model.Rel)" ($item.Length -ge [int64]$model.Size) "$($item.Length)/$($model.Size)"
    } else {
        Report "model $($model.Rel)" $false "missing"
    }
}

try {
    $stats = Get-Json "$ComfyBaseUrl/system_stats"
    $gpu = $stats.devices | Select-Object -First 1
    Report "ComfyUI /system_stats" $true "$($stats.system.comfyui_version), $($gpu.name)"
} catch {
    Report "ComfyUI /system_stats" $false $_.Exception.Message
}

try {
    $objectInfo = Get-Json "$ComfyBaseUrl/object_info"
    $nodeNames = $objectInfo.PSObject.Properties.Name
    $requiredNodes = @(
        "VHS_VideoCombine",
        "AdvancedLivePortrait",
        "MuseTalk",
        "MuseTalkRealTime",
        "MuseTalkLoadVideo",
        "PreViewVideo",
        "CombineAudioVideo",
        "LoadAudio"
    )
    foreach ($node in $requiredNodes) {
        Report "node $node" ($nodeNames -contains $node)
    }
} catch {
    Report "ComfyUI /object_info" $false $_.Exception.Message
}

$demoOutput = Join-Path $ComfyRoot "output\aiops_ops_story_avatar_aiops_ops_story_avatar.mp4"
if (Test-Path $demoOutput) {
    $ffprobe = Get-Command ffprobe -ErrorAction SilentlyContinue
    if ($ffprobe) {
        $probe = & ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,duration -show_entries format=duration,size -of json $demoOutput | ConvertFrom-Json
        $hasVideo = @($probe.streams | Where-Object { $_.codec_type -eq "video" }).Count -gt 0
        $hasAudio = @($probe.streams | Where-Object { $_.codec_type -eq "audio" }).Count -gt 0
        Report "demo output stream check" ($hasVideo -and $hasAudio) "$demoOutput"
    } else {
        Report "demo output exists" $true $demoOutput
    }
} else {
    Write-Host "[INFO] demo output not present: $demoOutput"
}

$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollama) {
    $ollamaList = ollama list | Out-String
    Report "ollama llama70b" ($ollamaList -match "llama70b|llama3\.3:70b")
    Report "ollama bge-m3" ($ollamaList -match "bge-m3")
} else {
    Write-Host "[INFO] ollama command not found; skipping local model check."
}

if (!$SkipApi) {
    $headers = @{ "X-Workspace-Id" = $WorkspaceId }
    try {
        $health = Get-Json "$ApiBaseUrl/api/v1/health"
        Report "AI Ops API health" ($health.status -eq "ok")
    } catch {
        Report "AI Ops API health" $false $_.Exception.Message
    }

    try {
        $runtimeHealth = Get-Json "$ApiBaseUrl/api/v1/comfyui-runtime/health" $headers
        Report "AI Ops guarded ComfyUI health" ($runtimeHealth.success -and $runtimeHealth.reachable) "$($runtimeHealth.base_url)"
    } catch {
        Report "AI Ops guarded ComfyUI health" $false $_.Exception.Message
    }

    try {
        $queue = Get-Json "$ApiBaseUrl/api/v1/comfyui-runtime/queue" $headers
        Report "AI Ops guarded ComfyUI queue" $queue.success
    } catch {
        Report "AI Ops guarded ComfyUI queue" $false $_.Exception.Message
    }
}

if ($failures -gt 0) {
    throw "$failures ComfyUI/MuseTalk verification check(s) failed."
}

Write-Host "ComfyUI/MuseTalk AI Ops verification completed successfully."
