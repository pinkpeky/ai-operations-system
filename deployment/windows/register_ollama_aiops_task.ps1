param(
    [string]$TaskName = "AI Ops Ollama D Drive",
    [string]$TaskUser = "SYSTEM",
    [string]$ModelsRoot = "D:\ollama\models",
    [string]$HostAddress = "0.0.0.0:11434"
)

$ErrorActionPreference = "Stop"

$repoScript = Join-Path $PSScriptRoot "start_ollama_aiops.ps1"
if (!(Test-Path $repoScript)) {
    throw "Cannot find repository startup script: $repoScript"
}

$quotedScript = '"' + (Resolve-Path $repoScript).Path + '"'
$quotedModels = '"' + $ModelsRoot + '"'
$quotedHost = '"' + $HostAddress + '"'

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File $quotedScript -ModelsRoot $quotedModels -HostAddress $quotedHost"

$trigger = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = "PT30S"

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
    -Description "Start Ollama with D:\ollama\models for AI Operations System after server reboot." `
    -Force | Out-Null

Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State, TaskPath
