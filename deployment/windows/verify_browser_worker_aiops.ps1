param(
    [string]$RepoRoot = "D:\ai-operations-system",
    [string]$WorkerBaseUrl = "http://127.0.0.1:9100",
    [string]$EnvPath = "",
    [string]$StatePath = ""
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

function Read-WorkerStateSecret {
    param([string]$Path)
    if (!(Test-Path $Path)) {
        return $null
    }
    try {
        $state = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
        if ($state.worker_secret) {
            return [string]$state.worker_secret
        }
    } catch {
        return $null
    }
    return $null
}

if (!$EnvPath) {
    $EnvPath = Join-Path $RepoRoot ".env"
}
if (!$StatePath) {
    $StatePath = Join-Path $RepoRoot "worker_client\worker_state.json"
}

try {
    $health = Invoke-RestMethod -Uri "$WorkerBaseUrl/health" -TimeoutSec 10
    Report "Browser worker /health" ($health.success -eq $true -and $health.capabilities.browser_runtime -eq $true) "type=$($health.worker_type)"
} catch {
    Report "Browser worker /health" $false $_.Exception.Message
}

try {
    Invoke-RestMethod -Uri "$WorkerBaseUrl/browser/session/create" -Method Post -ContentType "application/json" -Body '{"workspace_id":"browser-worker-verify"}' -TimeoutSec 20 | Out-Null
    Report "Unsigned strict request rejected" $false "unsigned request unexpectedly succeeded"
} catch {
    $status = $_.Exception.Response.StatusCode.value__
    Report "Unsigned strict request rejected" ($status -eq 401) "status=$status"
}

$secret = Read-WorkerStateSecret -Path $StatePath
if (!$secret) {
    $secret = Read-DotEnvValue -Path $EnvPath -Key "BROWSER_WORKER_SHARED_SECRET"
}
if (!$secret) {
    $secret = Read-DotEnvValue -Path $EnvPath -Key "BROWSER_WORKER_SECRET"
}

if (!$secret) {
    Report "Signed browser session" $false "missing shared secret"
} else {
    $pythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    $verifyScript = @"
import asyncio
import hashlib
import hmac
import json
import os
import secrets
import time
import httpx

def sign(secret, body):
    timestamp = str(int(time.time()))
    nonce = secrets.token_urlsafe(16)
    body_text = "" if body is None else json.dumps(body, sort_keys=True, separators=(",", ":"))
    body_hash = hashlib.sha256(body_text.encode("utf-8")).hexdigest()
    signing_text = "\n".join([timestamp, nonce, body_hash])
    signature = hmac.new(secret.encode("utf-8"), signing_text.encode("utf-8"), hashlib.sha256).hexdigest()
    return {
        "X-Worker-Timestamp": timestamp,
        "X-Worker-Nonce": nonce,
        "X-Worker-Body-Hash": body_hash,
        "X-Worker-Signature": signature,
        "X-Worker-Id": "verify-worker",
    }

async def main():
    secret = os.environ["VERIFY_BROWSER_WORKER_SECRET"]
    create_payload = {"workspace_id": "browser-worker-verify", "metadata": {"source": "verify_browser_worker_aiops"}}
    async with httpx.AsyncClient(base_url="$WorkerBaseUrl", timeout=60) as client:
        create_response = await client.post("/browser/session/create", json=create_payload, headers=sign(secret, create_payload))
        created = create_response.json()
        if create_response.status_code >= 400 or not created.get("success"):
            raise RuntimeError(created.get("error") or created.get("message") or str(created))
        session_id = str(created.get("remote_session_id") or created.get("session_id") or "")
        if not session_id:
            raise RuntimeError("remote_session_id missing")
        close_response = await client.post(f"/browser/session/{session_id}/close", headers=sign(secret, None))
        closed = close_response.json()
        if close_response.status_code >= 400 or not closed.get("success"):
            raise RuntimeError(closed.get("error") or closed.get("message") or str(closed))
        print("SIGNED_SESSION_OK")

asyncio.run(main())
"@
    try {
        $env:VERIFY_BROWSER_WORKER_SECRET = $secret
        $output = $verifyScript | & $pythonExe -
        Report "Signed browser session" (($output -join "`n") -match "SIGNED_SESSION_OK")
    } catch {
        Report "Signed browser session" $false $_.Exception.Message
    } finally {
        Remove-Item Env:\VERIFY_BROWSER_WORKER_SECRET -ErrorAction SilentlyContinue
    }
}

if ($failures -gt 0) {
    throw "$failures Browser Worker verification checks failed"
}

Write-Host "SUMMARY: PASS"
