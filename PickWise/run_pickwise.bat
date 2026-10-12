@echo off
title PickWise Launcher
echo ==========================================
echo        Starting PickWise Application      
echo ==========================================

cd /d "%~dp0"
echo Starting Backend on http://127.0.0.1:5000...
start "PickWise Backend" py -m backend.app

timeout /t 2 /nobreak >nul

echo Starting Frontend on http://localhost:5173...
cd frontend
start "PickWise Frontend" npm run dev

echo Both servers started! Open your browser at http://localhost:5173
pause
