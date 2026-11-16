# AUTONOM — Database Backup Script
# Creates a consistent online backup using SQLite backup API with SHA-256 manifest.

param(
    [string]$Reason = "manual-powershell"
)

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
    Write-Host "[AUTONOM] Creating consistent online backup..." -ForegroundColor Cyan
    & $BackendPython -m app.db.cli backup --reason $Reason
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
