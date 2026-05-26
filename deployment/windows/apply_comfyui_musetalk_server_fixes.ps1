param(
    [string]$ComfyRoot = "E:\ComfyUI",
    [string]$PatchPath = ""
)

$ErrorActionPreference = "Stop"

function Replace-InFile {
    param(
        [string]$Path,
        [string]$Old,
        [string]$New
    )

    if (!(Test-Path $Path)) {
        throw "Missing file: $Path"
    }

    $text = Get-Content -LiteralPath $Path -Raw
    if ($text.Contains($New)) {
        Write-Host "Already patched: $Path"
        return
    }

    if (!$text.Contains($Old)) {
        throw "Expected text not found in $Path"
    }

    $updated = $text.Replace($Old, $New)
    Set-Content -LiteralPath $Path -Value $updated -Encoding UTF8 -NoNewline
    Write-Host "Patched: $Path"
}

function Normalize-InFileIfPresent {
    param(
        [string]$Path,
        [string]$Old,
        [string]$New
    )

    if (!(Test-Path $Path)) {
        throw "Missing file: $Path"
    }

    $text = Get-Content -LiteralPath $Path -Raw
    if ($text.Contains($Old)) {
        Set-Content -LiteralPath $Path -Value $text.Replace($Old, $New) -Encoding UTF8 -NoNewline
        Write-Host "Normalized: $Path"
    }
}

if (!$PatchPath) {
    $repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
    $PatchPath = Join-Path $repoRoot "deployment\comfyui\musetalk_fsh_windows_compat.patch"
}

$museTalkRoot = Join-Path $ComfyRoot "custom_nodes\ComfyUI-MuseTalk_FSH"
if (!(Test-Path $museTalkRoot)) {
    throw "ComfyUI-MuseTalk_FSH does not exist: $museTalkRoot"
}
if (!(Test-Path $PatchPath)) {
    throw "Patch file does not exist: $PatchPath"
}

$faceParsingInitPath = Join-Path $museTalkRoot "musetalk\utils\face_parsing\__init__.py"
Normalize-InFileIfPresent `
    -Path $faceParsingInitPath `
    -Old "net.load_state_dict(torch.load(model_pth)) " `
    -New "net.load_state_dict(torch.load(model_pth))"
Normalize-InFileIfPresent `
    -Path $faceParsingInitPath `
    -Old "net.load_state_dict(torch.load(model_pth, weights_only=False)) " `
    -New "net.load_state_dict(torch.load(model_pth, weights_only=False))"

Push-Location $museTalkRoot
try {
    git apply --ignore-whitespace --reverse --check $PatchPath 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "MuseTalk compatibility patch is already applied."
    } else {
        git apply --ignore-whitespace --check $PatchPath
        if ($LASTEXITCODE -ne 0) {
            throw "MuseTalk compatibility patch does not apply cleanly."
        }
        git apply --ignore-whitespace $PatchPath
        Write-Host "Applied MuseTalk compatibility patch."
    }
} finally {
    Pop-Location
}

$sfdDetectorPath = Join-Path $museTalkRoot "musetalk\utils\face_detection\detection\sfd\sfd_detector.py"
Replace-InFile `
    -Path $sfdDetectorPath `
    -Old "model_weights = torch.load(path_to_detector)" `
    -New "model_weights = torch.load(path_to_detector, weights_only=False)"

$checkpointPath = Join-Path $ComfyRoot "venv\Lib\site-packages\mmengine\runner\checkpoint.py"
Replace-InFile `
    -Path $checkpointPath `
    -Old "checkpoint = torch.load(filename, map_location=map_location)" `
    -New "checkpoint = torch.load(filename, map_location=map_location, weights_only=False)"

Write-Host "ComfyUI MuseTalk server fixes are in place."
