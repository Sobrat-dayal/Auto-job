# AUTONOM — Full-Stack Development Orchestration Script
# Launches the FastAPI backend service and Tauri/Vite desktop development application

$ErrorActionPreference = "Stop"
$WorkspaceRoot = (Resolve-Path "$PSScriptRoot\..").Path
$ApiDir = Join-Path $WorkspaceRoot "services\api"
$DesktopDir = Join-Path $WorkspaceRoot "apps\desktop"

# Ensure cargo is on PATH
if (Test-Path "$env:USERPROFILE\.cargo\bin") {
    $env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
}

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "AUTONOM — Launching Development Environment" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Port conflict check (8765 for Backend, 5173 for Vite)
function Check-Port($Port) {
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        Write-Host "[WARN] Port $Port is currently in use by process PID $($conn.OwningProcess)." -ForegroundColor Yellow
        return $false
    }
    return $true
}

Check-Port 8765
Check-Port 5173

# 2. Python Backend Launcher
$BackendPython = Join-Path $ApiDir ".venv\Scripts\python.exe"
if (-not (Test-Path $BackendPython)) {
    Write-Host "[ERROR] Python virtual environment not found in $ApiDir. Run scripts/setup.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "[STEP 1/2] Starting Python FastAPI Backend on http://127.0.0.1:8765..." -ForegroundColor Cyan
$backendProc = Start-Process -FilePath $BackendPython `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--app-dir", $ApiDir, "--host", "127.0.0.1", "--port", "8765", "--reload" `
    -PassThru -NoNewWindow

Start-Sleep -Seconds 2

# 3. Frontend / Desktop Launcher
Write-Host "[STEP 2/2] Starting Tauri Desktop Development Environment..." -ForegroundColor Cyan

try {
    Push-Location $DesktopDir
    # Run Tauri Dev (starts Vite and loads WebView2)
    & pnpm.cmd tauri dev
} finally {
    Pop-Location
    Write-Host "`n[CLEANUP] Stopping background processes..." -ForegroundColor Gray
    if ($backendProc -and -not $backendProc.HasExited) {
        Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
        Write-Host "[CLEANUP] Backend process (PID $($backendProc.Id)) stopped." -ForegroundColor Green
    }
}
