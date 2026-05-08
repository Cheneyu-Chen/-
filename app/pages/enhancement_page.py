from __future__ import annotations

from datetime import datetime
from pathlib import Path

import matplotlib.image as mpimg
import numpy as np
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.enhancements import (
    compare_experiment_photo,
    finite_difference_plate_mode,
    metamaterial_array_response,
    parse_polygon_vertices,
    polygon_to_text,
    regular_polygon_vertices,
)
from app.theme import CHART_BG, CHART_CONTOUR, CHART_FG, CHART_FG_MUTED, CHART_GRID, CHART_TICK
from app.widgets.common import make_card, muted_label
from app.widgets.mpl_canvas import MplCanvas


class EnhancementPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.photo_array: np.ndarray | None = None
        self.last_similarity: dict[str, float] | None = None
        self.last_polygon_summary = ""
        self.last_meta_summary = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        intro, intro_layout = make_card("增强分析工具")
        intro_layout.addWidget(muted_label(
            "本页提供实验照片导入与相似度计算、自定义多边形边界、有限差分薄板求解、"
            "二维声学超材料阵列和自动生成实验报告。"
        ))
        root.addWidget(intro)

        tabs = QTabWidget()
        tabs.addTab(self._build_photo_tab(), "照片相似度")
        tabs.addTab(self._build_polygon_tab(), "多边形薄板")
        tabs.addTab(self._build_meta_tab(), "二维超材料")
        tabs.addTab(self._build_report_tab(), "自动报告")
        root.addWidget(tabs, 1)

    def _build_photo_tab(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        controls, control_layout = make_card("实验照片导入")
        self.photo_template = QComboBox()
        self.photo_template.addItems(["一维驻波", "二维驻波", "共振曲线", "矩形克拉尼图形", "圆形克拉尼图形", "三角形薄板模态"])
        self.photo_primary = QSpinBox()
        self.photo_primary.setRange(1, 8)
        self.photo_primary.setValue(3)
        self.photo_secondary = QSpinBox()
        self.photo_secondary.setRange(1, 8)
        self.photo_secondary.setValue(2)

        form = QFormLayout()
        form.addRow("仿真模板", self.photo_template)
        form.addRow("第一模态指标", self.photo_primary)
        form.addRow("第二模态指标", self.photo_secondary)
        control_layout.addLayout(form)

        load_btn = QPushButton("导入实验照片")
        calc_btn = QPushButton("计算相似度")
        load_btn.clicked.connect(self.load_photo)
        calc_btn.clicked.connect(self.calculate_similarity)
        control_layout.addWidget(load_btn)
        control_layout.addWidget(calc_btn)
        control_layout.addWidget(muted_label("支持常见 PNG/JPG 图像。程序会转为灰度、统一尺寸，并与所选仿真节点图案计算相关系数和结构重叠度。"))
        control_layout.addStretch(1)
        layout.addWidget(controls, 0)

        result, result_layout = make_card("照片-仿真对比")
        self.photo_canvas = MplCanvas(width=7.4, height=4.6, dpi=100)
        self.photo_result = QLabel("请先导入实验照片。")
        self.photo_result.setWordWrap(True)
        result_layout.addWidget(self.photo_canvas)
        result_layout.addWidget(self.photo_result)
        layout.addWidget(result, 1)
        self._draw_photo_placeholder()
        return page

    def _build_polygon_tab(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        controls, control_layout = make_card("自定义多边形边界")
        self.vertex_editor = QPlainTextEdit()
        self.vertex_editor.setPlainText(polygon_to_text(regular_polygon_vertices(6)))
        self.vertex_editor.setMinimumHeight(130)
        self.poly_mode = QSpinBox()
        self.poly_mode.setRange(1, 8)
        self.poly_mode.setValue(2)
        self.poly_resolution = QSpinBox()
        self.poly_resolution.setRange(24, 56)
        self.poly_resolution.setValue(38)

        form = QFormLayout()
        form.addRow("模态序号", self.poly_mode)
        form.addRow("网格分辨率", self.poly_resolution)
        control_layout.addLayout(form)
        control_layout.addWidget(QLabel("顶点坐标 x,y："))
        control_layout.addWidget(self.vertex_editor)

        preset_row = QHBoxLayout()
        for name, sides in [("三角形", 3), ("五边形", 5), ("六边形", 6)]:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked=False, s=sides: self.set_polygon_preset(s))
            preset_row.addWidget(btn)
        control_layout.addLayout(preset_row)

        solve_btn = QPushButton("有限差分求解")
        solve_btn.clicked.connect(self.solve_polygon_mode)
        control_layout.addWidget(solve_btn)
        control_layout.addWidget(muted_label("求解使用网格拉普拉斯算子的平方近似薄板双调和算子，适合教学演示任意边界对节点线的影响。"))
        control_layout.addStretch(1)
        layout.addWidget(controls, 0)

        result, result_layout = make_card("有限差分薄板模态")
        self.poly_canvas = MplCanvas(width=7.4, height=4.6, dpi=100)
        self.poly_result = QLabel()
        self.poly_result.setWordWrap(True)
        result_layout.addWidget(self.poly_canvas)
        result_layout.addWidget(self.poly_result)
        layout.addWidget(result, 1)
        self.solve_polygon_mode()
        return page

    def _build_meta_tab(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        controls, control_layout = make_card("二维声学超材料阵列")
        self.meta_rows = QSpinBox()
        self.meta_rows.setRange(4, 16)
        self.meta_rows.setValue(8)
        self.meta_cols = QSpinBox()
        self.meta_cols.setRange(4, 16)
        self.meta_cols.setValue(8)
        self.meta_resonance = QDoubleSpinBox()
        self.meta_resonance.setRange(120.0, 1000.0)
        self.meta_resonance.setValue(520.0)
        self.meta_resonance.setSingleStep(20.0)
        self.meta_coupling = QDoubleSpinBox()
        self.meta_coupling.setRange(0.05, 0.90)
        self.meta_coupling.setValue(0.36)
        self.meta_coupling.setSingleStep(0.05)
        self.meta_damping = QDoubleSpinBox()
        self.meta_damping.setRange(0.02, 0.40)
        self.meta_damping.setValue(0.08)
        self.meta_damping.setSingleStep(0.02)
        self.meta_observe = QDoubleSpinBox()
        self.meta_observe.setRange(80.0, 1200.0)
        self.meta_observe.setValue(520.0)
        self.meta_observe.setSingleStep(20.0)

        form = QFormLayout()
        form.addRow("阵列行数", self.meta_rows)
        form.addRow("阵列列数", self.meta_cols)
        form.addRow("局域共振频率 / Hz", self.meta_resonance)
        form.addRow("耦合强度", self.meta_coupling)
        form.addRow("阻尼", self.meta_damping)
        form.addRow("观察频率 / Hz", self.meta_observe)
        control_layout.addLayout(form)

        run_btn = QPushButton("计算阵列响应")
        run_btn.clicked.connect(self.solve_metamaterial)
        control_layout.addWidget(run_btn)
        control_layout.addWidget(muted_label("该模型用局域共振与耦合衰减近似展示二维阵列的带隙、传输下降和空间声场衰减。"))
        control_layout.addStretch(1)
        layout.addWidget(controls, 0)

        result, result_layout = make_card("带隙与空间场")
        self.meta_canvas = MplCanvas(width=7.4, height=4.6, dpi=100)
        self.meta_result = QLabel()
        self.meta_result.setWordWrap(True)
        result_layout.addWidget(self.meta_canvas)
        result_layout.addWidget(self.meta_result)
        layout.addWidget(result, 1)
        self.solve_metamaterial()
        return page

    def _build_report_tab(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        controls, control_layout = make_card("自动生成实验报告")
        self.report_title = QPlainTextEdit()
        self.report_title.setPlainText("声场与振动可视化虚拟仿真平台实验报告")
        self.report_title.setMaximumHeight(70)
        control_layout.addWidget(QLabel("报告标题"))
        control_layout.addWidget(self.report_title)

        generate_btn = QPushButton("生成 Markdown 报告")
        generate_btn.clicked.connect(self.generate_report)
        control_layout.addWidget(generate_btn)
        control_layout.addWidget(muted_label("报告会汇总平台结构、分析结果、课程联系和误差分析，输出到 outputs 目录。"))
        control_layout.addStretch(1)
        layout.addWidget(controls, 0)

        result, result_layout = make_card("报告预览")
        self.report_preview = QPlainTextEdit()
        self.report_preview.setReadOnly(True)
        result_layout.addWidget(self.report_preview)
        layout.addWidget(result, 1)
        self.update_report_preview()
        return page

    def _draw_photo_placeholder(self) -> None:
        fig = self.photo_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "导入实验照片后显示对比结果", ha="center", va="center", color=CHART_FG_MUTED)
        ax.set_axis_off()
        fig.patch.set_facecolor(CHART_BG)
        self.photo_canvas.draw_idle()

    def load_photo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "导入实验照片", str(Path.cwd()), "图像文件 (*.png *.jpg *.jpeg *.bmp)")
        if not path:
            return
        self.photo_array = mpimg.imread(path)
        self.photo_result.setText(f"已导入：{Path(path).name}。请选择模板后点击“计算相似度”。")

    def calculate_similarity(self) -> None:
        if self.photo_array is None:
            self.photo_result.setText("请先导入实验照片。")
            return
        result = compare_experiment_photo(
            self.photo_array,
            self.photo_template.currentText(),
            self.photo_primary.value(),
            self.photo_secondary.value(),
        )
        self.last_similarity = {
            "score": result.score,
            "correlation": result.correlation,
            "overlap": result.structure_overlap,
        }

        fig = self.photo_canvas.figure
        fig.clear()
        axes = fig.subplots(1, 3)
        axes[0].imshow(result.reference, cmap="gray")
        axes[0].set_title("实验照片灰度", color=CHART_FG)
        axes[1].imshow(result.simulation, cmap="magma")
        axes[1].set_title("仿真模板", color=CHART_FG)
        axes[2].imshow(np.abs(result.reference - result.simulation), cmap="viridis")
        axes[2].set_title("差异图", color=CHART_FG)
        for ax in axes:
            ax.set_axis_off()
        fig.patch.set_facecolor(CHART_BG)
        self.photo_canvas.draw_idle()

        self.photo_result.setText(
            f"综合相似度：{result.score * 100:.1f}%；相关系数：{result.correlation:.3f}；结构重叠度：{result.structure_overlap:.3f}。"
        )
        self.update_report_preview()

    def set_polygon_preset(self, sides: int) -> None:
        self.vertex_editor.setPlainText(polygon_to_text(regular_polygon_vertices(sides)))
        self.solve_polygon_mode()

    def solve_polygon_mode(self) -> None:
        try:
            vertices = parse_polygon_vertices(self.vertex_editor.toPlainText())
            result = finite_difference_plate_mode(vertices, self.poly_mode.value(), self.poly_resolution.value())
        except Exception as exc:  # noqa: BLE001
            self.poly_result.setText(f"求解失败：{exc}")
            return

        fig = self.poly_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        im = ax.imshow(result.mode, extent=[0, 1, 0, 1], origin="lower", cmap="RdBu_r", vmin=-1, vmax=1)
        ax.contour(result.x, result.y, np.ma.filled(result.mode, np.nan), levels=[0], colors=CHART_CONTOUR, linewidths=1.2)
        ax.plot(*np.vstack([vertices, vertices[0]]).T, color="#111827", linewidth=1.4)
        ax.set_title("自定义多边形有限差分模态", color=CHART_FG)
        ax.set_aspect("equal")
        ax.tick_params(colors=CHART_TICK)
        fig.colorbar(im, ax=ax, shrink=0.84)
        fig.patch.set_facecolor(CHART_BG)
        self.poly_canvas.draw_idle()

        self.last_polygon_summary = (
            f"多边形顶点数 {len(vertices)}，内部网格点 {result.active_points}，"
            f"第 {self.poly_mode.value()} 阶相对频率 {result.relative_frequency:.2f}。"
        )
        self.poly_result.setText(self.last_polygon_summary)
        self.update_report_preview()

    def solve_metamaterial(self) -> None:
        result = metamaterial_array_response(
            self.meta_rows.value(),
            self.meta_cols.value(),
            self.meta_resonance.value(),
            self.meta_coupling.value(),
            self.meta_damping.value(),
            self.meta_observe.value(),
        )
        fig = self.meta_canvas.figure
        fig.clear()
        ax1, ax2 = fig.subplots(1, 2)
        ax1.plot(result.frequencies, result.transmission_db, color="#0f766e", linewidth=2)
        ax1.axvspan(result.bandgap_start, result.bandgap_end, color="#f59e0b", alpha=0.24)
        ax1.set_title("传输谱与带隙", color=CHART_FG)
        ax1.set_xlabel("频率 / Hz", color=CHART_FG_MUTED)
        ax1.set_ylabel("传输 / dB", color=CHART_FG_MUTED)
        ax1.grid(True, color=CHART_GRID)
        ax1.tick_params(colors=CHART_TICK)

        im = ax2.imshow(result.field, cmap="RdBu_r", vmin=-1, vmax=1, origin="lower")
        ax2.set_title("阵列声场快照", color=CHART_FG)
        ax2.set_xlabel("列", color=CHART_FG_MUTED)
        ax2.set_ylabel("行", color=CHART_FG_MUTED)
        fig.colorbar(im, ax=ax2, shrink=0.78)
        fig.patch.set_facecolor(CHART_BG)
        self.meta_canvas.draw_idle()

        self.last_meta_summary = (
            f"二维阵列 {self.meta_rows.value()}x{self.meta_cols.value()}，"
            f"预测带隙约 {result.bandgap_start:.0f}-{result.bandgap_end:.0f} Hz，"
            f"最低传输 {result.min_transmission:.1f} dB。"
        )
        self.meta_result.setText(self.last_meta_summary)
        self.update_report_preview()

    def update_report_preview(self) -> str:
        similarity = "尚未导入实验照片并计算。"
        if self.last_similarity:
            similarity = (
                f"综合相似度 {self.last_similarity['score'] * 100:.1f}%，"
                f"相关系数 {self.last_similarity['correlation']:.3f}，"
                f"结构重叠度 {self.last_similarity['overlap']:.3f}。"
            )

        polygon = self.last_polygon_summary or "已提供自定义多边形有限差分求解功能，可用于展示任意边界节点线。"
        meta = self.last_meta_summary or "已提供二维声学超材料阵列响应，可展示带隙与局域共振吸声。"
        if hasattr(self, "report_title"):
            title = self.report_title.toPlainText().strip() or "声场与振动可视化虚拟仿真平台实验报告"
        else:
            title = "声场与振动可视化虚拟仿真平台实验报告"

        report = f"""# {title}

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 作品概述

本平台面向大学物理、机械振动与声学实验教学，覆盖一维驻波、二维模态、共振扫描、进阶声学、三维声波与增强分析工具。

## 增强功能结果

- 实验照片相似度：{similarity}
- 自定义多边形薄板：{polygon}
- 二维声学超材料：{meta}

## 物理模型

平台采用解析模态、有限差分近似、受迫振动响应、声场叠加与局域共振阵列模型，形成从基础实验到工程应用的递进结构。

## 误差分析

实验照片与仿真图案的差异可能来自边界夹持、材料非均匀、激励位置偏移、阻尼估计、图像拍摄角度和沙粒分布阈值。

## 课程联系

对应大学物理中的机械波、驻波、干涉、衍射、受迫振动、共振、阻尼、本征值问题和二维/三维场分布。

## 结论

仿真结果、照片相似度和参数分析共同构成实验解释链条，可用于展示声场分布、边界条件影响和工程应用规律。
"""
        if hasattr(self, "report_preview"):
            self.report_preview.setPlainText(report)
        return report

    def generate_report(self) -> None:
        report = self.update_report_preview()
        outputs = Path.cwd() / "outputs"
        outputs.mkdir(exist_ok=True)
        default = outputs / f"simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        path, _ = QFileDialog.getSaveFileName(self, "保存实验报告", str(default), "Markdown 文件 (*.md)")
        if path:
            Path(path).write_text(report, encoding="utf-8")
            self.report_preview.setPlainText(report + f"\n\n报告已保存：{path}\n")
