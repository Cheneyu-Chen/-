@echo off
setlocal

cd /d "%~dp0"

set "VENV_DIR=%~dp0..\.venv_local"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "PIP_EXE=%VENV_DIR%\Scripts\pip.exe"
set "LOCAL_TEMP=%~dp0.pip_temp"

if not exist "%LOCAL_TEMP%" mkdir "%LOCAL_TEMP%"
set "TEMP=%LOCAL_TEMP%"
set "TMP=%LOCAL_TEMP%"

echo Starting Sound and Vibration Simulation Platform...
echo Project dir: %CD%
echo Python: %PYTHON_EXE%
echo.

if not exist "%PYTHON_EXE%" (
    echo [INFO] Virtual environment not found. Creating it now...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

"%PYTHON_EXE%" -c "import PySide6, numpy, scipy, matplotlib" >nul 2>nul
if errorlevel 1 (
    echo [INFO] Dependencies are missing. Installing requirements...
    "%PYTHON_EXE%" -m pip install --upgrade pip
    "%PIP_EXE%" install -r requirements.txt -i https://pypi.org/simple
    if errorlevel 1 (
        echo [INFO] pypi.org failed. Trying Tsinghua mirror...
        "%PIP_EXE%" install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    )
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo [INFO] Launching application...
"%PYTHON_EXE%" -m app.main

if errorlevel 1 (
    echo [ERROR] Application exited with an error.
)
pause
