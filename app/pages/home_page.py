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
            "面向大学物理与工程振动教学，平台把一维驻波、二维薄板/膜本征振动、"
            "克拉尼图形、共振峰扫描和真实应用案例组织成可调参数、可看图像、可解释公式的仿真实验。"
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
            make_metric("基础层", "一维驻波", "fₙ = n v / 2L，观察波节、波腹、边界条件和激励位置。"),
            make_metric("进阶层", "二维模态", "矩形、圆形与三角形膜的振型热图、节点线和相对本征频率。"),
        ))
        metrics_layout.addWidget(two_col_row(
            make_metric("经典层", "克拉尼图形", "用节点线解释沙粒聚集图案，建立频率和模态阶数的对应。"),
            make_metric("应用层", "乐器 / MEMS", "连接共鸣箱音色、谐振传感器灵敏度与抗震声学超材料。"),
        ))
        layout.addWidget(metrics)

        roadmap, roadmap_layout = make_card("内容结构")
        roadmap_layout.addWidget(muted_label(
            "1. 一维驻波：改变边界、频率、阻尼和激励位置，验证波节与本征频率关系。\n"
            "2. 二维薄板/膜：选择几何形状和模态阶数，显示振幅热图、节点线与相对频率。\n"
            "3. 共振扫描：自动绘制响应曲线，寻找共振峰，直观看到阻尼对峰值和带宽的影响。\n"
            "4. 应用案例：从克拉尼图形延伸到乐器共鸣箱、MEMS 谐振器和声学超材料。\n"
            "5. 实验对比：给出实验照片、仿真图和理论节点线的对比方法，便于写入竞赛报告。"
        ))
        layout.addWidget(roadmap)

        report, report_layout = make_card("竞赛报告建议目录")
        report_layout.addWidget(muted_label(
            "选题背景 -> 产品定位 -> 开发环境与工具链 -> 平台架构 -> 物理原理 -> "
            "数值模型与边界条件 -> 功能界面说明 -> 实验案例展示 -> 与大学物理课程联系 -> "
            "讨论总结、分工与参考文献。"
        ))
        layout.addWidget(report)
        layout.addStretch(1)
