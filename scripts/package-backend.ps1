# AUTONOM — Backend Sidecar Packaging Script
# Compiles Python FastAPI backend into a standalone Windows executable for Tauri 2 sidecar bundling.

$ErrorActionPreference = "Stop"
$WorkspaceRoot = (Resolve-Path "$PSScriptRoot\..").Path
$ApiDir = Join-Path $WorkspaceRoot "services\api"
$PyInstallerExe = Join-Path $ApiDir ".venv\Scripts\pyinstaller.exe"
$TauriBinDir = Join-Path $WorkspaceRoot "apps\desktop\src-tauri\bin"

if (-not (Test-Path $PyInstallerExe)) {
    Write-Host "[ERROR] PyInstaller not found at $PyInstallerExe" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $TauriBinDir)) {
    New-Item -ItemType Directory -Path $TauriBinDir -Force | Out-Null
}

$DistDir = Join-Path $ApiDir "dist"
$BuildDir = Join-Path $ApiDir "build"
$EntryScript = Join-Path $ApiDir "app\server_entry.py"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "AUTONOM — Packaging Python Backend Sidecar via PyInstaller" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

Push-Location $ApiDir
try {
    $pyinstallerArgs = @(
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name", "autonom-api",
        "--paths", $ApiDir,
        "--add-data", "$ApiDir\alembic;alembic",
        "--add-data", "$ApiDir\alembic.ini;.",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops.asyncio",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.http.h11_impl",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespans.on",
        "--hidden-import", "sqlalchemy.dialects.sqlite.aiosqlite",
        "--hidden-import", "aiosqlite",
        "--hidden-import", "greenlet",
        "--collect-all", "aiosqlite",
        "--collect-all", "alembic",
        "--collect-all", "app",
        "--collect-all", "cryptography",
        "--collect-all", "pydantic",
        "--collect-all", "pydantic_core",
        "--distpath", $DistDir,
        "--workpath", $BuildDir,
        $EntryScript
    )

    & $PyInstallerExe $pyinstallerArgs

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] PyInstaller compilation failed with code $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }

    $BuiltExe = Join-Path $DistDir "autonom-api.exe"
    if (-not (Test-Path $BuiltExe)) {
        Write-Host "[ERROR] Expected binary not found at $BuiltExe" -ForegroundColor Red
        exit 1
    }

    # Copy to Tauri sidecar binaries with target triples
    $TripleMsvc = Join-Path $TauriBinDir "autonom-api-x86_64-pc-windows-msvc.exe"
    $TripleGnu = Join-Path $TauriBinDir "autonom-api-x86_64-pc-windows-gnu.exe"

    Copy-Item $BuiltExe $TripleMsvc -Force
    Copy-Item $BuiltExe $TripleGnu -Force

    $SizeMB = [math]::Round(((Get-Item $BuiltExe).Length / 1MB), 2)
    Write-Host "`n[SUCCESS] Backend sidecar successfully packaged!" -ForegroundColor Green
    Write-Host "  Binary:       $BuiltExe ($SizeMB MB)"
    Write-Host "  Sidecar MSVC: $TripleMsvc"
    Write-Host "  Sidecar GNU:  $TripleGnu"
} finally {
    Pop-Location
}
