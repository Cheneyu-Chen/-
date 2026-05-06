from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.resonance import scan_resonance
from app.theme import (
    CHART_BG, CHART_FG, CHART_FG_MUTED, CHART_GRID, CHART_LEGEND_EC,
    CHART_LEGEND_FC, CHART_LINE_PRIMARY, CHART_LINE_RED, CHART_NODE_LINE,
    CHART_SPINE, CHART_TICK,
)
from app.widgets.common import formula_label, make_card, muted_label
from app.widgets.mpl_canvas import MplCanvas


class ResonancePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        control_card, control_layout = make_card("频率扫描参数")
        form = QFormLayout()
        form.setSpacing(10)

        self.start_freq = QDoubleSpinBox()
        self.start_freq.setRange(0.1, 8.0)
        self.start_freq.setSingleStep(0.1)
        self.start_freq.setValue(0.5)

        self.end_freq = QDoubleSpinBox()
        self.end_freq.setRange(0.5, 10.0)
        self.end_freq.setSingleStep(0.1)
        self.end_freq.setValue(4.0)

        self.natural_freq = QDoubleSpinBox()
        self.natural_freq.setRange(0.1, 10.0)
        self.natural_freq.setSingleStep(0.1)
        self.natural_freq.setValue(2.0)

        self.damping = QDoubleSpinBox()
        self.damping.setRange(0.01, 1.0)
        self.damping.setSingleStep(0.02)
        self.damping.setValue(0.08)

        self.points = QDoubleSpinBox()
        self.points.setDecimals(0)
        self.points.setRange(50, 1000)
        self.points.setSingleStep(50)
        self.points.setValue(240)

        form.addRow("起始频率 / Hz", self.start_freq)
        form.addRow("终止频率 / Hz", self.end_freq)
        form.addRow("本征频率 / Hz", self.natural_freq)
        form.addRow("阻尼比 ζ", self.damping)
        form.addRow("采样点数", self.points)
        control_layout.addLayout(form)

        buttons = QHBoxLayout()
        scan_btn = QPushButton("扫描频率")
        export_btn = QPushButton("导出数据")
        scan_btn.clicked.connect(self.run_scan)
        export_btn.clicked.connect(self.export_data)
        buttons.addWidget(scan_btn)
        buttons.addWidget(export_btn)
        control_layout.addLayout(buttons)

        note_card, note_layout = make_card("理论对应")
        note_layout.addWidget(formula_label(
            "频率比：r = f / fₙ",
            "幅频响应：|A| = 1 / √[(1 - r²)² + (2ζr)²]",
            "品质因数：Q ≈ 1 / (2ζ)",
            "共振条件：f ≈ fₙ",
        ))
        note_layout.addWidget(muted_label(
            "每一条公式单独成行显示。驱动频率接近本征频率时响应达到峰值；阻尼越小，峰越高且带宽越窄。"
        ))
        control_layout.addWidget(note_card)
        control_layout.addStretch(1)
        root.addWidget(control_card, 0)

        right = QVBoxLayout()
        right.setSpacing(12)
        plot_card, plot_layout = make_card("共振峰自动识别")
        self.canvas = MplCanvas(width=7.6, height=4.5, dpi=100)
        plot_layout.addWidget(self.canvas)
        right.addWidget(plot_card, 3)

        summary_card, summary_layout = make_card("仿真解释")
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)
        right.addWidget(summary_card, 1)

        right_container = QWidget()
        right_container.setLayout(right)
        root.addWidget(right_container, 1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.anim_index = 0
        self.freq_data = np.array([])
        self.resp_data = np.array([])
        self.peaks_indices = []
        self.run_scan()

    def run_scan(self) -> None:
        self.timer.stop()
        start = min(self.start_freq.value(), self.end_freq.value() - 0.01)
        end = max(self.end_freq.value(), start + 0.01)
        freqs, response, peaks = scan_resonance(
            start_freq=start,
            end_freq=end,
            points=int(self.points.value()),
            natural_frequency=self.natural_freq.value(),
            damping=self.damping.value(),
        )

        fig = self.canvas.figure
        fig.clear()
        self.ax = fig.add_subplot(111)
        self.line, = self.ax.plot([], [], color=CHART_LINE_PRIMARY, linewidth=2.0, label="响应曲线")
        self.peak_scatter = self.ax.scatter([], [], color=CHART_LINE_RED, s=80, zorder=5, label="识别峰值")
        self.ax.axvline(self.natural_freq.value(), color=CHART_NODE_LINE, linestyle="--", linewidth=1.5, label="本征频率")
        self.ax.set_xlim(start, end)
        max_resp = np.max(response) if len(response) > 0 else 1.0
        self.ax.set_ylim(0, max_resp * 1.08 if max_resp > 0 else 1.0)
        self.ax.set_title("受迫振动幅频响应", color=CHART_FG)
        self.ax.set_xlabel("驱动频率 / Hz", color=CHART_FG_MUTED)
        self.ax.set_ylabel("归一化响应幅值", color=CHART_FG_MUTED)
        self.ax.grid(True, alpha=0.6, color=CHART_GRID, linewidth=0.8)
        self.ax.set_facecolor(CHART_BG)
        for spine in self.ax.spines.values():
            spine.set_color(CHART_SPINE)
        self.ax.tick_params(colors=CHART_TICK)
        leg = self.ax.legend(loc="upper right", facecolor=CHART_LEGEND_FC, edgecolor=CHART_LEGEND_EC)
        for text in leg.get_texts():
            text.set_color(CHART_FG)
        fig.patch.set_facecolor(CHART_BG)
        self.canvas.draw_idle()

        if len(peaks) > 0:
            peak_freqs = freqs[peaks]
            peak_values = response[peaks]
            peak_info = "；".join(f"{f:.2f} Hz，响应 {a:.2f}" for f, a in zip(peak_freqs, peak_values))
        else:
            peak_info = "扫描区间内未识别到显著峰值，请扩大频率范围或降低阻尼。"
        q_factor = 1 / max(2 * self.damping.value(), 1e-6)
        self.summary_label.setText(
            f"扫描范围 {start:.2f}-{end:.2f} Hz，本征频率 {self.natural_freq.value():.2f} Hz，"
            f"阻尼比 {self.damping.value():.2f}，估计 Q 值约 {q_factor:.1f}。"
            f"峰值结果：{peak_info}。这组数据可用于说明共振峰、半功率带宽和阻尼之间的关系。"
        )
        self.last_freqs = freqs
        self.last_response = response

        self.anim_index = 0
        self.freq_data = freqs
        self.resp_data = response
        self.peaks_indices = peaks
        self.points_per_frame = max(1, len(freqs) // 60)
        self.timer.start(16)

    def update_animation(self) -> None:
        self.anim_index += self.points_per_frame
        if self.anim_index >= len(self.freq_data):
            self.anim_index = len(self.freq_data)
            self.timer.stop()

        current_freqs = self.freq_data[:self.anim_index]
        current_resp = self.resp_data[:self.anim_index]
        self.line.set_data(current_freqs, current_resp)

        current_peaks = [p for p in self.peaks_indices if p < self.anim_index]
        if current_peaks:
            self.peak_scatter.set_offsets(np.column_stack((self.freq_data[current_peaks], self.resp_data[current_peaks])))
        else:
            self.peak_scatter.set_offsets(np.empty((0, 2)))
        self.canvas.draw_idle()

    def apply_preset(self, preset: dict) -> None:
        self.start_freq.setValue(float(preset.get("start", self.start_freq.value())))
        self.end_freq.setValue(float(preset.get("end", self.end_freq.value())))
        self.natural_freq.setValue(float(preset.get("natural", self.natural_freq.value())))
        self.damping.setValue(float(preset.get("damping", self.damping.value())))
        self.points.setValue(float(preset.get("points", self.points.value())))
        self.run_scan()

    def export_data(self) -> None:
        if not hasattr(self, "last_freqs"):
            return
        outputs = Path.cwd() / "outputs"
        outputs.mkdir(exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "导出共振扫描数据", str(outputs / "resonance_scan.txt"), "文本文件 (*.txt)")
        if path:
            data = np.column_stack([self.last_freqs, self.last_response])
            np.savetxt(path, data, header="frequency_hz,response", fmt="%.6f", delimiter=",", encoding="utf-8")
