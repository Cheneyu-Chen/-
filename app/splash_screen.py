from __future__ import annotations

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from app.theme import APP_TITLE
from app.widgets.common import apply_glass_effect
from app.widgets.glass import AnimatedGlassBackground


class SplashScreen(QWidget):
    finished = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._progress_value = 0
        self._ready_to_enter = False
        self._pulse_value = 0
        self._messages = [
            "正在加载声场与振动模型...",
            "正在初始化二维与三维可视化引擎...",
            "正在准备教学案例与参数预设...",
            "正在进入虚拟仿真实验平台...",
        ]

        self.setWindowTitle(APP_TITLE)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(920, 540)

        shell_layout = QStackedLayout(self)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setStackingMode(QStackedLayout.StackAll)

        self.background = AnimatedGlassBackground()
        self.background.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        shell_layout.addWidget(self.background)

        content = QWidget()
        content.setObjectName("SplashContent")
        content.setAttribute(Qt.WA_StyledBackground, True)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(64, 52, 64, 52)
        content_layout.setSpacing(18)
        shell_layout.addWidget(content)
        shell_layout.setCurrentWidget(content)
        self.background.lower()
        content.raise_()

        content_layout.addStretch(1)

        card = QFrame()
        card.setObjectName("SplashCard")
        apply_glass_effect(card, hoverable=False)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 34, 36, 30)
        card_layout.setSpacing(18)
        content_layout.addWidget(card)

        badge = QLabel("声学实验仿真平台")
        badge.setObjectName("SplashBadge")
        badge.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(badge, 0, Qt.AlignLeft)

        title = QLabel(APP_TITLE)
        title.setObjectName("SplashTitle")
        title.setWordWrap(True)
        card_layout.addWidget(title)

        subtitle = QLabel("三维声波、动态干涉、克拉尼图形、共振扫描与声学超材料的一体化教学仿真平台")
        subtitle.setObjectName("SplashSubtitle")
        subtitle.setWordWrap(True)
        card_layout.addWidget(subtitle)

        feature_row = QHBoxLayout()
        feature_row.setSpacing(10)
        for text in ["动态声场", "三维仿真", "一键案例", "实验对比"]:
            label = QLabel(text)
            label.setObjectName("SplashFeature")
            label.setAlignment(Qt.AlignCenter)
            feature_row.addWidget(label)
        card_layout.addLayout(feature_row)

        self.status_label = QLabel(self._messages[0])
        self.status_label.setObjectName("SplashStatus")
        card_layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        card_layout.addWidget(self.progress)

        self.enter_button = QPushButton("点击进入平台")
        self.enter_button.setObjectName("SplashEnterButton")
        self.enter_button.setCursor(Qt.PointingHandCursor)
        self.enter_button.setVisible(False)
        self.enter_button.clicked.connect(self._enter_platform)
        self.enter_shadow = QGraphicsDropShadowEffect(self.enter_button)
        self.enter_shadow.setBlurRadius(28)
        self.enter_shadow.setOffset(0, 8)
        self.enter_shadow.setColor(QColor(15, 118, 110, 90))
        self.enter_button.setGraphicsEffect(self.enter_shadow)
        card_layout.addWidget(self.enter_button)

        content_layout.addStretch(1)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse_enter_button)

    def start(self) -> None:
        self._timer.start(28)

    def _advance(self) -> None:
        if self._ready_to_enter:
            return

        if self._progress_value < 72:
            self._progress_value += 2
        elif self._progress_value < 94:
            self._progress_value += 1
        else:
            self._progress_value = 100

        self.progress.setValue(self._progress_value)
        message_index = min(len(self._messages) - 1, self._progress_value * len(self._messages) // 101)
        self.status_label.setText(self._messages[message_index])

        if self._progress_value >= 100:
            self._timer.stop()
            self._ready_to_enter = True
            self.status_label.setText("加载完成，请点击进入平台")
            self.enter_button.setVisible(True)
            self.enter_button.setFocus(Qt.OtherFocusReason)
            self._pulse_timer.start(45)

    def _pulse_enter_button(self) -> None:
        self._pulse_value = (self._pulse_value + 1) % 60
        wave = abs(30 - self._pulse_value) / 30
        blur = 22 + int(18 * (1 - wave))
        alpha = 70 + int(75 * (1 - wave))
        self.enter_shadow.setBlurRadius(blur)
        self.enter_shadow.setColor(QColor(15, 118, 110, alpha))
        dots = "." * ((self._pulse_value // 15) % 4)
        self.enter_button.setText(f"点击进入平台{dots}")

    def _enter_platform(self) -> None:
        if not self._ready_to_enter:
            return
        self._pulse_timer.stop()
        self.enter_button.setEnabled(False)
        self.enter_button.setText("正在进入...")
        self.finished.emit()
