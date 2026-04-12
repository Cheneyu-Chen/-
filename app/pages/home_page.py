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
        subtitle = QLabel("面向大学物理实验教学场景，支持一维驻波、二维模态、共振扫描与案例化演示。")
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
            make_metric("教学导向", "交互式", "强调参数变化与物理规律之间的联系"),
            make_metric("数值核心", "自主实现", "驻波响应、模态场分布与共振峰识别均为本地计算"),
        ))
        metrics_layout.addWidget(two_col_row(
            make_metric("比赛展示", "中文友好", "适配 1920×1080 演示和录屏，界面信息层次清晰"),
            make_metric("扩展空间", "可继续迭代", "后续可加入实验对照、更多边界条件和数据导出"),
        ))
        layout.addWidget(metrics)

        overview, overview_layout = make_card("建议演示顺序")
        overview_layout.addWidget(muted_label(
            "1. 先在“一维驻波”页调节频率与阻尼，展示接近固有频率时振幅放大。\n"
            "2. 再切换到“二维模态”页，展示矩形板与圆膜的典型振型、节点线与热图。\n"
            "3. 进入“共振扫描”页，扫描频率范围并观察共振峰位置。\n"
            "4. 最后用“教学案例”和“实验对照”页收束，强调教学价值与可扩展性。"
        ))
        layout.addWidget(overview)

        features, features_layout = make_card("软件亮点")
        features_layout.addWidget(muted_label(
            "• 中文界面，适合比赛答辩和课堂演示\n"
            "• 多模块联动，强调从现象到规律的理解\n"
            "• 深色风格 + 热图可视化，适合录屏与 PPT 截图\n"
            "• 支持图像导出与案例预置，便于沉淀参赛材料"
        ))
        layout.addWidget(features)
        layout.addStretch(1)
