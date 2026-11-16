# AUTONOM — Database Initialization Script
# Initializes the SQLite database schema and tables.

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
    Write-Host "[AUTONOM] Initializing database schema..." -ForegroundColor Cyan
    & $BackendPython -m app.db.cli init
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
