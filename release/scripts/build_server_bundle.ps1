param(
    [string]$OutputDir = "release/build/server"
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$target = Join-Path $repoRoot $OutputDir

Write-Host "Building server deployment bundle at $target"
if (Test-Path $target) {
    Remove-Item -Recurse -Force $target
}
New-Item -ItemType Directory -Force -Path $target | Out-Null

$paths = @(
    "app",
    "alembic",
    "worker",
    "worker_client",
    "docs/CURRENT_RUNTIME.md",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    "alembic.ini",
    ".env.example",
    "release/manifest.json",
    "release/version.json",
    "release/env/aiops.release.env.template"
)

foreach ($path in $paths) {
    $source = Join-Path $repoRoot $path
    if (-not (Test-Path $source)) {
        throw "Missing bundle source: $path"
    }
    $destination = Join-Path $target $path
    $parent = Split-Path -Parent $destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    Copy-Item -Path $source -Destination $destination -Recurse -Force
}

Write-Host "Server bundle complete. This is not a production HA package."

