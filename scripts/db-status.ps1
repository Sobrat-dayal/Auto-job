# AUTONOM — Database Storage & Schema Status Script
# Inspects database file size, WAL size, backups, free disk space, and schema version.

$ErrorActionPreference = "Stop"
$WorkspaceRoot = (Resolve-Path "$PSScriptRoot\..").Path
$ApiDir = Join-Path $WorkspaceRoot "services\api"
$BackendPython = Join-Path $ApiDir ".venv\Scripts\python.exe"

if (-not (Test-Path $BackendPython)) {
    Write-Host "[ERROR] Virtualenv Python not found at: $BackendPython" -ForegroundColor Red
    exit 1
}

$env:PYTHONPATH = $ApiDir
Push-Location $ApiDir
try {
    Write-Host "[AUTONOM] Querying storage status..." -ForegroundColor Cyan
    & $BackendPython -m app.db.cli status
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
