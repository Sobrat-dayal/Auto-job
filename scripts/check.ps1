# AUTONOM — Full Quality & Lint Check Script
# Enforces TypeScript typing, ESLint, Prettier, Ruff, Pytest, Cargo fmt, Clippy, and Stage Validation

$ErrorActionPreference = "Continue"
$WorkspaceRoot = (Resolve-Path "$PSScriptRoot\..").Path
$ApiDir = Join-Path $WorkspaceRoot "services\api"
$SrcTauriDir = Join-Path $WorkspaceRoot "apps\desktop\src-tauri"

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

$FailedChecks = @()

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "AUTONOM — Executing Quality & Validation Checks" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Stage 01 Architectural Validation
Write-Host "`n[CHECK 1/7] Validating Architectural Specifications..." -ForegroundColor Cyan
$BackendPython = Join-Path $ApiDir ".venv\Scripts\python.exe"
if (Test-Path $BackendPython) {
    & $BackendPython "$WorkspaceRoot\scripts\validate_stage01.py"
    if ($LASTEXITCODE -ne 0) { $FailedChecks += "Architecture Validation" }
}

# 2. TypeScript Compilation Check
Write-Host "`n[CHECK 2/7] Running TypeScript Compiler (tsc --noEmit)..." -ForegroundColor Cyan
Push-Location $WorkspaceRoot
try {
    & pnpm.cmd typecheck
    if ($LASTEXITCODE -ne 0) { $FailedChecks += "TypeScript Check" }
} finally {
    Pop-Location
}

# 3. Code Formatting Check (Prettier)
Write-Host "`n[CHECK 3/7] Running Prettier Format Check..." -ForegroundColor Cyan
Push-Location $WorkspaceRoot
try {
    & pnpm.cmd format:check
    if ($LASTEXITCODE -ne 0) { $FailedChecks += "Prettier Check" }
} finally {
    Pop-Location
}

# 4. Python Linting (Ruff)
Write-Host "`n[CHECK 4/7] Running Ruff Linter on services/api..." -ForegroundColor Cyan
$RuffExe = Join-Path $ApiDir ".venv\Scripts\ruff.exe"
if (Test-Path $RuffExe) {
    Push-Location $ApiDir
    try {
        & $RuffExe check .
        if ($LASTEXITCODE -ne 0) { $FailedChecks += "Ruff Lint" }
    } finally {
        Pop-Location
    }
}

# 5. Python Unit Tests (pytest)
Write-Host "`n[CHECK 5/7] Running Pytest Unit Tests on services/api..." -ForegroundColor Cyan
if (Test-Path $BackendPython) {
    Push-Location $ApiDir
    try {
        & $BackendPython -m pytest tests/
        if ($LASTEXITCODE -ne 0) { $FailedChecks += "Pytest Unit Tests" }
    } finally {
        Pop-Location
    }
}

# 6. Rust Formatting (cargo fmt)
Write-Host "`n[CHECK 6/7] Checking Rust Code Formatting (cargo fmt)..." -ForegroundColor Cyan
if (Test-Path $SrcTauriDir) {
    Push-Location $SrcTauriDir
    try {
        & cargo fmt --all -- --check
        if ($LASTEXITCODE -ne 0) { $FailedChecks += "Cargo Fmt" }
    } catch {
        Write-Host "[WARN] Cargo fmt failed or not available." -ForegroundColor Yellow
        $FailedChecks += "Cargo Fmt"
    } finally {
        Pop-Location
    }
}

# 7. Rust Linting (cargo clippy)
Write-Host "`n[CHECK 7/7] Checking Rust Code with Clippy (cargo clippy)..." -ForegroundColor Cyan
if (Test-Path $SrcTauriDir) {
    Push-Location $SrcTauriDir
    try {
        & cargo clippy --all-targets -- -D warnings
        if ($LASTEXITCODE -ne 0) { $FailedChecks += "Cargo Clippy" }
    } catch {
        Write-Host "[WARN] Cargo clippy check failed or not available." -ForegroundColor Yellow
        $FailedChecks += "Cargo Clippy"
    } finally {
        Pop-Location
    }
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
if ($FailedChecks.Count -eq 0) {
    Write-Host "ALL QUALITY CHECKS PASSED SUCCESSFULLY!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAILED CHECKS: $($FailedChecks -join ', ')" -ForegroundColor Red
    exit 1
}
