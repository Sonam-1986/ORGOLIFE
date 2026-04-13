@echo off
REM =========================================================================
REM  OrgoLife - ONE-CLICK STARTUP SCRIPT (Windows)
REM  Run this file to start both Backend and Frontend
REM =========================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo   ====== OrgoLife - Organ Donation Platform ======
echo.

REM ── Python check ──────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Python not found. Install from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo   [OK] Python !PYTHON_VERSION!

REM ── Virtual environment ───────────────────────────────────────
if not exist "venv" (
    echo   [*] Creating virtual environment...
    python -m venv venv
    echo   [OK] Virtual environment created
)

echo   [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM ── Install dependencies ───────────────────────────────────────
echo   [*] Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -q -r requirements.txt
echo   [OK] Dependencies installed

REM ── Setup .env file ──────────────────────────────────────────
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo   [OK] Created .env from .env.example
    )
)

echo.
echo   ====== Starting Application ======
echo   Backend: http://localhost:8000
echo   API Docs: http://localhost:8000/api/docs
echo   Frontend: http://localhost:8000
echo.

REM ── Start Backend ──────────────────────────────────────────────
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo   [!] Application stopped
pause
