from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.widgets.common import make_card, make_metric, muted_label, two_col_row


class HomePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        hero, hero_layout = make_card()
        title = QLabel("声场与振动可视化虚拟仿真平台")
        title.setObjectName("TitleLabel")
        subtitle = QLabel(
            "面向大学物理、机械振动和声学实验教学，平台用可调参数、动态图像和教学案例把"
            "一维驻波、二维膜模态、克拉尼图形、共振扫描、声子晶体带隙和工程应用连接起来。"
        )
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setWordWrap(True)
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        layout.addWidget(hero)

        metrics = QWidget()
        metrics_layout = QVBoxLayout(metrics)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(12)
        metrics_layout.addWidget(two_col_row(
            make_metric("产品定位", "教学 + 竞赛", "解决真实实验场地、器材、频率扫描和图案复现实验成本高的问题。"),
            make_metric("技术路线", "Python 自主实现", "NumPy/SciPy 负责数值模型，Matplotlib 负责图像，PySide6 负责交互界面。"),
        ))
        metrics_layout.addWidget(two_col_row(
            make_metric("内容层次", "基础到前沿", "一维驻波 -> 二维模态 -> 克拉尼图形 -> 声子晶体/超材料。"),
            make_metric("展示方式", "公式-参数-图像", "每个案例都给出物理公式、可调参数、图像结果和解释文字。"),
        ))
        layout.addWidget(metrics)

        roadmap, roadmap_layout = make_card("平台主要内容")
        roadmap_layout.addWidget(muted_label(
            "1. 一维驻波：改变边界、频率、阻尼和激励位置，验证波节与本征频率 fₙ 的关系。\n"
            "2. 二维模态：选择矩形、圆形、三角形几何，显示振幅热图、节点线与相对频率。\n"
            "3. 共振扫描：绘制受迫振动幅频响应，自动识别共振峰，分析阻尼与 Q 值。\n"
            "4. 进阶声学：展示干涉、衍射、声子晶体带隙和亥姆霍兹局域共振吸声。\n"
            "5. 教学案例：借鉴优秀作品的案例化展示方式，一键跳转到预设参数。\n"
            "6. 实验对比：整理真实照片、仿真热图、理论节点线和误差分析，服务竞赛报告。"
        ))
        layout.addWidget(roadmap)

        report, report_layout = make_card("竞赛报告建议目录")
        report_layout.addWidget(muted_label(
            "选题背景 -> 产品定位 -> 开发环境与工具链 -> 平台设计流程 -> 物理原理 -> "
            "数值模型与边界条件 -> 程序功能与界面说明 -> 教学案例展示 -> 与大学物理课程联系 -> "
            "实验讨论、总结、分工与参考文献。"
        ))
        layout.addWidget(report)
        layout.addStretch(1)
