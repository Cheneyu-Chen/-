from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QVBoxLayout, QWidget

from app.widgets.common import make_card, muted_label, two_col_row


CASES = [
    {
        "name": "驻波形成过程",
        "desc": "通过逐步调节激励频率，观察驻波从行波过渡到稳定驻波的过程。重点对比远离和接近固有频率时的振幅差异。",
        "actions": "• 在一维驻波页将频率从 0.5 Hz 缓慢调至 1.0 Hz\n• 观察节点和腹点的逐步形成\n• 增加阻尼，观察包络衰减变化",
    },
    {
        "name": "低阶模态比较",
        "desc": "对比矩形振动板的前几个模态，理解节点线数量与模态阶数之间的关系。",
        "actions": "• 在二维模态页选择矩形板\n• 调节主阶数 m=1、2、3 观察横向节点线变化\n• 调节次阶数 n，观察纵向节点线变化",
    },
    {
        "name": "阻尼对共振峰的影响",
        "desc": "通过不同阻尼设置，观察共振曲线形状变化，加深对 Q 值概念的理解。",
        "actions": "• 在共振扫描页设置固有频率 2.0 Hz\n• 将阻尼从 0.05 调至 0.3\n• 观察共振峰从尖锐变为平缓",
    },
    {
        "name": "激励位置与响应关系",
        "desc": "通过改变一维驻波的激励点位置，理解耦合效率对响应强度的影响。",
        "actions": "• 在一维驻波页固定频率为 1.0 Hz\n• 将激励位置从 0.1 调至 0.9\n• 观察当激励点接近节点时响应明显减弱",
    },
]


class CasesPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        overview, overview_layout = make_card("教学案例概览")
        overview_layout.addWidget(muted_label(
            "下方预置了 4 个常用教学案例，每个案例都配有操作建议和观察要点。"
            "点击列表项可查看详细信息。"
        ))
        layout.addWidget(overview)

        main = QWidget()
        main_layout = QHBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        list_card, list_layout = make_card("案例列表")
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.on_selection_changed)
        for case in CASES:
            self.list_widget.addItem(case["name"])
        list_layout.addWidget(self.list_widget)
        main_layout.addWidget(list_card, 0)

        detail_card, detail_layout = make_card("案例详情")
        self.title_label = QLabel("请选择左侧案例")
        self.title_label.setObjectName("SectionTitle")
        self.title_label.setWordWrap(True)
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.actions_label = QLabel()
        self.actions_label.setWordWrap(True)
        self.actions_label.setStyleSheet("color:#cbd5e1;font-family:consolas,monospace;")
        detail_layout.addWidget(self.title_label)
        detail_layout.addWidget(QLabel(""))
        detail_layout.addWidget(QLabel("教学目的："))
        detail_layout.addWidget(self.desc_label)
        detail_layout.addWidget(QLabel(""))
        detail_layout.addWidget(QLabel("操作建议："))
        detail_layout.addWidget(self.actions_label)
        detail_layout.addStretch(1)
        main_layout.addWidget(detail_card, 1)

        layout.addWidget(main, 3)
        layout.addStretch(1)

    def on_selection_changed(self, row: int) -> None:
        if 0 <= row < len(CASES):
            case = CASES[row]
            self.title_label.setText(case["name"])
            self.desc_label.setText(case["desc"])
            self.actions_label.setText(case["actions"])
        else:
            self.title_label.setText("请选择左侧案例")
            self.desc_label.clear()
            self.actions_label.clear()
