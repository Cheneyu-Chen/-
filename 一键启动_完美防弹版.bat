@echo off
chcp 65001 >nul
cd /d "%~dp0"
setlocal enabledelayedexpansion

set VENV_DIR=.venv_local
set RETRY_COUNT=0
set MAX_RETRIES=3

echo.
echo ============================================================================
echo Step 1/4: Checking Python environment...
echo ============================================================================
echo.

python --version 2>&1 | find /i "python" >nul
if errorlevel 1 goto python_not_found

echo [OK] Python found
echo.

echo Step 2/4: Preparing virtual environment...
echo.

if exist "!VENV_DIR!\Scripts\python.exe" (
    echo [OK] Virtual environment exists
) else (
    echo [*] Creating virtual environment...
    python -m venv !VENV_DIR!
    if errorlevel 1 goto venv_error
    echo [OK] Virtual environment created
)
echo.

echo Step 3/4: Installing dependencies (this may take several minutes)...
echo Please wait...
echo.

:retry_install
set /a RETRY_COUNT=!RETRY_COUNT! + 1

echo [Attempt !RETRY_COUNT!/!MAX_RETRIES!] Upgrading pip...
"!VENV_DIR!\Scripts\python.exe" -m pip install --upgrade pip 2>nul
if errorlevel 1 (
    if !RETRY_COUNT! LSS !MAX_RETRIES! (
        timeout /t 2 /nobreak
        goto retry_install
    )
    goto pip_error
)

echo [*] Installing required packages...
"!VENV_DIR!\Scripts\python.exe" -m pip install -r requirements.txt 2>nul
if errorlevel 1 (
    if !RETRY_COUNT! LSS !MAX_RETRIES! (
        timeout /t 2 /nobreak
        goto retry_install
    )
    goto install_error
)

echo [OK] Installation successful
echo.

echo Step 4/4: Starting application...
echo.
echo ============================================================================
echo.

"!VENV_DIR!\Scripts\python.exe" -m app.main
goto end

:: ============================================================================
:: Error handling
:: ============================================================================

:python_not_found
echo.
echo [ERROR] Python not found
echo.
echo Please:
echo   1. Download Python 3.10 or higher from: https://www.python.org/downloads/
echo   2. IMPORTANT: Check "Add python.exe to PATH" during installation
echo   3. Restart your computer
echo   4. Run this script again
echo.
pause
exit /b 1

:venv_error
echo.
echo [ERROR] Failed to create virtual environment
echo.
echo Try:
echo   1. Delete the .venv_local folder
echo   2. Run as Administrator
echo   3. Check available disk space
echo.
pause
exit /b 1

:pip_error
echo.
echo [ERROR] Failed to upgrade pip
echo.
echo Check:
echo   1. Your internet connection
echo   2. Disable VPN/Proxy and try again
echo   3. Firewall settings
echo.
pause
exit /b 1

:install_error
echo.
echo [ERROR] Failed to install dependencies
echo.
echo Try:
echo   1. Check your internet connection
echo   2. Delete the .venv_local folder
echo   3. Run as Administrator
echo   4. Disable antivirus software temporarily
echo.
pause
exit /b 1

:end
echo.
pause
exit /b