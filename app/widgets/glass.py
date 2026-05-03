from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QTimer, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


class AnimatedGlassBackground(QWidget):
    """A subtle animated background that makes translucent panels read as glass."""

    def __init__(self) -> None:
        super().__init__()
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

    def _tick(self) -> None:
        self._phase = (self._phase + 0.012) % (math.tau * 1000)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        base = QLinearGradient(QPointF(0, 0), QPointF(rect.width(), rect.height()))
        base.setColorAt(0.00, QColor("#eaf7f5"))
        base.setColorAt(0.38, QColor("#f8fbff"))
        base.setColorAt(0.68, QColor("#fff7ed"))
        base.setColorAt(1.00, QColor("#eef2ff"))
        painter.fillRect(rect, base)

        self._draw_band(painter, rect.width(), rect.height(), QColor(20, 184, 166, 40), 0.00, 0.16)
        self._draw_band(painter, rect.width(), rect.height(), QColor(56, 189, 248, 34), 1.80, 0.22)
        self._draw_band(painter, rect.width(), rect.height(), QColor(245, 158, 11, 28), 3.20, 0.28)

        pen = QPen(QColor(255, 255, 255, 75), 1.0)
        painter.setPen(pen)
        step = 88
        drift = int((math.sin(self._phase * 0.55) + 1.0) * 10)
        for x in range(-step, rect.width() + step, step):
            painter.drawLine(x + drift, 0, x + drift - 48, rect.height())
        for y in range(-step, rect.height() + step, step):
            painter.drawLine(0, y - drift, rect.width(), y + drift + 34)

    def _draw_band(self, painter: QPainter, width: int, height: int, color: QColor, offset: float, amplitude: float) -> None:
        if width <= 0 or height <= 0:
            return

        path = QPainterPath()
        start_y = height * (0.28 + amplitude * math.sin(self._phase + offset))
        path.moveTo(-40, start_y)
        segments = 8
        for i in range(segments + 1):
            x = width * i / segments
            y = height * (0.34 + amplitude * math.sin(self._phase + offset + i * 0.72))
            c1 = QPointF(x - width / segments * 0.55, y - height * 0.10)
            c2 = QPointF(x - width / segments * 0.20, y + height * 0.10)
            path.cubicTo(c1, c2, QPointF(x, y))

        path.lineTo(width + 40, height)
        path.lineTo(-40, height)
        path.closeSubpath()
        painter.fillPath(path, color)
