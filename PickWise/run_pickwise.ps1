# PickWise Dual Server Launcher
Write-Host "==========================================" -ForegroundColor Green
Write-Host "       Starting PickWise Application      " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend in background or separate window
Write-Host "Starting Flask Backend on http://127.0.0.1:5000..." -ForegroundColor Cyan
Start-Process -FilePath "py" -ArgumentList "-m", "backend.app" -WorkingDirectory $Root

Start-Sleep -Seconds 2

# 2. Start Frontend
Write-Host "Starting Vite React Frontend on http://localhost:5173..." -ForegroundColor Cyan
$FrontendDir = Join-Path $Root "frontend"
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory $FrontendDir

Write-Host "PickWise is launching! Open your browser at http://localhost:5173" -ForegroundColor Green
