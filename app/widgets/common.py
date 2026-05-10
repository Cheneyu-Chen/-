from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


def apply_glass_effect(widget: QWidget, hoverable: bool = True) -> None:
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(24)
    shadow.setOffset(0, 10)
    shadow.setColor(QColor(15, 23, 42, 32))
    widget.setGraphicsEffect(shadow)
    widget.setProperty("raised", "false")

    if hoverable:
        widget.setAttribute(Qt.WA_Hover, True)
        hover_filter = _CardHoverFilter(widget, shadow)
        widget._glass_hover_filter = hover_filter
        widget.installEventFilter(hover_filter)


class _SpinBoxInteractionFilter(QObject):
    """Make numeric inputs less twitchy in a dense control panel."""

    def eventFilter(self, watched, event) -> bool:  # noqa: N802
        if event.type() == QEvent.Wheel and isinstance(watched, QAbstractSpinBox):
            if not watched.hasFocus():
                event.ignore()
                return True
        return False


def polish_numeric_inputs(root: QWidget) -> None:
    """Apply consistent, larger hit areas to all spin boxes under *root*."""

    for spin in root.findChildren(QAbstractSpinBox):
        spin.setMinimumWidth(max(spin.minimumWidth(), 156))
        spin.setMinimumHeight(max(spin.minimumHeight(), 34))
        spin.setAccelerated(True)
        spin.setKeyboardTracking(False)
        spin.setAlignment(Qt.AlignCenter)
        spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        spin.setCorrectionMode(QAbstractSpinBox.CorrectionMode.CorrectToNearestValue)
        spin.setAttribute(Qt.WA_Hover, True)
        spin.setProperty("numericInput", "true")

        try:
            line_edit = spin.lineEdit()
            line_edit.setAlignment(Qt.AlignCenter)
            line_edit.setTextMargins(8, 0, 70, 0)
        except RuntimeError:
            pass

        if not hasattr(spin, "_interaction_filter"):
            interaction_filter = _SpinBoxInteractionFilter(spin)
            spin._interaction_filter = interaction_filter
            spin.installEventFilter(interaction_filter)

        spin.style().unpolish(spin)
        spin.style().polish(spin)


class _CardHoverFilter(QObject):
    def __init__(self, widget: QWidget, shadow: QGraphicsDropShadowEffect) -> None:
        super().__init__(widget)
        self.widget = widget
        self.shadow = shadow

    def eventFilter(self, watched, event) -> bool:  # noqa: N802
        if watched is self.widget and event.type() == QEvent.Enter:
            self.widget.setProperty("raised", "true")
            self.shadow.setBlurRadius(34)
            self.shadow.setOffset(0, 14)
            self.shadow.setColor(QColor(15, 23, 42, 48))
            self.widget.style().unpolish(self.widget)
            self.widget.style().polish(self.widget)
        elif watched is self.widget and event.type() == QEvent.Leave:
            self.widget.setProperty("raised", "false")
            self.shadow.setBlurRadius(24)
            self.shadow.setOffset(0, 10)
            self.shadow.setColor(QColor(15, 23, 42, 32))
            self.widget.style().unpolish(self.widget)
            self.widget.style().polish(self.widget)
        return False


def make_card(title: str | None = None) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("Card")
    apply_glass_effect(frame)
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
    apply_glass_effect(frame)
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


def formula_label(*lines: str) -> QLabel:
    label = QLabel("\n".join(lines))
    label.setObjectName("FormulaLabel")
    label.setWordWrap(False)
    label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    return label
