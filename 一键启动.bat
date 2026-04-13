@echo off
chcp 65001 >nul
echo 正在准备全新的运行环境...

set VENV_DIR=.venv_local

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [提示] 首次运行需要下载虚拟环境，请耐心等待...
    python -m venv %VENV_DIR%
)

echo [提示] 正在使用国内镜像源验证并安装依赖库，请不要关闭本窗口 (由于使用镜像加速，会有详细进度文字滚动)...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
"%VENV_DIR%\Scripts\python.exe" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [提示] 安装完成，正在启动声场与振动可视化平台...
echo.
"%VENV_DIR%\Scripts\python.exe" -m app.main

pause
