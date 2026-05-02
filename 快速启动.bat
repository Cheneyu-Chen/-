@echo off
setlocal

cd /d "%~dp0"
set "PYTHON_EXE=%~dp0..\.venv_local\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Virtual environment was not found.
    echo Please run start script first: start-software.bat or the Chinese named launch bat.
    pause
    exit /b 1
)

echo Fast launching application...
"%PYTHON_EXE%" -m app.main

if errorlevel 1 (
    echo [ERROR] Application exited with an error.
    pause
)
