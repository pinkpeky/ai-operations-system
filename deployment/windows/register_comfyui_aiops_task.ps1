param(
    [string]$ComfyRoot = "E:\ComfyUI_cu130\ComfyUI",
    [string]$TaskName = "AI Ops ComfyUI CU130",
    [string]$TaskUser = "SYSTEM",
    [switch]$UseRepositoryScript
)

$ErrorActionPreference = "Stop"

$repoScript = Join-Path $PSScriptRoot "start_comfyui_aiops.ps1"
if (!(Test-Path $repoScript)) {
    throw "Cannot find repository startup script: $repoScript"
}

if (!(Test-Path $ComfyRoot)) {
    throw "ComfyUI root does not exist: $ComfyRoot"
}

if ($UseRepositoryScript) {
    $taskScript = (Resolve-Path $repoScript).Path
} else {
    $taskScript = Join-Path $ComfyRoot "start-comfyui-aiops.ps1"
    Copy-Item -LiteralPath $repoScript -Destination $taskScript -Force
}

$quotedScript = '"' + $taskScript + '"'
$quotedRoot = '"' + $ComfyRoot + '"'
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File $quotedScript -ComfyRoot $quotedRoot"

$trigger = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = "PT1M"

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 2)

$principal = New-ScheduledTaskPrincipal -UserId $TaskUser -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Start E:\ComfyUI_cu130\ComfyUI for AI Operations System after server reboot." `
    -Force | Out-Null

Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State, TaskPath
