from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.widgets.common import make_card, muted_label


class ComparePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        purpose_card, purpose_layout = make_card("实验对照的目的")
        purpose_layout.addWidget(muted_label(
            "本页面为实验对照功能的占位区。在条件允许的情况下，可通过实际实验获取振动板上的颗粒分布图样，"
            "并与仿真计算得到的节点线进行对比，增强作品的可信度。"
        ))
        layout.addWidget(purpose_card)

        method_card, method_layout = make_card("实验方法建议")
        method_layout.addWidget(muted_label(
            "• 使用扬声器激励矩形振动板，在板上撒细砂或盐粒。\n"
            "• 驱动频率逐渐扫过系统的固有频率，观察颗粒聚集位置。\n"
            "• 将实验照片中的颗粒聚集路径与二维模态页的节点线进行对比。\n"
            "• 若实验条件受限，可采用简化装置（如一维弦线）进行对比。"
        ))
        layout.addWidget(method_card)

        usage_card, usage_layout = make_card("对照结果解读")
        usage_layout.addWidget(muted_label(
            "• 若实验中的颗粒聚集路径与仿真节点线位置基本一致，说明模型假设在当前场景下是合理的。\n"
            "• 若存在明显差异，可分析其来源：例如理想化边界、材料非均匀性、测量误差等。\n"
            "• 将对照结果写入设计报告和 PPT，可显著提升作品完整性与可信度。"
        ))
        layout.addWidget(usage_card)

        note_card, note_layout = make_card("后续扩展方向")
        note_layout.addWidget(muted_label(
            "• 本版本为参赛首版，实验对照部分以占位形式呈现。\n"
            "• 若有实验条件，可在该页面嵌入实验照片与仿真结果并排显示。\n"
            "• 甚至可扩展到数据导入功能，支持用户上传自己的实验图样进行对比分析。"
        ))
        layout.addWidget(note_card)
        layout.addStretch(1)
