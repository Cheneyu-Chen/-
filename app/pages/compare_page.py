from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.widgets.common import make_card, muted_label


class ComparePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        purpose_card, purpose_layout = make_card("实验对比目标")
        purpose_layout.addWidget(muted_label(
            "平台不仅输出仿真图，还应能和真实实验或理论图进行对照。建议在竞赛报告中放置三列："
            "真实克拉尼照片、仿真热图、理论节点线，并说明一致性与误差来源。"
        ))
        layout.addWidget(purpose_card)

        method_card, method_layout = make_card("对比流程")
        method_layout.addWidget(muted_label(
            "1. 采集实验图：在薄板上撒细沙，用扬声器或振子扫频，记录稳定图案。\n"
            "2. 建立仿真条件：选择相近几何形状、边界条件和模态阶数，生成振幅热图。\n"
            "3. 提取节点线：用零等值线表示理论节点线，与沙粒聚集位置比较。\n"
            "4. 解释误差：讨论夹持不理想、板厚不均、激励点偏移、阻尼和材料参数误差。"
        ))
        layout.addWidget(method_card)

        usage_card, usage_layout = make_card("可写入报告的指标")
        usage_layout.addWidget(muted_label(
            "频率误差：|fₑₓₚ - fₛᵢₘ| / fₑₓₚ。\n"
            "图案相似度：节点线数量、交点位置、对称性是否一致。\n"
            "参数敏感性：改变阻尼、边界或激励位置后，峰值和节点线如何变化。\n"
            "教学价值：学生能否从图像反推出模态阶数、边界条件和共振机制。"
        ))
        layout.addWidget(usage_card)

        report_card, report_layout = make_card("文档规范提示")
        report_layout.addWidget(muted_label(
            "建议按“选题背景、产品定位、开发环境、平台架构、物理原理、仿真模型、程序功能、实验案例、"
            "课程联系、讨论总结、分工、参考文献”的顺序整理。每个仿真现象都配一条公式、一张图和一段物理解释。"
        ))
        layout.addWidget(report_card)
        layout.addStretch(1)
