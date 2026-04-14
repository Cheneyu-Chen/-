# ============================================================================
# 声场与振动可视化平台 - PowerShell 启动脚本
# ============================================================================
# 使用方法：
# 右键点击此文件 -> 用PowerShell运行
# 或在PowerShell中运行: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process; .\一键启动.ps1
# ============================================================================

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

# 设置变量
$VenvDir = ".venv_local"
$PythonMinVersion = "3.10"
$MaxRetries = 3
$RetryCount = 0

# 颜色定义
$ErrorStyle = @{ ForegroundColor = "Red"; BackgroundColor = "Black" }
$SuccessStyle = @{ ForegroundColor = "Green"; BackgroundColor = "Black" }
$InfoStyle = @{ ForegroundColor = "Cyan"; BackgroundColor = "Black" }
$WarningStyle = @{ ForegroundColor = "Yellow"; BackgroundColor = "Black" }

Write-Host ""
Write-Host ("=" * 76) @SuccessStyle
Write-Host ""
Write-Host "  欢迎使用 声场与振动可视化虚拟仿真平台" @SuccessStyle
Write-Host ""
Write-Host ("=" * 76) @SuccessStyle
Write-Host ""

# 函数：检查Python
function Check-Python {
    try {
        $output = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[✓] 检测到 Python：$output" @SuccessStyle
            return $true
        }
    }
    catch {
        return $false
    }
    return $false
}

# 函数：创建虚拟环境
function Create-VirtualEnv {
    Write-Host "[步骤 2/4] 准备虚拟环境..." @InfoStyle
    Write-Host ""

    if (Test-Path "$VenvDir\Scripts\python.exe") {
        Write-Host "[✓] 虚拟环境已存在，跳过创建" @SuccessStyle
        Write-Host ""
        return $true
    }

    Write-Host "[*] 首次运行，正在为您创建虚拟环境..." @WarningStyle
    
    try {
        & python -m venv $VenvDir
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[✓] 虚拟环境创建成功" @SuccessStyle
            Write-Host ""
            return $true
        }
        else {
            Write-Host "[!] 虚拟环境创建失败" @ErrorStyle
            Write-Host ""
            return $false
        }
    }
    catch {
        Write-Host "[!] 虚拟环境创建异常：$_" @ErrorStyle
        Write-Host ""
        return $false
    }
}

# 函数：安装依赖
function Install-Dependencies {
    Write-Host "[步骤 3/4] 安装依赖库（可能需要几分钟）..." @InfoStyle
    Write-Host ""

    $pythonExe = "$VenvDir\Scripts\python.exe"
    $sources = @(
        "https://pypi.tuna.tsinghua.edu.cn/simple",  # 清华镜像
        "https://pypi.org/simple"                      # 官方源
    )

    foreach ($source in $sources) {
        Write-Host "[*] 尝试源：$source" @WarningStyle
        
        # 升级 pip
        & $pythonExe -m pip install --upgrade pip -i $source 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[!] pip 升级失败，尝试下一个源..." @WarningStyle
            continue
        }

        # 安装依赖
        & $pythonExe -m pip install -r requirements.txt -i $source 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[✓] 依赖库安装成功" @SuccessStyle
            Write-Host ""
            return $true
        }
        else {
            Write-Host "[!] 使用此源安装失败，尝试下一个源..." @WarningStyle
        }
    }

    Write-Host "[!] 所有源均安装失败" @ErrorStyle
    Write-Host ""
    return $false
}

# 函数：启动应用
function Start-Application {
    Write-Host "[步骤 4/4] 启动应用..." @InfoStyle
    Write-Host ""
    Write-Host ("=" * 76) @SuccessStyle
    Write-Host ""

    $pythonExe = "$VenvDir\Scripts\python.exe"
    
    try {
        & $pythonExe -m app.main
        if ($LASTEXITCODE -ne 0) {
            Write-Host ""
            Write-Host "[!] 应用运行出现错误" @ErrorStyle
        }
    }
    catch {
        Write-Host ""
        Write-Host "[!] 启动应用异常：$_" @ErrorStyle
    }
}

# 主逻辑
try {
    # 步骤 1：检查 Python
    Write-Host "[步骤 1/4] 检查 Python 运行环境..." @InfoStyle
    Write-Host ""

    if (-not (Check-Python)) {
        Write-Host "[!] 未找到 Python 或未添加到环境变量" @ErrorStyle
        Write-Host ""
        Write-Host "解决方案：" @WarningStyle
        Write-Host "  1. 访问 https://www.python.org/downloads/" @InfoStyle
        Write-Host "  2. 下载 Python 3.10 或更高版本" @InfoStyle
        Write-Host "  3. 安装时勾选 'Add python.exe to PATH' 选项" @InfoStyle
        Write-Host "  4. 安装完成后重新运行本脚本" @InfoStyle
        Write-Host ""
        Read-Host "按 Enter 键退出"
        exit 1
    }
    Write-Host ""

    # 步骤 2：创建虚拟环境
    if (-not (Create-VirtualEnv)) {
        Write-Host "错误处理：" @WarningStyle
        Write-Host "  1. 检查是否有管理员权限" @InfoStyle
        Write-Host "  2. 删除 .venv_local 文件夹后重试" @InfoStyle
        Write-Host "  3. 尝试以管理员身份运行 PowerShell" @InfoStyle
        Write-Host ""
        Read-Host "按 Enter 键退出"
        exit 1
    }

    # 步骤 3：安装依赖
    if (-not (Install-Dependencies)) {
        Write-Host "错误处理：" @WarningStyle
        Write-Host "  1. 检查网络连接" @InfoStyle
        Write-Host "  2. 尝试删除 .venv_local 文件夹后重试" @InfoStyle
        Write-Host "  3. 尝试以管理员身份运行 PowerShell" @InfoStyle
        Write-Host "  4. 若使用代理，请临时禁用后重试" @InfoStyle
        Write-Host ""
        Read-Host "按 Enter 键退出"
        exit 1
    }

    # 步骤 4：启动应用
    Start-Application
}
catch {
    Write-Host ""
    Write-Host "[!] 发生未预期的错误：$_" @ErrorStyle
    Write-Host ""
    Read-Host "按 Enter 键退出"
    exit 1
}
finally {
    Write-Host ""
    Read-Host "按 Enter 键退出"
}
