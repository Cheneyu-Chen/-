from __future__ import annotations

from pathlib import Path

import matplotlib.patches as patches
import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.modes import circular_mode, rectangular_mode, triangular_mode
from app.theme import CHART_BG, CHART_CONTOUR, CHART_FG, CHART_FG_MUTED, CHART_SPINE, CHART_TICK
from app.widgets.common import make_card, muted_label
from app.widgets.mpl_canvas import MplCanvas


class ModesPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.time_value = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        control_card, control_layout = make_card("二维模态参数")
        form = QFormLayout()
        form.setSpacing(10)

        self.geometry_box = QComboBox()
        self.geometry_box.addItems(["矩形膜 / 薄板", "圆形膜 / 圆盘", "三角形膜"])
        self.geometry_box.currentIndexChanged.connect(self.refresh_plot)

        self.first_index = QComboBox()
        self.second_index = QComboBox()
        for i in range(1, 6):
            self.first_index.addItem(str(i))
            self.second_index.addItem(str(i))
        self.second_index.setCurrentIndex(1)
        self.first_index.currentIndexChanged.connect(self.refresh_plot)
        self.second_index.currentIndexChanged.connect(self.refresh_plot)

        self.application_box = QComboBox()
        self.application_box.addItems(["教学演示", "克拉尼图形", "乐器共鸣箱", "MEMS 谐振器"])
        self.application_box.currentIndexChanged.connect(self.refresh_plot)

        form.addRow("几何形状", self.geometry_box)
        form.addRow("第一模态指标", self.first_index)
        form.addRow("第二模态指标", self.second_index)
        form.addRow("应用场景", self.application_box)
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

        note_card, note_layout = make_card("动态演示说明")
        note_layout.addWidget(muted_label(
            "播放后，颜色表示瞬时位移正负变化，节点线保持不动；这能更直观看到“模态形状固定、幅值随时间振荡”的物理图像。"
        ))
        control_layout.addWidget(note_card)
        control_layout.addStretch(1)
        root.addWidget(control_card, 0)

        right = QVBoxLayout()
        right.setSpacing(12)
        plot_card, plot_layout = make_card("动态振幅热图与节点线")
        self.canvas = MplCanvas(width=7.6, height=4.3, dpi=100)
        plot_layout.addWidget(self.canvas)
        right.addWidget(plot_card, 4)

        summary_card, summary_layout = make_card("仿真解释")
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)
        right.addWidget(summary_card, 1)

        right_container = QWidget()
        right_container.setLayout(right)
        root.addWidget(right_container, 1)
        self.refresh_plot()

    def _mode_data(self):
        primary = int(self.first_index.currentText() or "1")
        secondary = int(self.second_index.currentText() or "1")
        geometry_name = self.geometry_box.currentText()
        if geometry_name.startswith("矩形"):
            xx, yy, zz, relative_freq = rectangular_mode(primary, secondary, resolution=180)
            title = f"矩形膜模态：m={primary}，n={secondary}"
            extent = [0, 1, 0, 1]
            model_text = "矩形边界近似满足四边固定，振型 φ = sin(mπx)sin(nπy)。"
            patch = None
        elif geometry_name.startswith("圆形"):
            order = primary - 1
            radial = max(1, secondary)
            xx, yy, zz, relative_freq = circular_mode(order, radial, resolution=220)
            title = f"圆形膜模态：角向阶数={order}，径向指标={radial}"
            extent = [-1, 1, -1, 1]
            model_text = "圆形膜振型由贝塞尔函数 Jₘ(kr) 与 cos(mθ) 组合得到。"
            patch = patches.Circle((0, 0), 1, fill=False, edgecolor=CHART_SPINE, linewidth=1.2)
        else:
            xx, yy, zz, relative_freq = triangular_mode(primary, secondary, resolution=200)
            title = f"三角形膜近似模态：m={primary}，n={secondary}"
            extent = [0, 1, 0, 1]
            model_text = "三角边界会打破矩形对称性，节点线更容易形成斜向图案。"
            patch = patches.Polygon([[0, 0], [1, 0], [0, 1]], fill=False, edgecolor=CHART_SPINE, linewidth=1.2)
        return xx, yy, zz, relative_freq, title, extent, model_text, patch

    def refresh_plot(self) -> None:
        xx, yy, zz, relative_freq, title, extent, model_text, patch = self._mode_data()
        temporal = np.cos(2 * np.pi * 0.7 * self.time_value)
        dynamic_zz = zz * temporal

        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        im = ax.imshow(dynamic_zz, extent=extent, origin="lower", cmap="RdBu_r", vmin=-1, vmax=1)
        ax.contour(xx, yy, np.ma.filled(zz, np.nan), levels=[0], colors=CHART_CONTOUR, linewidths=1.2)
        if patch is not None:
            ax.add_patch(patch)
        cbar = fig.colorbar(im, ax=ax, shrink=0.85)
        cbar.ax.yaxis.set_tick_params(color=CHART_TICK)
        for tick in cbar.ax.get_yticklabels():
            tick.set_color(CHART_FG_MUTED)
        ax.set_title(title, color=CHART_FG)
        ax.set_aspect("equal", adjustable="box")
        ax.set_facecolor(CHART_BG)
        ax.tick_params(colors=CHART_TICK)
        for spine in ax.spines.values():
            spine.set_color(CHART_SPINE)
        fig.patch.set_facecolor(CHART_BG)
        self.canvas.draw_idle()

        self.summary_label.setText(
            f"{model_text} 当前相对本征频率约为 {relative_freq:.2f}。"
            f"瞬时相位系数为 {temporal:+.2f}，节点线位置不随时间移动。"
        )

    def on_tick(self) -> None:
        self.time_value += 0.04
        self.refresh_plot()

    def start_animation(self) -> None:
        self.timer.start(50)

    def stop_animation(self) -> None:
        self.timer.stop()

    def reset_animation(self) -> None:
        self.time_value = 0.0
        self.refresh_plot()

    def apply_preset(self, preset: dict) -> None:
        geometry_index = {"rectangular": 0, "circular": 1, "triangular": 2}.get(preset.get("geometry", "rectangular"), 0)
        self.geometry_box.setCurrentIndex(geometry_index)
        primary = max(1, min(5, int(preset.get("primary", 1))))
        secondary = max(1, min(5, int(preset.get("secondary", 1))))
        self.first_index.setCurrentIndex(primary - 1)
        self.second_index.setCurrentIndex(secondary - 1)
        application = str(preset.get("application", "教学演示"))
        for index in range(self.application_box.count()):
            if self.application_box.itemText(index) == application:
                self.application_box.setCurrentIndex(index)
                break
        self.time_value = 0.0
        self.refresh_plot()

    def export_figure(self) -> None:
        outputs = Path.cwd() / "outputs"
        outputs.mkdir(exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "导出模态图像", str(outputs / "mode_map.png"), "PNG 图像 (*.png)")
        if path:
            self.canvas.figure.savefig(path, dpi=180, facecolor=self.canvas.figure.get_facecolor(), bbox_inches="tight")
