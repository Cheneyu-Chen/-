@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo 正在启动声场与振动可视化平台...
echo.

REM 检查虚拟环境是否存在
if not exist ".venv_local\Scripts\python.exe" (
    echo [!] 虚拟环境未找到！
    echo.
    echo 请先运行 "一键启动.bat" 进行环境配置
    echo.
    pause
    exit /b 1
)

".venv_local\Scripts\python.exe" -m app.main
pause
