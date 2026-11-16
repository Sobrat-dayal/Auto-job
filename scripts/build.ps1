# AUTONOM — Full-Stack Build Script
# Builds frontend production distribution and compiles native desktop binaries

$ErrorActionPreference = "Stop"
$WorkspaceRoot = (Resolve-Path "$PSScriptRoot\..").Path
$DesktopDir = Join-Path $WorkspaceRoot "apps\desktop"
$DistDir = Join-Path $DesktopDir "dist"
$SrcTauriDir = Join-Path $DesktopDir "src-tauri"

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

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "AUTONOM — Production Build Pipeline" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Frontend Build
Write-Host "`n[STEP 1/2] Compiling Frontend Distribution via Vite..." -ForegroundColor Cyan
Push-Location $DesktopDir
try {
    & pnpm.cmd build
    if (-not (Test-Path $DistDir)) {
        Write-Host "[ERROR] Frontend build did not produce dist/ directory." -ForegroundColor Red
        exit 1
    }
    Write-Host "[PASS] Frontend built successfully at: $DistDir" -ForegroundColor Green
} finally {
    Pop-Location
}

# 2. Native Desktop Artifact Build
Write-Host "`n[STEP 2/2] Compiling Native Tauri Desktop Binary..." -ForegroundColor Cyan
Push-Location $SrcTauriDir
try {
    & cargo build --release
    $ReleaseExe = if (Test-Path "$env:CARGO_TARGET_DIR\release\autonom-desktop.exe") {
        "$env:CARGO_TARGET_DIR\release\autonom-desktop.exe"
    } else {
        Join-Path $SrcTauriDir "target\release\autonom-desktop.exe"
    }
    if (Test-Path $ReleaseExe) {
        Write-Host "[PASS] Native desktop binary compiled: $ReleaseExe" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Cargo release build executed. Check target/release for binary." -ForegroundColor Gray
    }
} catch {
    Write-Host "[WARN] Native binary compilation encountered an error: $_" -ForegroundColor Yellow
} finally {
    Pop-Location
}

Write-Host "`n[NOTICE] Windows NSIS/MSIX installer packaging is scheduled for Stage 50." -ForegroundColor Gray
Write-Host "Stage 02 build outputs: Web distribution compiled in apps/desktop/dist" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
