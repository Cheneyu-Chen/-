from __future__ import annotations

from pathlib import Path

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

from app.core.modes import circular_mode, rectangular_mode
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
        self.geometry_box.addItems(["矩形振动板", "圆膜（扩展示例）"])
        self.geometry_box.currentIndexChanged.connect(self.refresh_plot)

        self.first_index = QComboBox()
        self.second_index = QComboBox()
        self._load_index_options()
        self.first_index.currentIndexChanged.connect(self.refresh_plot)
        self.second_index.currentIndexChanged.connect(self.refresh_plot)

        form.addRow("几何类型", self.geometry_box)
        form.addRow("主阶数", self.first_index)
        form.addRow("次阶数", self.second_index)
        control_layout.addLayout(form)

        button_row = QHBoxLayout()
        refresh_btn = QPushButton("重新计算")
        export_btn = QPushButton("导出图像")
        refresh_btn.clicked.connect(self.refresh_plot)
        export_btn.clicked.connect(self.export_figure)
        button_row.addWidget(refresh_btn)
        button_row.addWidget(export_btn)
        control_layout.addLayout(button_row)

        note_card, note_layout = make_card("教学说明")
        note_layout.addWidget(muted_label(
            "• 矩形板模态由 m、n 两个整数控制，节点线数目会随阶数增多。\n"
            "• 圆膜示例用贝塞尔函数构造，适合展示中心对称与角向节点变化。\n"
            "• 热图亮度越高表示振幅绝对值越大，黑色等值线附近可视为节点线区域。"
        ))
        control_layout.addWidget(note_card)
        control_layout.addStretch(1)
        root.addWidget(control_card, 0)

        right = QVBoxLayout()
        right.setSpacing(12)
        plot_card, plot_layout = make_card("振型热图与节点线")
        self.canvas = MplCanvas(width=7.6, height=4.3, dpi=100)
        plot_layout.addWidget(self.canvas)
        right.addWidget(plot_card, 4)

        summary_card, summary_layout = make_card("结果解读")
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)
        right.addWidget(summary_card, 1)

        right_container = QWidget()
        right_container.setLayout(right)
        root.addWidget(right_container, 1)
        self.refresh_plot()

    def _load_index_options(self) -> None:
        self.first_index.clear()
        self.second_index.clear()
        for i in range(1, 6):
            self.first_index.addItem(str(i))
            self.second_index.addItem(str(i))
        self.second_index.setCurrentIndex(1)

    def refresh_plot(self) -> None:
        primary = int(self.first_index.currentText() or "1")
        secondary = int(self.second_index.currentText() or "1")
        geometry_name = self.geometry_box.currentText()

        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if geometry_name.startswith("矩形"):
            xx, yy, zz, relative_freq = rectangular_mode(primary, secondary, resolution=180)
            im = ax.imshow(zz, extent=[0, 1, 0, 1], origin="lower", cmap="magma")
            ax.contour(xx, yy, zz, levels=[0], colors="#dbeafe", linewidths=1.3)
            ax.set_title(f"矩形板模态 m={primary}, n={secondary}", color="#e5e7eb")
            description = (
                f"当前为矩形振动板模态 (m={primary}, n={secondary})。相对频率约为 {relative_freq:.2f}。"
                f" 横向节点线约 {max(primary - 1, 0)} 条，纵向节点线约 {max(secondary - 1, 0)} 条。"
            )
        else:
            order = primary - 1
            radial = max(1, secondary)
            xx, yy, zz, relative_freq = circular_mode(order, radial, resolution=220)
            im = ax.imshow(zz, extent=[-1, 1, -1, 1], origin="lower", cmap="magma")
            ax.contour(xx, yy, np.ma.filled(zz, np.nan), levels=[0], colors="#dbeafe", linewidths=1.2)
            circle = ax.add_patch(__import__("matplotlib").patches.Circle((0, 0), 1, fill=False, edgecolor="#e5e7eb", linewidth=1.2))
            description = (
                f"当前为圆膜扩展示例，角向阶数为 {order}，径向序号为 {radial}，相对特征频率约 {relative_freq:.2f}。"
                f" 这类模式适合展示中心对称系统中的环形节点与角向节点。"
            )
            ax.set_title(f"圆膜模态 order={order}, radial={radial}", color="#e5e7eb")

        cbar = fig.colorbar(im, ax=ax, shrink=0.85)
        cbar.ax.yaxis.set_tick_params(color="#cbd5e1")
        for tick in cbar.ax.get_yticklabels():
            tick.set_color("#cbd5e1")
        cbar.outline.set_edgecolor("#475569")
        ax.set_facecolor("#0f172a")
        ax.tick_params(colors="#cbd5e1")
        for spine in ax.spines.values():
            spine.set_color("#475569")
        fig.patch.set_facecolor("#111827")
        self.canvas.draw_idle()

        self.summary_label.setText(
            description + "\n\n图中的浅色节点线附近振幅接近零，适合与克拉尼图形中的颗粒聚集路径建立对应关系。"
        )

    def export_figure(self) -> None:
        outputs = Path.cwd() / "outputs"
        outputs.mkdir(exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "导出图像", str(outputs / "mode_map.png"), "PNG 图片 (*.png)")
        if path:
            self.canvas.figure.savefig(path, dpi=180, facecolor=self.canvas.figure.get_facecolor(), bbox_inches="tight")
