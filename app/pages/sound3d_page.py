from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.sound3d import room_mode_field, spherical_wave_field, two_source_wave_field
from app.theme import CHART_BG, CHART_FG, CHART_FG_MUTED
from app.widgets.common import make_card, muted_label
from app.widgets.mpl_canvas import MplCanvas


class Sound3DPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.time_value = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        control_card, control_layout = make_card("三维声波实验")
        form = QFormLayout()
        form.setSpacing(10)

        self.mode_box = QComboBox()
        self.mode_box.addItems(["点声源球面波", "双声源三维干涉", "矩形房间驻波模态"])
        self.mode_box.currentIndexChanged.connect(self.refresh_plot)

        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(80.0, 2000.0)
        self.freq_spin.setSingleStep(20.0)
        self.freq_spin.setValue(420.0)
        self.freq_spin.valueChanged.connect(self.refresh_plot)

        self.param_a = QDoubleSpinBox()
        self.param_a.setRange(0.05, 8.0)
        self.param_a.setSingleStep(0.05)
        self.param_a.setValue(0.8)
        self.param_a.valueChanged.connect(self.refresh_plot)

        self.param_b = QDoubleSpinBox()
        self.param_b.setRange(0.0, 8.0)
        self.param_b.setSingleStep(0.05)
        self.param_b.setValue(0.0)
        self.param_b.valueChanged.connect(self.refresh_plot)

        form.addRow("实验类型", self.mode_box)
        form.addRow("频率 / Hz", self.freq_spin)
        form.addRow("参数 A", self.param_a)
        form.addRow("参数 B", self.param_b)
        control_layout.addLayout(form)

        button_row = QHBoxLayout()
        play_btn = QPushButton("播放")
        pause_btn = QPushButton("暂停")
        reset_btn = QPushButton("复位")
        export_btn = QPushButton("导出图像")
        play_btn.clicked.connect(self.start_animation)
        pause_btn.clicked.connect(self.stop_animation)
        reset_btn.clicked.connect(self.reset_animation)
        export_btn.clicked.connect(self.export_figure)
        button_row.addWidget(play_btn)
        button_row.addWidget(pause_btn)
        control_layout.addLayout(button_row)
        control_layout.addWidget(reset_btn)
        control_layout.addWidget(export_btn)

        self.param_hint = QLabel()
        self.param_hint.setWordWrap(True)
        control_layout.addWidget(self.param_hint)

        note_card, note_layout = make_card("动态演示说明")
        note_layout.addWidget(muted_label(
            "本页用三维曲面显示声压瞬时分布：波峰和波谷会随时间传播，"
            "比静态声强图更适合展示球面波、干涉和房间模态的动态过程。"
        ))
        control_layout.addWidget(note_card)
        control_layout.addStretch(1)
        root.addWidget(control_card, 0)

        right = QVBoxLayout()
        plot_card, plot_layout = make_card("三维声压场")
        self.canvas = MplCanvas(width=7.8, height=4.8, dpi=100)
        plot_layout.addWidget(self.canvas)
        right.addWidget(plot_card, 4)

        summary_card, summary_layout = make_card("结果解释")
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)
        right.addWidget(summary_card, 1)

        right_container = QWidget()
        right_container.setLayout(right)
        root.addWidget(right_container, 1)
        self.refresh_plot()

    def refresh_plot(self) -> None:
        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111, projection="3d")
        mode = self.mode_box.currentText()

        if mode == "点声源球面波":
            xx, yy, pressure, wavelength = spherical_wave_field(self.freq_spin.value(), self.time_value)
            title = "点声源球面波瞬时声压"
            self.param_hint.setText("参数 A、B 在点声源模式中不使用。")
            self.summary_label.setText(
                f"当前波长 λ={wavelength:.3f} m。播放时可看到波峰从中心向外传播，体现三维声波的球面扩散。"
            )
        elif mode == "双声源三维干涉":
            spacing = self.param_a.value()
            phase = self.param_b.value()
            xx, yy, pressure, wavelength = two_source_wave_field(self.freq_spin.value(), spacing, phase, self.time_value)
            title = "双声源三维干涉瞬时声压"
            self.param_hint.setText("参数 A：声源间距 d / m；参数 B：相位差 Δφ / rad。")
            self.summary_label.setText(
                f"声源间距 d={spacing:.2f} m，相位差 Δφ={phase:.2f} rad。动态图中波面叠加会形成移动的相长/相消区域。"
            )
        else:
            mx = max(1, round(self.param_a.value()))
            my = max(1, round(self.param_b.value()))
            xx, yy, pressure, rel = room_mode_field(mx, my, 1, self.time_value, self.freq_spin.value())
            title = "矩形房间驻波模态截面"
            self.param_hint.setText("参数 A：x 方向模态阶数；参数 B：y 方向模态阶数；z 方向固定为 1。")
            self.summary_label.setText(
                f"当前模态近似为 ({mx}, {my}, 1)，相对本征频率约 {rel:.2f}。动态图展示房间中固定节点与振荡声压。"
            )

        surf = ax.plot_surface(xx, yy, pressure, cmap="RdBu_r", linewidth=0, antialiased=True, vmin=-1, vmax=1)
        ax.set_title(title, color=CHART_FG)
        ax.set_xlabel("x / m", color=CHART_FG_MUTED)
        ax.set_ylabel("y / m", color=CHART_FG_MUTED)
        ax.set_zlabel("声压", color=CHART_FG_MUTED)
        ax.set_zlim(-1.1, 1.1)
        ax.view_init(elev=28, azim=-55 + 20 * self.time_value)
        ax.set_facecolor(CHART_BG)
        fig.colorbar(surf, ax=ax, shrink=0.65, pad=0.08)
        fig.patch.set_facecolor(CHART_BG)
        self.canvas.draw_idle()

    def on_tick(self) -> None:
        self.time_value += 0.025
        self.refresh_plot()

    def start_animation(self) -> None:
        self.timer.start(45)

    def stop_animation(self) -> None:
        self.timer.stop()

    def reset_animation(self) -> None:
        self.time_value = 0.0
        self.refresh_plot()

    def apply_preset(self, preset: dict) -> None:
        mode = preset.get("mode")
        if mode:
            for index in range(self.mode_box.count()):
                if self.mode_box.itemText(index) == mode:
                    self.mode_box.setCurrentIndex(index)
                    break
        self.freq_spin.setValue(float(preset.get("frequency", self.freq_spin.value())))
        self.param_a.setValue(float(preset.get("param_a", self.param_a.value())))
        self.param_b.setValue(float(preset.get("param_b", self.param_b.value())))
        self.time_value = 0.0
        self.refresh_plot()

    def export_figure(self) -> None:
        outputs = Path.cwd() / "outputs"
        outputs.mkdir(exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "导出三维声波图像", str(outputs / "sound3d.png"), "PNG 图像 (*.png)")
        if path:
            self.canvas.figure.savefig(path, dpi=180, facecolor=self.canvas.figure.get_facecolor(), bbox_inches="tight")
