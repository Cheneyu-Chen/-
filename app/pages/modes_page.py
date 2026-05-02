from __future__ import annotations

from pathlib import Path

import matplotlib.patches as patches
import numpy as np
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
from app.theme import (
    CHART_BG, CHART_CONTOUR, CHART_FG, CHART_FG_MUTED, CHART_SPINE, CHART_TICK,
)
from app.widgets.common import make_card, muted_label
from app.widgets.mpl_canvas import MplCanvas


class ModesPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
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
        refresh_btn = QPushButton("刷新")
        export_btn = QPushButton("导出图像")
        refresh_btn.clicked.connect(self.refresh_plot)
        export_btn.clicked.connect(self.export_figure)
        button_row.addWidget(refresh_btn)
        button_row.addWidget(export_btn)
        control_layout.addLayout(button_row)

        note_card, note_layout = make_card("理论对应")
        note_layout.addWidget(muted_label(
            "二维膜振动可写作 uₜₜ = c²∇²u，薄板模型进一步对应 D∇⁴w + ρh·wₜₜ = 0。"
            "本页面用解析或近似振型快速显示节点线；节点线就是克拉尼实验中沙粒最终聚集的区域。"
        ))
        control_layout.addWidget(note_card)
        control_layout.addStretch(1)
        root.addWidget(control_card, 0)

        right = QVBoxLayout()
        right.setSpacing(12)
        plot_card, plot_layout = make_card("振幅热图与节点线")
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

    def refresh_plot(self) -> None:
        primary = int(self.first_index.currentText() or "1")
        secondary = int(self.second_index.currentText() or "1")
        geometry_name = self.geometry_box.currentText()

        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if geometry_name.startswith("矩形"):
            xx, yy, zz, relative_freq = rectangular_mode(primary, secondary, resolution=180)
            im = ax.imshow(zz, extent=[0, 1, 0, 1], origin="lower", cmap="RdBu_r")
            ax.contour(xx, yy, zz, levels=[0], colors=CHART_CONTOUR, linewidths=1.3)
            ax.set_title(f"矩形膜模态：m={primary}，n={secondary}", color=CHART_FG)
            node_text = f"内部竖向节点约 {max(primary - 1, 0)} 条，横向节点约 {max(secondary - 1, 0)} 条。"
            model_text = "矩形边界近似满足四边固定，振型 φ = sin(mπx)sin(nπy)。"
        elif geometry_name.startswith("圆形"):
            order = primary - 1
            radial = max(1, secondary)
            xx, yy, zz, relative_freq = circular_mode(order, radial, resolution=220)
            im = ax.imshow(zz, extent=[-1, 1, -1, 1], origin="lower", cmap="RdBu_r")
            ax.contour(xx, yy, np.ma.filled(zz, np.nan), levels=[0], colors=CHART_CONTOUR, linewidths=1.2)
            ax.add_patch(patches.Circle((0, 0), 1, fill=False, edgecolor=CHART_SPINE, linewidth=1.2))
            ax.set_title(f"圆形膜模态：角向阶数={order}，径向指标={radial}", color=CHART_FG)
            node_text = "角向阶数决定径向分瓣数量，径向指标决定同心节点圈数量。"
            model_text = "圆形膜振型由贝塞尔函数 Jₘ(kr) 与 cos(mθ) 组合得到。"
        else:
            xx, yy, zz, relative_freq = triangular_mode(primary, secondary, resolution=200)
            im = ax.imshow(zz, extent=[0, 1, 0, 1], origin="lower", cmap="RdBu_r")
            ax.contour(xx, yy, np.ma.filled(zz, np.nan), levels=[0], colors=CHART_CONTOUR, linewidths=1.2)
            ax.add_patch(patches.Polygon([[0, 0], [1, 0], [0, 1]], fill=False, edgecolor=CHART_SPINE, linewidth=1.2))
            ax.set_title(f"三角形膜近似模态：m={primary}，n={secondary}", color=CHART_FG)
            node_text = "三角边界会打破矩形对称性，节点线更容易形成斜向与局部分裂图案。"
            model_text = "此处采用满足三角区域零边界的解析近似，适合教学快速展示。"

        cbar = fig.colorbar(im, ax=ax, shrink=0.85)
        cbar.ax.yaxis.set_tick_params(color=CHART_TICK)
        for tick in cbar.ax.get_yticklabels():
            tick.set_color(CHART_FG_MUTED)
        cbar.outline.set_edgecolor(CHART_SPINE)
        ax.set_aspect("equal", adjustable="box")
        ax.set_facecolor(CHART_BG)
        ax.tick_params(colors=CHART_TICK)
        for spine in ax.spines.values():
            spine.set_color(CHART_SPINE)
        fig.patch.set_facecolor(CHART_BG)
        self.canvas.draw_idle()

        application = self.application_box.currentText()
        app_text = {
            "教学演示": "适合说明本征值问题、边界条件和模态正交性。",
            "克拉尼图形": "可把零等值线视为沙粒聚集线，用于解释频率改变时图案突变。",
            "乐器共鸣箱": "可比较不同形状的模态密度，讨论音色、响度和共鸣频段。",
            "MEMS 谐振器": "可关注高 Q 模态的节点/腹部分布，讨论传感器灵敏度与抗干扰设计。",
        }[application]
        self.summary_label.setText(
            f"{model_text} 当前相对本征频率约为 {relative_freq:.2f}。{node_text} "
            f"应用场景：{app_text}"
        )

    def apply_preset(self, preset: dict) -> None:
        geometry_index = {
            "rectangular": 0,
            "circular": 1,
            "triangular": 2,
        }.get(preset.get("geometry", "rectangular"), 0)
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
        self.refresh_plot()

    def export_figure(self) -> None:
        outputs = Path.cwd() / "outputs"
        outputs.mkdir(exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "导出模态图像", str(outputs / "mode_map.png"), "PNG 图像 (*.png)")
        if path:
            self.canvas.figure.savefig(path, dpi=180, facecolor=self.canvas.figure.get_facecolor(), bbox_inches="tight")
