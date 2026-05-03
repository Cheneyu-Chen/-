from __future__ import annotations

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
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
        self._finished_emitted = False
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

        badge = QLabel("最终参赛展示版  v2.0")
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

        content_layout.addStretch(1)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)

    def start(self) -> None:
        self._timer.start(28)

    def _advance(self) -> None:
        if self._finished_emitted:
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
            self._finished_emitted = True
            QTimer.singleShot(220, self.finished.emit)
