@echo off
title High Value Sales - 3D Intelligence Platform
echo ========================================================
echo   High Value Sales - Futuristic 3D Intelligence Platform
echo ========================================================
echo.
echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

echo Starting Flask Application on http://127.0.0.1:5000 ...
echo Press Ctrl+C to terminate the server.
echo.
python app.py
pause
