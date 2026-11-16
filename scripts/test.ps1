# AUTONOM — Unified Test Execution Script
# Runs frontend tests (Vitest), backend tests (pytest), and native Rust tests (cargo test)

$ErrorActionPreference = "Continue"
$WorkspaceRoot = (Resolve-Path "$PSScriptRoot\..").Path
$ApiDir = Join-Path $WorkspaceRoot "services\api"
$DesktopDir = Join-Path $WorkspaceRoot "apps\desktop"
$SrcTauriDir = Join-Path $DesktopDir "src-tauri"

# Ensure PATH includes Cargo and MinGW gcc if present
if (Test-Path "$env:USERPROFILE\.cargo\bin") {
    $env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
}
if (Test-Path "C:\Strawberry\c\bin") {
    $env:PATH = "C:\Strawberry\c\bin;$env:PATH"
}
if (-not $env:CARGO_TARGET_DIR) {
    if (Test-Path "E:\proooo\target") {
        $env:CARGO_TARGET_DIR = "E:\proooo\target"
    } elseif ($WorkspaceRoot -match '\s') {
        $fallbackTarget = "$env:TEMP\autonom_target"
        if (-not (Test-Path $fallbackTarget)) { New-Item -ItemType Directory -Path $fallbackTarget -Force | Out-Null }
        $env:CARGO_TARGET_DIR = $fallbackTarget
    }
}

$FailedSuites = @()

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "AUTONOM — Running Full-Stack Test Suites" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Frontend Tests (Vitest)
Write-Host "`n[SUITE 1/3] Running Frontend Vitest Tests..." -ForegroundColor Cyan
Push-Location $DesktopDir
try {
    & pnpm.cmd test
    if ($LASTEXITCODE -ne 0) { $FailedSuites += "Frontend Vitest" }
} catch {
    $FailedSuites += "Frontend Vitest"
} finally {
    Pop-Location
}

# 2. Backend Tests (pytest)
Write-Host "`n[SUITE 2/3] Running Backend FastAPI Tests..." -ForegroundColor Cyan
$BackendPython = Join-Path $ApiDir ".venv\Scripts\python.exe"
if (Test-Path $BackendPython) {
    Push-Location $ApiDir
    try {
        & $BackendPython -m pytest tests/
        if ($LASTEXITCODE -ne 0) { $FailedSuites += "Backend pytest" }
    } catch {
        $FailedSuites += "Backend pytest"
    } finally {
        Pop-Location
    }
} else {
    Write-Host "[WARN] Backend Python environment not found in $ApiDir." -ForegroundColor Yellow
    $FailedSuites += "Backend pytest (missing venv)"
}

# 3. Rust Native Tests (cargo test)
Write-Host "`n[SUITE 3/3] Running Native Rust Tests..." -ForegroundColor Cyan
if (Test-Path $SrcTauriDir) {
    Push-Location $SrcTauriDir
    try {
        & cargo test
        if ($LASTEXITCODE -ne 0) { $FailedSuites += "Native Rust" }
    } catch {
        $FailedSuites += "Native Rust"
    } finally {
        Pop-Location
    }
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
if ($FailedSuites.Count -eq 0) {
    Write-Host "ALL TEST SUITES PASSED SUCCESSFULLY!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAILED SUITES: $($FailedSuites -join ', ')" -ForegroundColor Red
    exit 1
}
