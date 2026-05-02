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

from app.core.advanced_acoustics import (
    diffraction_field,
    helmholtz_absorber_response,
    interference_field,
    phononic_chain_dispersion,
)
from app.theme import (
    CHART_BG,
    CHART_FG,
    CHART_FG_MUTED,
    CHART_GRID,
    CHART_LINE_AMBER,
    CHART_LINE_GREEN,
    CHART_LINE_PRIMARY,
    CHART_LINE_RED,
    CHART_SPINE,
    CHART_TICK,
)
from app.widgets.common import make_card, muted_label
from app.widgets.mpl_canvas import MplCanvas


class AdvancedAcousticsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.time_value = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        control_card, control_layout = make_card("进阶声学实验")
        form = QFormLayout()
        form.setSpacing(10)

        self.experiment_box = QComboBox()
        self.experiment_box.addItems(["双声源干涉", "单缝声衍射", "一维声子晶体带隙", "亥姆霍兹共鸣吸声"])
        self.experiment_box.currentIndexChanged.connect(self.refresh_plot)

        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(80.0, 5000.0)
        self.freq_spin.setSingleStep(20.0)
        self.freq_spin.setValue(800.0)
        self.freq_spin.valueChanged.connect(self.refresh_plot)

        self.param_a = QDoubleSpinBox()
        self.param_a.setRange(0.05, 10.0)
        self.param_a.setSingleStep(0.05)
        self.param_a.setValue(0.50)
        self.param_a.valueChanged.connect(self.refresh_plot)

        self.param_b = QDoubleSpinBox()
        self.param_b.setRange(0.0, 20.0)
        self.param_b.setSingleStep(0.05)
        self.param_b.setValue(0.00)
        self.param_b.valueChanged.connect(self.refresh_plot)

        form.addRow("实验类型", self.experiment_box)
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
            "播放后，干涉图会显示相位推进，衍射图会显示扫描位置，带隙和吸声响应会显示运动的频率游标，"
            "用于把静态公式转化为可观察的实验过程。"
        ))
        control_layout.addWidget(note_card)
        control_layout.addStretch(1)
        root.addWidget(control_card, 0)

        right = QVBoxLayout()
        right.setSpacing(12)
        plot_card, plot_layout = make_card("动态仿真图像")
        self.canvas = MplCanvas(width=7.8, height=4.6, dpi=100)
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
        experiment = self.experiment_box.currentText()
        if experiment == "双声源干涉":
            self._plot_interference(fig)
        elif experiment == "单缝声衍射":
            self._plot_diffraction(fig)
        elif experiment == "一维声子晶体带隙":
            self._plot_bandgap(fig)
        else:
            self._plot_helmholtz(fig)
        fig.patch.set_facecolor(CHART_BG)
        self.canvas.draw_idle()

    def _style_axis(self, ax) -> None:
        ax.set_facecolor(CHART_BG)
        ax.tick_params(colors=CHART_TICK)
        ax.grid(True, color=CHART_GRID, alpha=0.65, linewidth=0.8)
        for spine in ax.spines.values():
            spine.set_color(CHART_SPINE)

    def _plot_interference(self, fig) -> None:
        spacing = self.param_a.value()
        phase = self.param_b.value() + 2.0 * self.time_value
        xx, yy, intensity = interference_field(self.freq_spin.value(), spacing, phase)
        ax = fig.add_subplot(111)
        im = ax.imshow(intensity, extent=[xx.min(), xx.max(), yy.min(), yy.max()], origin="lower", cmap="viridis")
        ax.scatter([-spacing / 2, spacing / 2], [0, 0], color="white", edgecolor="black", s=60, zorder=5)
        ax.set_title("双声源干涉声强分布", color=CHART_FG)
        ax.set_xlabel("x / m", color=CHART_FG_MUTED)
        ax.set_ylabel("y / m", color=CHART_FG_MUTED)
        self._style_axis(ax)
        fig.colorbar(im, ax=ax, shrink=0.86)
        self.param_hint.setText("参数 A：声源间距 d / m；参数 B：初始相位差 Δφ / rad。")
        self.summary_label.setText(f"相位正在推进：等效相位差 Δφ={phase:.2f} rad。亮纹与暗纹会随相位变化发生移动。")

    def _plot_diffraction(self, fig) -> None:
        slit_width = self.param_a.value()
        screen_distance = max(self.param_b.value(), 0.2)
        x, envelope, wavelength = diffraction_field(self.freq_spin.value(), slit_width, screen_distance)
        ax = fig.add_subplot(111)
        ax.plot(x, envelope, color=CHART_LINE_PRIMARY, linewidth=2.2)
        ax.fill_between(x, envelope, color=CHART_LINE_PRIMARY, alpha=0.18)
        scan_x = x[int((self.time_value * 60) % len(x))]
        ax.axvline(scan_x, color=CHART_LINE_RED, linestyle="--", linewidth=1.8, label="扫描位置")
        ax.scatter([scan_x], [envelope[int((self.time_value * 60) % len(x))]], color=CHART_LINE_RED, s=55, zorder=5)
        ax.set_title("单缝声衍射强度包络", color=CHART_FG)
        ax.set_xlabel("屏上横向位置 / m", color=CHART_FG_MUTED)
        ax.set_ylabel("归一化强度", color=CHART_FG_MUTED)
        self._style_axis(ax)
        self.param_hint.setText("参数 A：缝宽 a / m；参数 B：屏距 L / m。")
        self.summary_label.setText(f"波长 λ={wavelength:.3f} m。红色游标模拟探头沿屏幕扫描衍射强度。")

    def _plot_bandgap(self, fig) -> None:
        mass_ratio = self.param_a.value()
        stiffness_ratio = max(self.param_b.value(), 0.05)
        q, acoustic, optical, gap = phononic_chain_dispersion(mass_ratio, stiffness_ratio)
        ax = fig.add_subplot(111)
        ax.plot(q, acoustic, color=CHART_LINE_PRIMARY, linewidth=2.2, label="声学支")
        ax.plot(q, optical, color=CHART_LINE_RED, linewidth=2.2, label="光学支")
        if optical.min() > acoustic.max():
            ax.axhspan(acoustic.max(), optical.min(), color=CHART_LINE_AMBER, alpha=0.22, label="带隙")
        cursor = (self.time_value * 0.35) % 1.0
        ax.axvline(cursor, color=CHART_LINE_GREEN, linestyle="--", linewidth=1.8, label="波矢扫描")
        ax.set_title("一维双原胞声子晶体色散关系", color=CHART_FG)
        ax.set_xlabel("归一化波矢 q/π", color=CHART_FG_MUTED)
        ax.set_ylabel("归一化角频率", color=CHART_FG_MUTED)
        self._style_axis(ax)
        leg = ax.legend(loc="best")
        for text in leg.get_texts():
            text.set_color(CHART_FG)
        self.param_hint.setText("参数 A：质量比 m₂/m₁；参数 B：刚度比 k₂/k₁。")
        self.summary_label.setText(f"归一化带隙宽度约 {gap:.3f}。绿色游标模拟波矢扫描，带隙区间内没有传播模态。")

    def _plot_helmholtz(self, fig) -> None:
        resonant_frequency = self.freq_spin.value()
        damping = max(self.param_a.value(), 0.01)
        freqs, absorption, bandwidth = helmholtz_absorber_response(resonant_frequency, damping)
        ax = fig.add_subplot(111)
        ax.plot(freqs, absorption, color=CHART_LINE_PRIMARY, linewidth=2.2)
        ax.axvline(resonant_frequency, color=CHART_LINE_RED, linestyle="--", linewidth=1.6, label="共鸣频率")
        cursor = freqs[int((self.time_value * 40) % len(freqs))]
        ax.axvline(cursor, color=CHART_LINE_GREEN, linestyle=":", linewidth=1.8, label="扫频游标")
        ax.set_title("亥姆霍兹共鸣吸声响应", color=CHART_FG)
        ax.set_xlabel("频率 / Hz", color=CHART_FG_MUTED)
        ax.set_ylabel("吸声系数", color=CHART_FG_MUTED)
        ax.set_ylim(0, 1.05)
        self._style_axis(ax)
        leg = ax.legend(loc="best")
        for text in leg.get_texts():
            text.set_color(CHART_FG)
        self.param_hint.setText("频率：共鸣频率 f₀ / Hz；参数 A：阻尼系数 ζ；参数 B 不使用。")
        self.summary_label.setText(f"半吸收带宽约 {bandwidth:.1f} Hz。绿色游标模拟扫频实验，接近 f₀ 时吸声最强。")

    def on_tick(self) -> None:
        self.time_value += 0.04
        self.refresh_plot()

    def start_animation(self) -> None:
        self.timer.start(55)

    def stop_animation(self) -> None:
        self.timer.stop()

    def reset_animation(self) -> None:
        self.time_value = 0.0
        self.refresh_plot()

    def apply_preset(self, preset: dict) -> None:
        experiment = preset.get("experiment")
        if experiment:
            for index in range(self.experiment_box.count()):
                if self.experiment_box.itemText(index) == experiment:
                    self.experiment_box.setCurrentIndex(index)
                    break
        self.freq_spin.setValue(float(preset.get("frequency", self.freq_spin.value())))
        self.param_a.setValue(float(preset.get("param_a", self.param_a.value())))
        self.param_b.setValue(float(preset.get("param_b", self.param_b.value())))
        self.time_value = 0.0
        self.refresh_plot()

    def export_figure(self) -> None:
        outputs = Path.cwd() / "outputs"
        outputs.mkdir(exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "导出进阶声学图像", str(outputs / "advanced_acoustics.png"), "PNG 图像 (*.png)")
        if path:
            self.canvas.figure.savefig(path, dpi=180, facecolor=self.canvas.figure.get_facecolor(), bbox_inches="tight")
