from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.widgets.common import make_card, make_metric, muted_label, two_col_row


class CompetitionPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title_card, title_layout = make_card()
        title = QLabel("作品总览")
        title.setObjectName("TitleLabel")
        subtitle = QLabel(
            "本页汇总平台的物理内容、实验矩阵、核心特点和演示路线，便于快速了解系统整体结构。"
        )
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setWordWrap(True)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        layout.addWidget(title_card)

        metrics = QWidget()
        metrics_layout = QVBoxLayout(metrics)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(12)
        metrics_layout.addWidget(two_col_row(
            make_metric("作品定位", "声场与振动虚拟仿真", "面向大学物理、机械振动、声学实验和科普展示。"),
            make_metric("实验数量", "12 个教学案例", "覆盖驻波、模态、共振、干涉、衍射、带隙、吸声和三维声波。"),
        ))
        metrics_layout.addWidget(two_col_row(
            make_metric("核心特点", "动态 + 三维 + 增强分析", "支持声场演化、照片相似度、任意边界和自动报告。"),
            make_metric("技术实现", "Python 自主实现", "PySide6 界面、NumPy/SciPy 数值、Matplotlib 可视化。"),
        ))
        layout.addWidget(metrics)

        matrix, matrix_layout = make_card("实验矩阵")
        matrix_layout.addWidget(muted_label(
            "基础实验：一维驻波、二维膜模态、受迫共振扫描。\n"
            "进阶实验：双声源干涉、单缝声衍射、一维声子晶体带隙、亥姆霍兹共鸣吸声。\n"
            "三维实验：点声源球面波、双声源三维干涉、矩形房间驻波模态。\n"
            "应用案例：克拉尼图形、乐器共鸣箱、MEMS 谐振器、声学超材料与隔振吸声。"
        ))
        layout.addWidget(matrix)

        innovation, innovation_layout = make_card("核心特点")
        innovation_layout.addWidget(muted_label(
            "1. 从一维到三维构建声场实验链条，形成基础、进阶、应用的内容层次。\n"
            "2. 采用动态演示展示波峰传播、相位推进、扫频和模态振荡过程。\n"
            "3. 每个案例支持一键跳转和参数预设，适合课堂演示和重复实验。\n"
            "4. 将声学超材料中的带隙与局域共振纳入平台，连接工程应用。\n"
            "5. 提供照片相似度、自定义多边形有限差分、二维超材料阵列和自动报告生成。"
        ))
        layout.addWidget(innovation)

        route, route_layout = make_card("推荐演示路线")
        route_layout.addWidget(muted_label(
            "平台总览 -> 作品总览 -> 一维驻波播放 -> 二维克拉尼模态播放 -> 共振扫描 -> "
            "单缝声衍射 -> 声子晶体带隙 -> 三维房间驻波 -> 增强工具 -> 实验对比与课程联系。"
        ))
        layout.addWidget(route)
        layout.addStretch(1)
