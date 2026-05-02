from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


def make_card(title: str | None = None) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)
    if title:
        label = QLabel(title)
        label.setObjectName("SectionTitle")
        layout.addWidget(label)
    return frame, layout


def make_metric(title: str, value: str, hint: str = "") -> QFrame:
    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(4)
    title_label = QLabel(title)
    title_label.setObjectName("MetricTitle")
    value_label = QLabel(value)
    value_label.setObjectName("MetricValue")
    layout.addWidget(title_label)
    layout.addWidget(value_label)
    if hint:
        hint_label = QLabel(hint)
        hint_label.setObjectName("MetricHint")
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)
    return frame


def two_col_row(left: QWidget, right: QWidget) -> QWidget:
    wrapper = QWidget()
    layout = QHBoxLayout(wrapper)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(16)
    layout.addWidget(left, 1)
    layout.addWidget(right, 1)
    return wrapper


def muted_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("MutedLabel")
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    return label
