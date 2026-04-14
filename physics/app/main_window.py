from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.pages.cases_page import CasesPage
from app.pages.compare_page import ComparePage
from app.pages.home_page import HomePage
from app.pages.modes_page import ModesPage
from app.pages.resonance_page import ResonancePage
from app.pages.standing_wave_page import StandingWavePage
from app.theme import APP_TITLE, build_stylesheet


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1280, 800)
        self.setMinimumSize(1024, 640)

        self.setStyleSheet(build_stylesheet())

        self._setup_ui()

    def _setup_ui(self) -> None:
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panel, left_layout = self._create_side_panel()
        main_layout.addWidget(left_panel)

        self.stack = QStackedWidget()
        self._init_pages()
        main_layout.addWidget(self.stack)

        self.setCentralWidget(main_widget)
        self._connect_nav_signals()

    def _create_side_panel(self) -> tuple[QFrame, QVBoxLayout]:
        panel = QFrame()
        panel.setFixedWidth(260)
        panel.setStyleSheet("background-color:#0b1220;border-right:1px solid #1f2937;")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(4)

        logo_label = QLabel("声场与振动可视化\n虚拟仿真平台")
        logo_label.setObjectName("TitleLabel")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setWordWrap(True)
        layout.addWidget(logo_label)
        layout.addSpacing(20)

        self.nav_buttons: list[tuple[str, int, QWidget]] = []
        nav_items = [
            ("首页", 0),
            ("一维驻波", 1),
            ("二维模态", 2),
            ("共振扫描", 3),
            ("教学案例", 4),
            ("实验对照", 5),
        ]
        for name, index in nav_items:
            btn = QLabel(name)
            btn.setProperty("class", "nav-label")
            btn.setStyleSheet("""
                QLabel[class='nav-label'] {
                    padding: 12px 16px;
                    border-radius: 10px;
                    color: #cbd5e1;
                    font-size: 15px;
                    background-color: transparent;
                }
                QLabel[class='nav-label']:hover {
                    background-color: #172554;
                    color: #e5e7eb;
                }
                QLabel[class='nav-label'][active='true'] {
                    background-color: #1d4ed8;
                    color: white;
                    font-weight: 600;
                }
            """)
            btn.setCursor(Qt.PointingHandCursor)
            self.nav_buttons.append((btn, index))
            layout.addWidget(btn)

        layout.addStretch(1)

        footer = QLabel("v1.0 参赛首版")
        footer.setStyleSheet("color:#475569;font-size:12px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        return panel, layout

    def _init_pages(self) -> None:
        self.stack.addWidget(HomePage())
        self.stack.addWidget(StandingWavePage())
        self.stack.addWidget(ModesPage())
        self.stack.addWidget(ResonancePage())
        self.stack.addWidget(CasesPage())
        self.stack.addWidget(ComparePage())

    def _connect_nav_signals(self) -> None:
        for btn, index in self.nav_buttons:
            btn.mousePressEvent = lambda e, b=btn, i=index: self._on_nav_click(b, i)

    def _on_nav_click(self, btn: QLabel, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for b, _ in self.nav_buttons:
            b.setProperty("active", "false")
            b.style().unpolish(b)
            b.style().polish(b)
        btn.setProperty("active", "true")
        btn.style().unpolish(btn)
        btn.style().polish(btn)
