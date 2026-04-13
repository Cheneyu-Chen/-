@echo off
chcp 65001 >nul
echo 正在启动声场与振动可视化平台...

".venv_local\Scripts\python.exe" -m app.main
