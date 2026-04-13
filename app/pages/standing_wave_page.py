from __future__ import annotations

import os
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
from app.widgets.common import make_card, muted_label
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

        control_card, control_layout = make_card("参数控制")
        form = QFormLayout()
        form.setSpacing(10)

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
        form.addRow("模态阶数", self.mode_box)
        form.addRow("激励频率 / Hz", self.freq_spin)
        form.addRow("初始振幅", self.amp_spin)
        form.addRow("阻尼系数", self.damping_spin)
        form.addRow("激励位置", self.excitation_spin)
        control_layout.addLayout(form)

        buttons = QHBoxLayout()
        play_btn = QPushButton("播放")
        pause_btn = QPushButton("暂停")
        reset_btn = QPushButton("恢复默认")
        export_btn = QPushButton("导出图像")
        play_btn.clicked.connect(self.start_animation)
        pause_btn.clicked.connect(self.stop_animation)
        reset_btn.clicked.connect(self.reset_defaults)
        export_btn.clicked.connect(self.export_figure)
        buttons.addWidget(play_btn)
        buttons.addWidget(pause_btn)
        control_layout.addLayout(buttons)
        control_layout.addWidget(reset_btn)
        control_layout.addWidget(export_btn)

        tips_card, tips_layout = make_card("教学提示")
        tips_layout.addWidget(muted_label(
            "• 当激励频率接近当前模态的固有频率时，响应增大。\n"
            "• 激励点若接近节点位置，耦合效率会明显下降。\n"
            "• 阻尼增大后，共振峰变缓，动态响应衰减更快。"
        ))
        control_layout.addWidget(tips_card)
        control_layout.addStretch(1)
        root.addWidget(control_card, 0)

        right = QVBoxLayout()
        right.setSpacing(12)
        plot_card, plot_layout = make_card("驻波动态显示")
        self.canvas = MplCanvas(width=7.6, height=4.2, dpi=100)
        plot_layout.addWidget(self.canvas)
        right.addWidget(plot_card, 4)

        info_card, info_layout = make_card("结果解读")
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)

        metrics = QWidget()
        metrics_layout = QGridLayout(metrics)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(10)
        self.metric_labels: dict[str, QLabel] = {}
        for idx, key in enumerate(["固有频率", "响应增益", "耦合系数", "节点数量"]):
            label = QLabel("--")
            label.setStyleSheet("font-size:20px;font-weight:700;color:#f8fafc;")
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
            self.current_boundary()
        )
        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(self.x, y, color="#60a5fa", linewidth=2.0, label="实时位移")
        ax.plot(self.x, envelope, color="#f59e0b", linestyle="--", linewidth=1.6, label="包络线")
        ax.plot(self.x, -envelope, color="#f59e0b", linestyle="--", linewidth=1.6)
        for pos in info["node_positions"]:
            ax.axvline(pos, color="#334155", linestyle=":", linewidth=1)
        ax.scatter([self.excitation_spin.value()], [0], color="#22c55e", s=70, zorder=5, label="激励点")
        ax.set_title("一维驻波时域快照", color="#e5e7eb", fontsize=13)
        ax.set_xlabel("归一化位置 x/L", color="#cbd5e1")
        ax.set_ylabel("位移", color="#cbd5e1")
        ax.grid(True, alpha=0.18)
        ax.set_facecolor("#0f172a")
        for spine in ax.spines.values():
            spine.set_color("#475569")
        ax.tick_params(colors="#cbd5e1")
        leg = ax.legend(loc="upper right", facecolor="#111827", edgecolor="#334155")
        for text in leg.get_texts():
            text.set_color("#e5e7eb")
        fig.patch.set_facecolor("#111827")
        self.canvas.draw_idle()

        self.info_label.setText(
            f"当前选择 {self.boundary_box.currentText()}， {self.current_mode()} 阶驻波。激励频率为 {self.freq_spin.value():.2f} Hz，"
            f"与该模态固有频率 {info['natural_frequency']:.2f} Hz 的接近程度决定了响应强弱。"
            f"激励位置耦合系数为 {info['coupling']:.2f}，说明激励点越接近腹点，越容易激发明显响应。"
        )
        self.metric_labels["固有频率"].setText(f"{info['natural_frequency']:.2f} Hz")
        self.metric_labels["响应增益"].setText(f"{info['gain']:.2f}")
        self.metric_labels["耦合系数"].setText(f"{info['coupling']:.2f}")
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

    def export_figure(self) -> None:
        outputs = Path.cwd() / "outputs"
        outputs.mkdir(exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "导出图像", str(outputs / "standing_wave.png"), "PNG 图片 (*.png)")
        if path:
            self.canvas.figure.savefig(path, dpi=180, facecolor=self.canvas.figure.get_facecolor(), bbox_inches="tight")
