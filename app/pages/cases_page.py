from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget

from app.widgets.common import make_card, muted_label


CASES = [
    {
        "name": "案例 1：固定弦的一维驻波",
        "target": "一维驻波",
        "desc": "控制变量：固定边界和材料参数，只改变模态阶数。观察节点数量和本征频率之间的关系，适合讲解 fₙ = n v / 2L。",
        "actions": "一键设置：固定-固定边界，2 阶模态，驱动频率 2.00 Hz，激励点位于 x/L=0.25。",
        "preset": {"page": "standing_wave", "boundary": "fixed-fixed", "mode": 2, "frequency": 2.0, "amplitude": 0.55, "damping": 0.10, "excitation": 0.25},
    },
    {
        "name": "案例 2：激励点在节点附近",
        "target": "一维驻波",
        "desc": "控制变量：保持频率和边界不变，只改变激励位置。用于说明节点处耦合系数小，接近共振也不一定能激发模态。",
        "actions": "一键设置：固定-固定边界，2 阶模态，驱动频率 2.00 Hz，激励点位于 x/L=0.50。",
        "preset": {"page": "standing_wave", "boundary": "fixed-fixed", "mode": 2, "frequency": 2.0, "amplitude": 0.75, "damping": 0.08, "excitation": 0.50},
    },
    {
        "name": "案例 3：矩形板克拉尼图形",
        "target": "二维模态",
        "desc": "控制变量：固定矩形几何，只改变模态指标。零等值线对应克拉尼实验中沙粒聚集的稳定图案。",
        "actions": "一键设置：矩形膜，m=3，n=2，应用场景选择“克拉尼图形”。",
        "preset": {"page": "modes", "geometry": "rectangular", "primary": 3, "secondary": 2, "application": "克拉尼图形"},
    },
    {
        "name": "案例 4：圆形 MEMS 谐振器",
        "target": "二维模态",
        "desc": "应用拓展：圆盘结构常见于 MEMS 谐振器。角向分瓣和径向节点圈可以用来解释驱动/检测电极布置。",
        "actions": "一键设置：圆形膜，角向阶数 2，径向指标 1，应用场景选择“MEMS 谐振器”。",
        "preset": {"page": "modes", "geometry": "circular", "primary": 3, "secondary": 1, "application": "MEMS 谐振器"},
    },
    {
        "name": "案例 5：低阻尼共振峰扫描",
        "target": "共振扫描",
        "desc": "控制变量：固定本征频率，只降低阻尼比。观察尖锐共振峰，用于解释 Q 值、峰值响应和半功率带宽。",
        "actions": "一键设置：扫描 0.5-4.0 Hz，本征频率 2.00 Hz，阻尼比 0.04。",
        "preset": {"page": "resonance", "start": 0.5, "end": 4.0, "natural": 2.0, "damping": 0.04, "points": 320},
    },
    {
        "name": "案例 6：高阻尼响应对比",
        "target": "共振扫描",
        "desc": "对照实验：与低阻尼案例相比，只增大阻尼比。观察峰值下降、带宽变宽，形成清晰的实验讨论材料。",
        "actions": "一键设置：扫描 0.5-4.0 Hz，本征频率 2.00 Hz，阻尼比 0.25。",
        "preset": {"page": "resonance", "start": 0.5, "end": 4.0, "natural": 2.0, "damping": 0.25, "points": 320},
    },
    {
        "name": "案例 7：单缝声衍射",
        "target": "进阶声学",
        "desc": "进阶实验：声波通过狭缝后发生衍射，主瓣宽度与波长、缝宽和观测距离有关。适合讲解惠更斯原理和孔径限制下的声场扩展。",
        "actions": "一键设置：单缝声衍射，频率 680 Hz，缝宽 0.18 m，屏幕距离 1.60 m。",
        "preset": {"page": "advanced", "experiment": "单缝声衍射", "frequency": 680.0, "param_a": 0.18, "param_b": 1.6},
    },
    {
        "name": "案例 8：声子晶体带隙",
        "target": "进阶声学",
        "desc": "高阶实验：周期结构会让特定频率的声波无法传播。通过改变质量比和刚度比，观察声学支、光学支和带隙宽度。",
        "actions": "一键设置：一维声子晶体带隙，质量比 3.00，刚度比 0.60。",
        "preset": {"page": "advanced", "experiment": "一维声子晶体带隙", "frequency": 800.0, "param_a": 3.0, "param_b": 0.6},
    },
    {
        "name": "案例 9：亥姆霍兹共鸣吸声",
        "target": "进阶声学",
        "desc": "高阶实验：局域共振器会在目标频段强吸声，是消声器、建筑声学和声学超材料的基本单元。",
        "actions": "一键设置：亥姆霍兹共鸣吸声，共鸣频率 420 Hz，阻尼 0.08。",
        "preset": {"page": "advanced", "experiment": "亥姆霍兹共鸣吸声", "frequency": 420.0, "param_a": 0.08, "param_b": 0.0},
    },
    {
        "name": "案例 10：三维点声源球面波",
        "target": "三维声波",
        "desc": "动态实验：观察声压波峰从点声源向外传播，理解三维声波的球面扩散和波长概念。",
        "actions": "一键设置：点声源球面波，频率 420 Hz。",
        "preset": {"page": "sound3d", "mode": "点声源球面波", "frequency": 420.0, "param_a": 0.8, "param_b": 0.0},
    },
    {
        "name": "案例 11：三维双声源干涉",
        "target": "三维声波",
        "desc": "动态实验：两个声源同时发声，三维声压曲面展示相长和相消干涉区域随时间变化。",
        "actions": "一键设置：双声源三维干涉，频率 620 Hz，声源间距 0.65 m，相位差 0.80 rad。",
        "preset": {"page": "sound3d", "mode": "双声源三维干涉", "frequency": 620.0, "param_a": 0.65, "param_b": 0.8},
    },
    {
        "name": "案例 12：矩形房间三维驻波",
        "target": "三维声波",
        "desc": "应用实验：房间长、宽、高方向同时形成驻波模态，声压分布会出现空间热点和静区。适合解释室内声学、低频驻波和吸声布置。",
        "actions": "一键设置：矩形房间驻波模态，频率 180 Hz，模态阶数近似为 (3, 2, 1)。",
        "preset": {"page": "sound3d", "mode": "矩形房间驻波模态", "frequency": 180.0, "param_a": 3.0, "param_b": 2.0},
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
            "选择案例后点击“一键进入案例”，平台会跳转到对应仿真页并自动设置参数。案例按基础、进阶、三维与应用拓展组织，"
            "便于在课堂展示和重复实验中快速复现实验现象。"
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
