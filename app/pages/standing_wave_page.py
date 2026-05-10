from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.standing_wave import StandingWaveModel
from app.theme import (
    CHART_BG, CHART_FG, CHART_FG_MUTED, CHART_GRID, CHART_LEGEND_EC,
    CHART_LEGEND_FC, CHART_LINE_AMBER, CHART_LINE_GREEN, CHART_LINE_PRIMARY,
    CHART_NODE_LINE, CHART_SPINE, CHART_TICK,
)
from app.widgets.common import formula_label, make_card, muted_label
from app.widgets.mpl_canvas import MplCanvas


class StandingWavePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.model = StandingWaveModel()
        self.x = np.linspace(0, 1, 400)
        self.time_value = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        control_card, control_layout = make_card("一维驻波参数")
        form = QFormLayout()
        form.setSpacing(8)

        self.mode_box = QComboBox()
        self.mode_box.addItems(["1 阶", "2 阶", "3 阶", "4 阶"])
        self.mode_box.currentIndexChanged.connect(self.refresh_plot)

        self.boundary_box = QComboBox()
        self.boundary_box.addItems(["固定-固定", "固定-自由", "自由-自由"])
        self.boundary_box.currentIndexChanged.connect(self.refresh_plot)

        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(0.2, 6.0)
        self.freq_spin.setSingleStep(0.1)
        self.freq_spin.setValue(1.0)
        self.freq_spin.valueChanged.connect(self.refresh_plot)

        self.amp_spin = QDoubleSpinBox()
        self.amp_spin.setRange(0.05, 1.5)
        self.amp_spin.setSingleStep(0.05)
        self.amp_spin.setValue(0.6)
        self.amp_spin.valueChanged.connect(self.refresh_plot)

        self.damping_spin = QDoubleSpinBox()
        self.damping_spin.setRange(0.01, 1.0)
        self.damping_spin.setSingleStep(0.02)
        self.damping_spin.setValue(0.12)
        self.damping_spin.valueChanged.connect(self.refresh_plot)

        self.excitation_spin = QDoubleSpinBox()
        self.excitation_spin.setRange(0.05, 0.95)
        self.excitation_spin.setSingleStep(0.05)
        self.excitation_spin.setValue(0.50)
        self.excitation_spin.valueChanged.connect(self.refresh_plot)

        form.addRow("边界条件", self.boundary_box)
        form.addRow("模态阶数 n", self.mode_box)
        form.addRow("驱动频率 / Hz", self.freq_spin)
        form.addRow("驱动振幅", self.amp_spin)
        form.addRow("阻尼比 ζ", self.damping_spin)
        form.addRow("激励位置 x/L", self.excitation_spin)
        control_layout.addLayout(form)
        control_layout.addSpacing(16)

        buttons = QHBoxLayout()
        buttons.setSpacing(16)
        buttons.setContentsMargins(0, 0, 0, 0)
        play_btn = QPushButton("播放")
        pause_btn = QPushButton("暂停")
        reset_btn = QPushButton("重置")
        export_btn = QPushButton("导出图像")
        for btn in (play_btn, pause_btn, reset_btn, export_btn):
            btn.setFixedHeight(44)
        play_btn.clicked.connect(self.start_animation)
        pause_btn.clicked.connect(self.stop_animation)
        reset_btn.clicked.connect(self.reset_defaults)
        export_btn.clicked.connect(self.export_figure)
        buttons.addWidget(play_btn)
        buttons.addWidget(pause_btn)
        control_layout.addLayout(buttons)
        control_layout.addWidget(reset_btn)
        control_layout.addWidget(export_btn)

        tips_card, tips_layout = make_card("理论对应")
        tips_layout.addWidget(formula_label(
            "固定-固定：y(0) = y(L) = 0",
            "本征频率：fₙ = n·v / (2L)",
            "固定-自由：fₙ = (n - 1/2)·v / (2L)",
            "激励耦合：C = |φₙ(x₀)|",
        ))
        tips_layout.addWidget(muted_label(
            "每一条公式单独成行显示。激励点位于节点附近时，耦合系数接近 0，即使频率接近共振也难以激发该模态。"
        ))
        control_layout.addWidget(tips_card)
        control_layout.addStretch(1)
        root.addWidget(control_card, 0)

        right = QVBoxLayout()
        right.setSpacing(12)
        plot_card, plot_layout = make_card("驻波形态与节点")
        self.canvas = MplCanvas(width=7.6, height=4.2, dpi=100)
        plot_layout.addWidget(self.canvas)
        right.addWidget(plot_card, 4)

        info_card, info_layout = make_card("仿真解释")
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)

        metrics = QWidget()
        metrics_layout = QGridLayout(metrics)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(10)
        self.metric_labels: dict[str, QLabel] = {}
        for idx, key in enumerate(["本征频率", "响应放大", "激励耦合", "节点数量"]):
            label = QLabel("--")
            label.setObjectName("MetricValue")
            label.setWordWrap(True)
            box, box_layout = make_card(key)
            box_layout.addWidget(label)
            metrics_layout.addWidget(box, idx // 2, idx % 2)
            self.metric_labels[key] = label
        info_layout.addWidget(metrics)
        right.addWidget(info_card, 2)

        right_container = QWidget()
        right_container.setLayout(right)
        root.addWidget(right_container, 1)
        self.refresh_plot()

    def current_mode(self) -> int:
        return self.mode_box.currentIndex() + 1

    def current_boundary(self) -> str:
        mapping = {0: "fixed-fixed", 1: "fixed-free", 2: "free-free"}
        return mapping[self.boundary_box.currentIndex()]

    def refresh_plot(self) -> None:
        y, envelope, info = self.model.simulate(
            self.x,
            self.time_value,
            self.freq_spin.value(),
            self.current_mode(),
            self.damping_spin.value(),
            self.amp_spin.value(),
            self.excitation_spin.value(),
            self.current_boundary(),
        )
        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(self.x, y, color=CHART_LINE_PRIMARY, linewidth=2.0, label="瞬时位移")
        ax.plot(self.x, envelope, color=CHART_LINE_AMBER, linestyle="--", linewidth=1.6, label="振幅包络")
        ax.plot(self.x, -envelope, color=CHART_LINE_AMBER, linestyle="--", linewidth=1.6)
        for pos in info["node_positions"]:
            ax.axvline(pos, color=CHART_NODE_LINE, linestyle=":", linewidth=1)
        ax.scatter([self.excitation_spin.value()], [0], color=CHART_LINE_GREEN, s=70, zorder=5, label="激励点")
        ax.set_title("一维驻波：频率、边界条件与节点分布", color=CHART_FG, fontsize=13)
        ax.set_xlabel("归一化位置 x/L", color=CHART_FG_MUTED)
        ax.set_ylabel("位移幅值", color=CHART_FG_MUTED)
        ax.grid(True, alpha=0.6, color=CHART_GRID, linewidth=0.8)
        ax.set_facecolor(CHART_BG)
        for spine in ax.spines.values():
            spine.set_color(CHART_SPINE)
        ax.tick_params(colors=CHART_TICK)
        leg = ax.legend(loc="upper right", facecolor=CHART_LEGEND_FC, edgecolor=CHART_LEGEND_EC)
        for text in leg.get_texts():
            text.set_color(CHART_FG)
        fig.patch.set_facecolor(CHART_BG)
        self.canvas.draw_idle()

        detune = self.freq_spin.value() - info["natural_frequency"]
        self.info_label.setText(
            f"当前为 {self.boundary_box.currentText()} 边界、{self.current_mode()} 阶模态。"
            f"驱动频率 {self.freq_spin.value():.2f} Hz，本征频率 {info['natural_frequency']:.2f} Hz，"
            f"失谐量 {detune:+.2f} Hz。激励耦合系数为 {info['coupling']:.2f}。"
            "这说明同一频率下，激励位置不同会导致不同的振幅响应。"
        )
        self.metric_labels["本征频率"].setText(f"{info['natural_frequency']:.2f} Hz")
        self.metric_labels["响应放大"].setText(f"{info['gain']:.2f}")
        self.metric_labels["激励耦合"].setText(f"{info['coupling']:.2f}")
        self.metric_labels["节点数量"].setText(str(len(info["node_positions"])))

    def on_tick(self) -> None:
        self.time_value += 0.04
        self.refresh_plot()

    def start_animation(self) -> None:
        self.timer.start(40)

    def stop_animation(self) -> None:
        self.timer.stop()

    def reset_defaults(self) -> None:
        self.mode_box.setCurrentIndex(0)
        self.boundary_box.setCurrentIndex(0)
        self.freq_spin.setValue(1.0)
        self.amp_spin.setValue(0.6)
        self.damping_spin.setValue(0.12)
        self.excitation_spin.setValue(0.50)
        self.time_value = 0.0
        self.refresh_plot()

    def apply_preset(self, preset: dict) -> None:
        boundary_index = {
            "fixed-fixed": 0,
            "fixed-free": 1,
            "free-free": 2,
        }.get(preset.get("boundary", "fixed-fixed"), 0)
        self.boundary_box.setCurrentIndex(boundary_index)
        self.mode_box.setCurrentIndex(max(1, int(preset.get("mode", 1))) - 1)
        self.freq_spin.setValue(float(preset.get("frequency", self.freq_spin.value())))
        self.amp_spin.setValue(float(preset.get("amplitude", self.amp_spin.value())))
        self.damping_spin.setValue(float(preset.get("damping", self.damping_spin.value())))
        self.excitation_spin.setValue(float(preset.get("excitation", self.excitation_spin.value())))
        self.time_value = 0.0
        self.refresh_plot()

    def export_figure(self) -> None:
        outputs = Path.cwd() / "outputs"
        outputs.mkdir(exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "导出驻波图像", str(outputs / "standing_wave.png"), "PNG 图像 (*.png)")
        if path:
            self.canvas.figure.savefig(path, dpi=180, facecolor=self.canvas.figure.get_facecolor(), bbox_inches="tight")
