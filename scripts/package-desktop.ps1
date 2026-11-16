# AUTONOM — Desktop Packaging Pipeline
# Builds the frontend, packages the Python backend sidecar, and builds the native Tauri 2 desktop binary.

$ErrorActionPreference = "Stop"
$WorkspaceRoot = (Resolve-Path "$PSScriptRoot\..").Path
$DesktopDir = Join-Path $WorkspaceRoot "apps\desktop"
$SrcTauriDir = Join-Path $DesktopDir "src-tauri"
$DistDir = Join-Path $DesktopDir "dist"
$BinDir = Join-Path $SrcTauriDir "bin"

if (Test-Path "$env:USERPROFILE\.cargo\bin") {
    $env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
}
if (Test-Path "C:\Strawberry\c\bin") {
    $env:PATH = "C:\Strawberry\c\bin;$env:PATH"
}
if (-not $env:CARGO_TARGET_DIR) {
    if (Test-Path "E:\proooo\target") {
        $env:CARGO_TARGET_DIR = "E:\proooo\target"
    } else {
        $env:CARGO_TARGET_DIR = "$env:TEMP\autonom_target"
    }
}

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "AUTONOM — Stage 05 Desktop Packaging Pipeline" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Package Backend Sidecar
Write-Host "`n[STEP 1/3] Packaging Python Backend Sidecar..." -ForegroundColor Cyan
$SidecarMsvc = Join-Path $BinDir "autonom-api-x86_64-pc-windows-msvc.exe"
if (-not (Test-Path $SidecarMsvc)) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot\package-backend.ps1"
} else {
    Write-Host "  Sidecar binary already present: $SidecarMsvc" -ForegroundColor Green
}

# 2. Compile Web Frontend
Write-Host "`n[STEP 2/3] Building Production Web Frontend..." -ForegroundColor Cyan
Push-Location $DesktopDir
try {
    & pnpm.cmd build
    if (-not (Test-Path $DistDir)) {
        Write-Host "[ERROR] Frontend build failed — dist directory not found." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Frontend assets generated at: $DistDir" -ForegroundColor Green
} finally {
    Pop-Location
}

# 3. Compile Native Tauri Binary
Write-Host "`n[STEP 3/3] Compiling Native Tauri Desktop Application..." -ForegroundColor Cyan
Push-Location $SrcTauriDir
try {
    & cargo build --release
    $ReleaseExe = Join-Path $env:CARGO_TARGET_DIR "release\autonom-desktop.exe"
    if (-not (Test-Path $ReleaseExe)) {
        $ReleaseExe = Join-Path $SrcTauriDir "target\release\autonom-desktop.exe"
    }

    if (Test-Path $ReleaseExe) {
        $SizeMB = [math]::Round((Get-Item $ReleaseExe).Length / 1MB, 2)
        Write-Host "`n[SUCCESS] Native Desktop Application Built!" -ForegroundColor Green
        Write-Host "  Desktop Binary: $ReleaseExe ($SizeMB MB)" -ForegroundColor Gray
        Write-Host "  Sidecar Binary: $SidecarMsvc" -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] Release binary not found at expected location." -ForegroundColor Red
        exit 1
    }
} finally {
    Pop-Location
}

Write-Host "================================================================================" -ForegroundColor Cyan
