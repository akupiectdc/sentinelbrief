#!/usr/bin/env pwsh
#
# Start the SentinelBrief dev stack on Windows (PowerShell):
#   - Python ai-service (via uv) on :8000
#   - C# gateway on :8080
# then seed the demo corpus. Press Ctrl-C to stop everything cleanly.
#
# This assumes the local infrastructure is already running:
#   - Ollama on :11434   (the Windows installer runs it automatically)
#   - Qdrant on :6333    (e.g. `docker compose up -d qdrant`)
#
# Usage (from the repo root, in PowerShell):
#   ./scripts/dev.ps1
#
# If Windows blocks the script, allow local scripts once:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

$ErrorActionPreference = 'Stop'

$Root    = Split-Path -Parent $PSScriptRoot
$AiPort  = 8000
$WebPort = 8080
$AiUrl   = "http://localhost:$AiPort"
$WebUrl  = "http://localhost:$WebPort"

$AiProc  = $null
$WebProc = $null

function Test-Service($name, $url) {
    try {
        Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 2 | Out-Null
        Write-Host "  + $name reachable"
    } catch {
        Write-Host "  ! $name NOT reachable at $url (start it, or answers will fail with 502)"
    }
}

# Kill a process and its children (uvicorn / dotnet spawn child processes).
function Stop-Tree($proc) {
    if ($proc -and -not $proc.HasExited) {
        taskkill /PID $proc.Id /T /F 2>$null | Out-Null
    }
}

try {
    Write-Host "Checking local infrastructure..."
    Test-Service "Ollama" "http://localhost:11434/api/tags"
    Test-Service "Qdrant" "http://localhost:6333/collections"

    Write-Host "Starting ai-service (uv) on $AiPort..."
    $AiProc = Start-Process -PassThru -NoNewWindow `
        -WorkingDirectory "$Root\src\ai-service" `
        -FilePath "uv" `
        -ArgumentList @("run", "uvicorn", "app.main:app", "--port", "$AiPort")

    Write-Host "Starting C# gateway on $WebPort..."
    $env:AI_SERVICE_URL = $AiUrl
    $env:ASPNETCORE_URLS = $WebUrl
    $WebProc = Start-Process -PassThru -NoNewWindow `
        -WorkingDirectory "$Root\src\web-api" `
        -FilePath "dotnet" `
        -ArgumentList @("run", "--project", "SentinelBrief.WebApi")

    Write-Host -NoNewline "Waiting for services to be ready"
    $ready = $false
    for ($i = 0; $i -lt 120; $i++) {
        try {
            Invoke-WebRequest -UseBasicParsing -Uri "$AiUrl/health"  -TimeoutSec 2 | Out-Null
            Invoke-WebRequest -UseBasicParsing -Uri "$WebUrl/health" -TimeoutSec 2 | Out-Null
            $ready = $true
            break
        } catch {
            Write-Host -NoNewline "."
            Start-Sleep -Seconds 1
        }
    }
    Write-Host ""

    if (-not $ready) {
        Write-Host "Services did not become ready in time. See the logs above."
        exit 1
    }

    # Seeding can fail transiently (e.g. Ollama still warming up), so retry and
    # then verify the corpus is actually non-empty. An empty corpus makes every
    # answer a refusal, so we surface that loudly instead of declaring success.
    # Seed against the ai-service directly (snake_case-native); verify through
    # the gateway so the public read path is exercised too.
    Write-Host "Seeding demo corpus..."
    $seeded = $false
    foreach ($attempt in 1..3) {
        try {
            Push-Location $Root
            uv run --project src/ai-service python scripts/seed_demo.py $AiUrl
        } catch {
        } finally {
            Pop-Location
        }
        $count = 0
        try { $count = [int](Invoke-RestMethod -Uri "$WebUrl/documents" -TimeoutSec 5).count } catch {}
        if ($count -gt 0) {
            $seeded = $true
            Write-Host "  corpus ready: $count document(s) indexed"
            break
        }
        Write-Host "  seed attempt $attempt left the corpus empty; retrying in 3s..."
        Start-Sleep -Seconds 3
    }
    if (-not $seeded) {
        Write-Host "  WARNING: corpus is still empty - answers will be refusals."
        Write-Host "  Re-run later: uv run --project src/ai-service python scripts/seed_demo.py $AiUrl"
    }

    Write-Host ""
    Write-Host "--------------------------------------------"
    Write-Host "  SentinelBrief is up:"
    Write-Host "    Demo page  : $WebUrl"
    Write-Host "    API docs   : $AiUrl/docs"
    Write-Host "  Press Ctrl-C to stop everything."
    Write-Host "--------------------------------------------"

    # Block until either server exits or the user presses Ctrl-C.
    while (-not $AiProc.HasExited -and -not $WebProc.HasExited) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host ""
    Write-Host "Shutting down..."
    Stop-Tree $WebProc
    Stop-Tree $AiProc
    Write-Host "Stopped."
}
