from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
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

from app.core.sound3d import room_mode_slices, spherical_wave_field, two_source_wave_field
from app.theme import CHART_BG, CHART_FG, CHART_FG_MUTED
from app.widgets.common import make_card, muted_label
from app.widgets.mpl_canvas import MplCanvas


class Sound3DPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.phase_value = 0.0
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

        self.label_a = QLabel("参数 A")
        self.label_b = QLabel("参数 B")
        form.addRow("实验类型", self.mode_box)
        form.addRow("频率 / Hz", self.freq_spin)
        form.addRow(self.label_a, self.param_a)
        form.addRow(self.label_b, self.param_b)
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
            "仿真进行时可使用鼠标拖动旋转三维图像来从不同视角观察。用连续相位推进显示声压场本身。球面波和双声源干涉显示瞬时声压曲面，"
            "房间驻波显示三个正交截面，便于观察三维空间中的节点面和声压热点。"
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
        self.last_mode = None
        self.refresh_plot()

    def refresh_plot(self) -> None:
        fig = self.canvas.figure
        mode = self.mode_box.currentText()
        frequency = self.freq_spin.value()
        animation_time = self.phase_value / max(frequency, 1.0)

        is_new = getattr(self, 'last_mode', None) != mode
        self.last_mode = mode

        if mode == "点声源球面波":
            self.label_a.setText("参数 A (不使用)")
            self.label_b.setText("参数 B (不使用)")
            self.param_a.setEnabled(False)
            self.param_b.setEnabled(False)
        elif mode == "双声源三维干涉":
            self.label_a.setText("声源间距(A) / m")
            self.label_b.setText("相位差(B) / rad")
            self.param_a.setEnabled(True)
            self.param_b.setEnabled(True)
        else:
            self.label_a.setText("X向阶数(A)")
            self.label_b.setText("Y向阶数(B)")
            self.param_a.setEnabled(True)
            self.param_b.setEnabled(True)

        if is_new or not fig.axes:
            fig.clear()
            ax = fig.add_subplot(111, projection="3d")
        else:
            ax = fig.axes[0]
            # 仅移除旧的多边形集合和线条，不销毁坐标轴对象，从而保留鼠标拖动交互状态！
            while ax.collections:
                ax.collections[0].remove()
            while ax.lines:
                ax.lines[0].remove()

        if mode == "点声源球面波":
            xx, yy, pressure, wavelength = spherical_wave_field(frequency, animation_time)
            surf = ax.plot_surface(xx, yy, pressure, cmap="RdBu_r", linewidth=0, antialiased=True, vmin=-1, vmax=1)
            if is_new:
                self._style_surface_axes(ax, "点声源球面波瞬时声压")
                fig.colorbar(surf, ax=ax, shrink=0.65, pad=0.08)
            self.param_hint.setText("参数 A、B 在点声源模式中不使用。")
            self.summary_label.setText(
                f"当前波长 λ={wavelength:.3f} m，相位推进 {self.phase_value:.2f} 周期。播放时可看到波峰从中心向外传播。"
            )
        elif mode == "双声源三维干涉":
            spacing = self.param_a.value()
            phase = self.param_b.value()
            xx, yy, pressure, _ = two_source_wave_field(frequency, spacing, phase, animation_time)
            surf = ax.plot_surface(xx, yy, pressure, cmap="RdBu_r", linewidth=0, antialiased=True, vmin=-1, vmax=1)
            if is_new:
                self._style_surface_axes(ax, "双声源三维干涉瞬时声压")
                fig.colorbar(surf, ax=ax, shrink=0.65, pad=0.08)
            self.param_hint.setText("参数 A：声源间距 d / m；参数 B：相位差 Δφ / rad。")
            self.summary_label.setText(
                f"声源间距 d={spacing:.2f} m，相位差 Δφ={phase:.2f} rad，相位推进 {self.phase_value:.2f} 周期。"
                "播放时红蓝声压峰谷交替推进，可观察相长和相消干涉区域。"
            )
        else:
            mx = max(1, round(self.param_a.value()))
            my = max(1, round(self.param_b.value()))
            mz = max(1, min(4, round(frequency / 180.0)))
            slices = room_mode_slices(mx, my, mz, animation_time, frequency)
            self._draw_room_mode(ax, slices, mx, my, mz, is_new)
            self.param_hint.setText("参数 A：x 方向模态阶数；参数 B：y 方向模态阶数；z 方向阶数由频率估算。")
            self.summary_label.setText(
                f"当前房间模态近似为 ({mx}, {my}, {mz})，相对本征频率约 {slices['relative_frequency']:.2f}。"
                "图中同时显示水平截面、纵向截面和横向截面，可观察三维空间中的节点面和声压热点。"
            )

        if is_new:
            fig.patch.set_facecolor(CHART_BG)
        self.canvas.draw_idle()

    def _style_surface_axes(self, ax, title: str) -> None:
        ax.set_title(title, color=CHART_FG)
        ax.set_xlabel("x / m", color=CHART_FG_MUTED)
        ax.set_ylabel("y / m", color=CHART_FG_MUTED)
        ax.set_zlabel("声压", color=CHART_FG_MUTED)
        ax.set_zlim(-1.1, 1.1)
        ax.view_init(elev=28, azim=-55)
        ax.set_facecolor(CHART_BG)

    def _draw_room_mode(self, ax, slices: dict, mx: int, my: int, mz: int, is_new: bool) -> None:
        cmap = plt.get_cmap("RdBu_r")
        norm = plt.Normalize(-1, 1)

        for key, alpha in [("xy", 0.86), ("yz", 0.78), ("xz", 0.78)]:
            sx, sy, sz, pressure = slices[key]
            colors = cmap(norm(pressure))
            colors[..., -1] = alpha
            ax.plot_surface(sx, sy, sz, facecolors=colors, rstride=1, cstride=1, linewidth=0, shade=False, antialiased=False)

        self._draw_room_box(ax)
        
        if is_new:
            sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
            sm.set_array([])
            ax.figure.colorbar(sm, ax=ax, shrink=0.65, pad=0.08, label="声压")

            ax.set_xlabel("x / L", color=CHART_FG_MUTED)
            ax.set_ylabel("y / W", color=CHART_FG_MUTED)
            ax.set_zlabel("z / H", color=CHART_FG_MUTED)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_zlim(0, 1)
            ax.set_box_aspect((1.25, 1.0, 0.75))
            ax.view_init(elev=24, azim=-42)
            ax.set_facecolor(CHART_BG)
        
        # 始终更新标题（因为mx, my, mz即使在同一模式下也可能变化）
        ax.set_title(f"矩形房间驻波模态：({mx}, {my}, {mz})", color=CHART_FG)

    def _draw_room_box(self, ax) -> None:
        corners = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
        ])
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]
        for start, end in edges:
            xs, ys, zs = zip(corners[start], corners[end])
            ax.plot(xs, ys, zs, color=CHART_FG_MUTED, linewidth=0.8, alpha=0.55)

    def on_tick(self) -> None:
        self.phase_value = (self.phase_value + 0.035) % 1.0
        self.refresh_plot()

    def start_animation(self) -> None:
        self.timer.start(45)

    def stop_animation(self) -> None:
        self.timer.stop()

    def reset_animation(self) -> None:
        self.phase_value = 0.0
        self.last_mode = None  # 强制作为新图重新绘制，以重置视角
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
        self.phase_value = 0.0
        self.last_mode = None  # 重置预设时也恢复默认视角
        self.refresh_plot()

    def export_figure(self) -> None:
        outputs = Path.cwd() / "outputs"
        outputs.mkdir(exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "导出三维声波图像", str(outputs / "sound3d.png"), "PNG 图像 (*.png)")
        if path:
            self.canvas.figure.savefig(path, dpi=180, facecolor=self.canvas.figure.get_facecolor(), bbox_inches="tight")
