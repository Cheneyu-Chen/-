from __future__ import annotations

from pathlib import Path

import numpy as np
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
from app.widgets.common import make_card, muted_label
from app.widgets.mpl_canvas import MplCanvas


class ResonancePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        control_card, control_layout = make_card("扫描参数设置")
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
        self.points.setValue(200)

        form.addRow("起始频率 / Hz", self.start_freq)
        form.addRow("结束频率 / Hz", self.end_freq)
        form.addRow("固有频率 / Hz", self.natural_freq)
        form.addRow("阻尼系数", self.damping)
        form.addRow("扫描点数", int(self.points.value()))
        control_layout.addLayout(form)

        buttons = QHBoxLayout()
        scan_btn = QPushButton("开始扫描")
        export_btn = QPushButton("导出数据")
        scan_btn.clicked.connect(self.run_scan)
        export_btn.clicked.connect(self.export_data)
        buttons.addWidget(scan_btn)
        buttons.addWidget(export_btn)
        control_layout.addLayout(buttons)

        note_card, note_layout = make_card("教学说明")
        note_layout.addWidget(muted_label(
            "• 共振扫描通过缓慢改变驱动频率，观察系统响应变化。\n"
            "• 响应峰值出现的位置对应系统的固有频率附近。\n"
            "• 阻尼增大时，共振峰变宽、峰值降低；阻尼减小时，峰变尖锐。"
        ))
        control_layout.addWidget(note_card)
        control_layout.addStretch(1)
        root.addWidget(control_card, 0)

        right = QVBoxLayout()
        right.setSpacing(12)
        plot_card, plot_layout = make_card("频率响应曲线")
        self.canvas = MplCanvas(width=7.6, height=4.5, dpi=100)
        plot_layout.addWidget(self.canvas)
        right.addWidget(plot_card, 3)

        summary_card, summary_layout = make_card("结果解读")
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)
        right.addWidget(summary_card, 1)

        right_container = QWidget()
        right_container.setLayout(right)
        root.addWidget(right_container, 1)

        self.run_scan()

    def run_scan(self) -> None:
        freqs, response, peaks = scan_resonance(
            start_freq=self.start_freq.value(),
            end_freq=self.end_freq.value(),
            points=int(self.points.value()),
            natural_frequency=self.natural_freq.value(),
            damping=self.damping.value(),
        )

        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(freqs, response, color="#60a5fa", linewidth=2.0)
        ax.scatter(freqs[peaks], response[peaks], color="#ef4444", s=80, zorder=5, label="共振峰")
        ax.axvline(self.natural_freq.value(), color="#334155", linestyle="--", linewidth=1.5, label="固有频率")
        ax.set_title("系统频率响应与共振峰", color="#e5e7eb")
        ax.set_xlabel("驱动频率 / Hz", color="#cbd5e1")
        ax.set_ylabel("响应强度", color="#cbd5e1")
        ax.grid(True, alpha=0.15)
        ax.set_facecolor("#0f172a")
        for spine in ax.spines.values():
            spine.set_color("#475569")
        ax.tick_params(colors="#cbd5e1")
        leg = ax.legend(facecolor="#111827", edgecolor="#334155")
        for text in leg.get_texts():
            text.set_color("#e5e7eb")
        fig.patch.set_facecolor("#111827")
        self.canvas.draw_idle()

        peak_info = ""
        if len(peaks) > 0:
            peak_freqs = freqs[peaks]
            peak_info = f"扫描到 {len(peaks)} 个响应峰值，峰值位置分别为：{', '.join(f'{f:.2f} Hz' for f in peak_freqs)}。"
        else:
            peak_info = "扫描范围内未检测到明显峰值，可尝试调整固有频率或扫描范围。"

        self.summary_label.setText(
            f"已从 {self.start_freq.value():.2f} Hz 扫描至 {self.end_freq.value():.2f} Hz，"
            f"系统固有频率设定为 {self.natural_freq.value():.2f} Hz，阻尼系数为 {self.damping.value():.2f}。"
            f"{peak_info}阻尼系数越小，共振峰越尖锐；增大阻尼会使共振峰变宽且峰值降低。"
        )
        self.last_freqs = freqs
        self.last_response = response

    def export_data(self) -> None:
        if not hasattr(self, "last_freqs"):
            return
        outputs = Path.cwd() / "outputs"
        outputs.mkdir(exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "导出共振扫描数据", str(outputs / "resonance_scan.txt"), "文本文件 (*.txt)")
        if path:
            data = np.column_stack([self.last_freqs, self.last_response])
            np.savetxt(path, data, header="频率,响应强度", fmt="%.6f", delimiter=",", encoding="utf-8")
