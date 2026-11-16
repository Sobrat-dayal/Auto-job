# AUTONOM — Database Restore Script
# Restores SQLite database from a specified backup with pre-restore snapshot and verification.

param(
    [Parameter(Position=0, Mandatory=$false)]
    [string]$BackupId,
    [switch]$Force
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
    Write-Host "[AUTONOM] Restoring database backup..." -ForegroundColor Cyan
    $argsList = @("-m", "app.db.cli", "restore")
    if ($BackupId) { $argsList += $BackupId }
    if ($Force) { $argsList += "--force" }
    & $BackendPython $argsList
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
