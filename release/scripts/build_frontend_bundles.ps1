param(
    [string]$OutputDir = "release/build/frontends"
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$target = Join-Path $repoRoot $OutputDir
$frontends = @("admin_dashboard", "worker_console", "worker_console_desktop")

New-Item -ItemType Directory -Force -Path $target | Out-Null

foreach ($frontend in $frontends) {
    $frontendPath = Join-Path $repoRoot $frontend
    Write-Host "Building $frontend"
    Push-Location $frontendPath
    npm install
    npm run build
    Pop-Location

    $dist = Join-Path $frontendPath "dist"
    if (-not (Test-Path $dist)) {
        throw "Missing frontend dist: $frontend/dist"
    }
    $destination = Join-Path $target $frontend
    if (Test-Path $destination) {
        Remove-Item -Recurse -Force $destination
    }
    Copy-Item -Path $dist -Destination $destination -Recurse -Force
}

Write-Host "Frontend build bundles complete."

