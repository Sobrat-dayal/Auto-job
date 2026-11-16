# AUTONOM — Windows Development Environment Setup Script
# Verifies prerequisites, installs pnpm packages, and initializes Python virtual environment

$ErrorActionPreference = "Stop"
$WorkspaceRoot = (Resolve-Path "$PSScriptRoot\..").Path

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "AUTONOM — Windows 11 Development Environment Setup" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Detect Architecture & OS
$Arch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
$OsDesc = [System.Runtime.InteropServices.RuntimeInformation]::OSDescription
Write-Host "[INFO] Detected OS: $OsDesc ($Arch)" -ForegroundColor Gray

# Ensure cargo bin is in PATH for current session
if (Test-Path "$env:USERPROFILE\.cargo\bin") {
    $env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
}

# 2. Check Prerequisites
function Check-Command($CmdName, $Label) {
    $cmd = Get-Command $CmdName -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Host "[PASS] $Label is installed: $($cmd.Source)" -ForegroundColor Green
        return $true
    } else {
        Write-Host "[WARN] $Label is NOT found on PATH." -ForegroundColor Yellow
        return $false
    }
}

$hasNode = Check-Command "node" "Node.js"
$hasPnpm = Check-Command "pnpm.cmd" "pnpm (or pnpm.cmd)"
if (-not $hasPnpm) { $hasPnpm = Check-Command "pnpm" "pnpm" }
$hasPython = Check-Command "python" "Python"
$hasUv = Check-Command "uv" "uv package manager"
$hasCargo = Check-Command "cargo" "Rust Cargo"
$hasRustc = Check-Command "rustc" "Rust Compiler"

# 3. Check WebView2
$wv2Path = "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-6E3A4A60F352}"
$hasWv2 = Test-Path $wv2Path
if ($hasWv2) {
    Write-Host "[PASS] Microsoft Edge WebView2 runtime detected." -ForegroundColor Green
} else {
    Write-Host "[INFO] Standard Windows 11 includes WebView2 by default." -ForegroundColor Gray
}

# 4. Install JavaScript Monorepo Dependencies
if ($hasPnpm) {
    Write-Host "`n[STEP] Installing pnpm workspace dependencies..." -ForegroundColor Cyan
    Push-Location $WorkspaceRoot
    try {
        & pnpm.cmd install
        Write-Host "[PASS] pnpm dependencies installed successfully." -ForegroundColor Green
    } finally {
        Pop-Location
    }
} else {
    Write-Host "[ERROR] pnpm is required. Install via: npm install -g pnpm" -ForegroundColor Red
}

# 5. Initialize Python Virtual Environment for services/api
$ApiDir = Join-Path $WorkspaceRoot "services\api"
if ($hasUv -and (Test-Path $ApiDir)) {
    Write-Host "`n[STEP] Setting up Python virtual environment in services/api via uv..." -ForegroundColor Cyan
    Push-Location $ApiDir
    try {
        if (-not (Test-Path ".venv")) {
            & uv venv
        }
        & uv pip install -e ".[dev]"
        Write-Host "[PASS] Python virtual environment ready." -ForegroundColor Green
    } finally {
        Pop-Location
    }
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "Setup Completed! Run scripts/dev.ps1 to start the development environment." -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
