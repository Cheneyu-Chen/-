from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget

from app.widgets.common import make_card, muted_label


CASES = [
    {
        "name": "案例 1：固定弦的一维驻波",
        "target": "一维驻波",
        "desc": "演示固定-固定边界下，模态阶数、节点数量和本征频率之间的关系。适合讲解 fₙ = n v / 2L。",
        "actions": "一键设置：固定-固定边界，2 阶模态，驱动频率 2.00 Hz，激励点位于 x/L=0.25。",
        "preset": {
            "page": "standing_wave",
            "boundary": "fixed-fixed",
            "mode": 2,
            "frequency": 2.0,
            "amplitude": 0.55,
            "damping": 0.10,
            "excitation": 0.25,
        },
    },
    {
        "name": "案例 2：激励点在节点附近",
        "target": "一维驻波",
        "desc": "同样接近共振时，激励点如果落在节点附近，耦合系数会显著变小，振动难以被激发。",
        "actions": "一键设置：固定-固定边界，2 阶模态，驱动频率 2.00 Hz，激励点位于 x/L=0.50。",
        "preset": {
            "page": "standing_wave",
            "boundary": "fixed-fixed",
            "mode": 2,
            "frequency": 2.0,
            "amplitude": 0.75,
            "damping": 0.08,
            "excitation": 0.50,
        },
    },
    {
        "name": "案例 3：矩形板克拉尼图形",
        "target": "二维模态",
        "desc": "展示矩形薄板/膜的节点线。零等值线可对应克拉尼实验中沙粒聚集的稳定图案。",
        "actions": "一键设置：矩形膜，m=3，n=2，应用场景选择“克拉尼图形”。",
        "preset": {
            "page": "modes",
            "geometry": "rectangular",
            "primary": 3,
            "secondary": 2,
            "application": "克拉尼图形",
        },
    },
    {
        "name": "案例 4：圆形 MEMS 谐振器",
        "target": "二维模态",
        "desc": "圆盘结构常见于 MEMS 谐振器。角向分瓣和径向节点圈可以用来解释驱动/检测电极布置。",
        "actions": "一键设置：圆形膜，角向阶数 2，径向指标 1，应用场景选择“MEMS 谐振器”。",
        "preset": {
            "page": "modes",
            "geometry": "circular",
            "primary": 3,
            "secondary": 1,
            "application": "MEMS 谐振器",
        },
    },
    {
        "name": "案例 5：低阻尼共振峰扫描",
        "target": "共振扫描",
        "desc": "演示低阻尼系统的尖锐共振峰。可用于解释 Q 值、峰值响应和半功率带宽。",
        "actions": "一键设置：扫描 0.5-4.0 Hz，本征频率 2.00 Hz，阻尼比 0.04。",
        "preset": {
            "page": "resonance",
            "start": 0.5,
            "end": 4.0,
            "natural": 2.0,
            "damping": 0.04,
            "points": 320,
        },
    },
    {
        "name": "案例 6：高阻尼响应对比",
        "target": "共振扫描",
        "desc": "演示阻尼增大后峰值下降、带宽变宽的现象，适合与低阻尼案例并列展示。",
        "actions": "一键设置：扫描 0.5-4.0 Hz，本征频率 2.00 Hz，阻尼比 0.25。",
        "preset": {
            "page": "resonance",
            "start": 0.5,
            "end": 4.0,
            "natural": 2.0,
            "damping": 0.25,
            "points": 320,
        },
    },
]


class CasesPage(QWidget):
    case_requested = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        overview, overview_layout = make_card("教学案例一键跳转")
        overview_layout.addWidget(muted_label(
            "选择一个教学案例后，点击“一键进入案例”，平台会自动跳转到对应仿真页面，并设置好频率、边界、模态、阻尼等参数。"
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

        detail_card, detail_layout = make_card("案例说明")
        self.title_label = QLabel("请选择一个案例")
        self.title_label.setObjectName("SectionTitle")
        self.title_label.setWordWrap(True)
        self.target_label = QLabel()
        self.target_label.setWordWrap(True)
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.actions_label = QLabel()
        self.actions_label.setWordWrap(True)
        self.actions_label.setObjectName("CodeLabel")
        self.apply_button = QPushButton("一键进入案例")
        self.apply_button.clicked.connect(self.apply_current_case)

        detail_layout.addWidget(self.title_label)
        detail_layout.addWidget(self.target_label)
        detail_layout.addWidget(QLabel("物理意义"))
        detail_layout.addWidget(self.desc_label)
        detail_layout.addWidget(QLabel("预设参数"))
        detail_layout.addWidget(self.actions_label)
        detail_layout.addWidget(self.apply_button)
        detail_layout.addStretch(1)
        main_layout.addWidget(detail_card, 1)

        layout.addWidget(main, 3)
        layout.addStretch(1)
        self.list_widget.setCurrentRow(0)

    def current_case(self) -> dict | None:
        row = self.list_widget.currentRow()
        if 0 <= row < len(CASES):
            return CASES[row]
        return None

    def on_selection_changed(self, row: int) -> None:
        if 0 <= row < len(CASES):
            case = CASES[row]
            self.title_label.setText(case["name"])
            self.target_label.setText(f"目标页面：{case['target']}")
            self.desc_label.setText(case["desc"])
            self.actions_label.setText(case["actions"])
            self.apply_button.setEnabled(True)
        else:
            self.title_label.setText("请选择一个案例")
            self.target_label.clear()
            self.desc_label.clear()
            self.actions_label.clear()
            self.apply_button.setEnabled(False)

    def apply_current_case(self) -> None:
        case = self.current_case()
        if case:
            self.case_requested.emit(case["preset"])
