param(
    [string]$RepoRoot = "D:\ai-operations-system",
    [string]$TaskName = "AI Ops Reranker Worker",
    [string]$TaskUser = "SYSTEM"
)

$ErrorActionPreference = "Stop"

$repoScript = Join-Path $PSScriptRoot "start_reranker_aiops.ps1"
if (!(Test-Path $repoScript)) {
    throw "Cannot find repository startup script: $repoScript"
}
if (!(Test-Path $RepoRoot)) {
    throw "Repository root does not exist: $RepoRoot"
}

$quotedScript = '"' + (Resolve-Path $repoScript).Path + '"'
$quotedRoot = '"' + (Resolve-Path $RepoRoot).Path + '"'

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File $quotedScript -RepoRoot $quotedRoot"

$trigger = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = "PT90S"

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
    -Description "Start local reranker worker for AI Operations System after server reboot." `
    -Force | Out-Null

Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State, TaskPath
