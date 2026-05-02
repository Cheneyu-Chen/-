@echo off
chcp 65001 >nul
echo 正在检查依赖...

.venv_local\Scripts\python.exe -c "import PySide6, numpy, scipy, matplotlib" 2>nul
if errorlevel 1 (
    echo 缺少依赖库，正在安装...
    .venv_local\Scripts\python.exe -m pip install --upgrade pip -q
    .venv_local\Scripts\python.exe -m pip install -r requirements.txt -q
)

echo.
echo 启动声场与振动可视化虚拟仿真平台...
echo.
.venv_local\Scripts\python.exe -m app.main

pause
