# AUTONOM — Database Migration Script
# Applies pending Alembic migrations to head.

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
    Write-Host "[AUTONOM] Applying database migrations..." -ForegroundColor Cyan
    & $BackendPython -m app.db.cli migrate
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
