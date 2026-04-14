# 声场与振动可视化虚拟仿真平台

一个用于全国大学生物理实验竞赛的 Python 桌面应用，提供声场与振动现象的可视化仿真。

## 🚀 快速开始

### Windows 用户

**最简单的方法：直接双击运行**

```
一键启动.bat        ← 首次使用：自动配置环境并启动
快速启动.bat        ← 后续使用：快速启动（需先运行一键启动.bat）
```

**如果上面不行，尝试：**
```
一键启动.ps1        ← PowerShell 版本（对于特殊网络环境）
```

### Mac / Linux 用户

```bash
# 1. 创建虚拟环境
python3 -m venv .venv

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
python -m app.main
```

---

## 📋 环境要求

- **Python 3.10 或更高版本**
- **网络连接**（首次启动需要下载依赖库）
- **至少 500MB 磁盘空间**

### 检查 Python 版本
```bash
python --version
```

### 安装 Python
访问 [https://www.python.org/downloads/](https://www.python.org/downloads/) 下载最新版本

**重要：安装时必须勾选 "Add Python to PATH"**

---

## 🛠️ 依赖库

| 库名 | 版本 | 用途 |
|------|------|------|
| PySide6 | ≥6.7 | GUI 框架 |
| numpy | ≥1.24 | 数值计算 |
| scipy | ≥1.10 | 科学计算 |
| matplotlib | ≥3.7 | 数据可视化 |

---

## 📁 项目结构

```
physics/
├── app/
│   ├── main.py                 # 应用入口
│   ├── main_window.py          # 主窗口
│   ├── theme.py                # 主题配置
│   ├── core/                   # 核心计算模块
│   │   ├── modes.py            # 模态分析
│   │   ├── resonance.py        # 共振分析
│   │   └── standing_wave.py    # 驻波分析
│   └── pages/                  # 页面模块
│       ├── home_page.py        # 首页
│       ├── standing_wave_page.py
│       ├── modes_page.py
│       ├── resonance_page.py
│       ├── compare_page.py
│       └── cases_page.py
├── requirements.txt            # 依赖库列表
├── 一键启动.bat               # Windows 自动配置启动脚本
├── 快速启动.bat               # Windows 快速启动脚本
├── 一键启动.ps1               # PowerShell 备用启动脚本
└── README.md                   # 本文件
```

---

## 🎯 主要功能模块

### 1. 首页 (Home)
- 应用介绍
- 功能导航
- 项目信息

### 2. 一维驻波仿真 (Standing Wave)
- 调节频率、阻尼、振幅
- 调节激励位置
- 实时波形显示
- 节点/腹点标注

### 3. 二维振动模态 (Modes)
- 典型二维模态展示
- 热图可视化
- 节点线显示
- 模态阶数切换

### 4. 共振扫描 (Resonance)
- 频率范围扫描
- 响应曲线生成
- 共振峰标注
- 参数设置

### 5. 教学案例 (Cases)
- 基本驻波形成
- 模态变化演示
- 阻尼影响对比
- 共振峰变化

### 6. 比较分析 (Compare)
- 参数对照分析
- 多场景对比
- 数据导出

---

## 🔧 常见问题

### Q: 双击脚本没反应
**A:** 尝试以管理员身份运行

### Q: 提示"未找到 Python"
**A:** 确认 Python 已安装并添加到 PATH，可能需要重启电脑

### Q: 依赖安装失败
**A:** 检查网络连接，如使用代理请临时关闭，然后删除 `.venv_local` 文件夹重试

### Q: 应用启动后立即关闭
**A:** 参考《启动说明.md》文件中的故障排查部分

### Q: 更多问题？
**A:** 参考项目根目录的 `启动说明.md` 文件

---

## ⌨️ 命令行手动启动

如果图形化启动脚本都不行，可以尝试命令行方式：

### Windows
```bash
# 打开 PowerShell 或命令提示符，切换到项目目录

# 创建虚拟环境
python -m venv .venv_local

# 激活虚拟环境
.venv_local\Scripts\activate

# 升级 pip
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 启动应用
python -m app.main
```

### Mac / Linux
```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 启动应用
python -m app.main
```

---

## 📝 文件说明

| 文件 | 说明 |
|------|------|
| `一键启动.bat` | 首次使用必选，自动创建虚拟环境并安装依赖 |
| `快速启动.bat` | 环境配置完成后快速启动 |
| `一键启动.ps1` | PowerShell 版本，适用于特殊网络环境 |
| `requirements.txt` | Python 依赖库列表 |
| `启动说明.md` | 详细的启动和故障排查指南 |

---

## 🌟 功能特点

- ✓ **全中文界面** - 避免乱码，完全本地化
- ✓ **自动环境配置** - 一键启动，无需手动操作
- ✓ **美观现代 UI** - 深色主题，适合演示
- ✓ **实时交互** - 参数联动，流畅体验
- ✓ **教学友好** - 详细注解，易于理解
- ✓ **完整演示** - 涵盖多个物理现象

---

## 💡 使用建议

1. **首次使用**：运行 `一键启动.bat` 完整配置环境
2. **后续使用**：运行 `快速启动.bat` 快速启动应用
3. **问题排查**：参考 `启动说明.md` 中的常见问题
4. **手动启动**：参考本文档的"命令行手动启动"章节

---

## 📞 技术支持

遇到问题时，请提供以下信息：
- 操作系统（Windows 10/11、macOS、Linux 发行版）
- Python 版本（运行 `python --version`）
- 完整的错误信息截图
- 网络环境说明（是否使用代理）

---

## 📄 许可证

本项目用于全国大学生物理实验竞赛（创新）自选题2"教学资源和虚仿"

---

## 🎓 项目由以下技术栈支持

- **Python** - 核心语言
- **PySide6** - GUI 框架
- **NumPy & SciPy** - 科学计算
- **Matplotlib** - 数据可视化

---

祝您使用愉快！如有任何问题，请参考项目文档或联系技术支持。

🚀 Happy Physics Simulation! 🚀
