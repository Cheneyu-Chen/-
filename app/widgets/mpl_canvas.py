from __future__ import annotations

import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width: float = 6.0, height: float = 4.0, dpi: int = 100):
        # 配置 matplotlib 支持中文
        matplotlib.rcParams["font.sans-serif"] = [
            "Microsoft YaHei UI",
            "Microsoft YaHei",
            "SimHei",
            "DejaVu Sans",
        ]
        matplotlib.rcParams["axes.unicode_minus"] = False
        self.figure = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        super().__init__(self.figure)

    def clear(self) -> None:
        self.figure.clear()
