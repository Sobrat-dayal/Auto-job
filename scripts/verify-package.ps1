# AUTONOM — Package Verification Script
# Verifies frontend dist, backend sidecar binary, native desktop binary, and sidecar execution.

$ErrorActionPreference = "Stop"
$WorkspaceRoot = (Resolve-Path "$PSScriptRoot\..").Path
$DesktopDir = Join-Path $WorkspaceRoot "apps\desktop"
$SrcTauriDir = Join-Path $DesktopDir "src-tauri"
$DistHtml = Join-Path $DesktopDir "dist\index.html"
$BinDir = Join-Path $SrcTauriDir "bin"
$SidecarExe = Join-Path $BinDir "autonom-api-x86_64-pc-windows-msvc.exe"

$TargetDir = if ($env:CARGO_TARGET_DIR) { $env:CARGO_TARGET_DIR } else { "E:\proooo\target" }
$DesktopExe = Join-Path $TargetDir "release\autonom-desktop.exe"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "AUTONOM — Package Verification" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

$Passed = $true

# 1. Verify Frontend Dist
Write-Host "`n[CHECK 1/4] Verifying Frontend Distribution..." -ForegroundColor Cyan
if (Test-Path $DistHtml) {
    $HtmlSize = (Get-Item $DistHtml).Length
    Write-Host "  [PASS] Frontend dist found ($DistHtml, $HtmlSize bytes)" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Frontend dist not found: $DistHtml" -ForegroundColor Red
    $Passed = $false
}

# 2. Verify Backend Sidecar Binary
Write-Host "`n[CHECK 2/4] Verifying Backend Sidecar Executable..." -ForegroundColor Cyan
if (Test-Path $SidecarExe) {
    $SidecarSizeMB = [math]::Round((Get-Item $SidecarExe).Length / 1MB, 2)
    Write-Host "  [PASS] Sidecar binary found ($SidecarExe, $SidecarSizeMB MB)" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Sidecar binary not found: $SidecarExe" -ForegroundColor Red
    $Passed = $false
}

# 3. Verify Native Desktop Executable
Write-Host "`n[CHECK 3/4] Verifying Native Desktop Executable..." -ForegroundColor Cyan
if (Test-Path $DesktopExe) {
    $DesktopSizeMB = [math]::Round((Get-Item $DesktopExe).Length / 1MB, 2)
    Write-Host "  [PASS] Desktop binary found ($DesktopExe, $DesktopSizeMB MB)" -ForegroundColor Green
} else {
    Write-Host "  [INFO] Desktop binary not yet compiled at: $DesktopExe" -ForegroundColor Yellow
}

# 4. Live Health Check on Sidecar Executable
Write-Host "`n[CHECK 4/4] Testing Standalone Sidecar Boot & Health..." -ForegroundColor Cyan
if (Test-Path $SidecarExe) {
    $TestPort = 8798
    $ApiKey = "verify-token-12345"
    Write-Host "  Launching sidecar on 127.0.0.1:$TestPort..." -ForegroundColor Gray

    $proc = Start-Process -FilePath $SidecarExe -ArgumentList "--host 127.0.0.1 --port $TestPort --api-key $ApiKey --log-level error" -PassThru -WindowStyle Hidden
    try {
        $Ready = $false
        for ($i = 0; $i -lt 20; $i++) {
            Start-Sleep -Milliseconds 500
            try {
                $response = Invoke-RestMethod -Uri "http://127.0.0.1:$TestPort/api/v1/ready" -Method Get -TimeoutSec 2
                if ($response.ready -eq $true -or $response.status -eq "ready" -or $response.status -eq "Ready") {
                    $Ready = $true
                    break
                }
            } catch {
                # Waiting for boot
            }
        }

        if ($Ready) {
            Write-Host "  [PASS] Packaged sidecar booted and returned Ready on 127.0.0.1:$TestPort" -ForegroundColor Green
        } else {
            Write-Host "  [FAIL] Sidecar did not report ready within timeout." -ForegroundColor Red
            $Passed = $false
        }
    } finally {
        if (-not $proc.HasExited) {
            Stop-Process -Id $proc.Id -Force
            Write-Host "  Sidecar process terminated cleanly." -ForegroundColor Gray
        }
    }
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
if ($Passed) {
    Write-Host "[SUCCESS] Package verification completed successfully!" -ForegroundColor Green
} else {
    Write-Host "[WARN] Package verification found warnings or missing components." -ForegroundColor Yellow
}
Write-Host "================================================================================" -ForegroundColor Cyan
