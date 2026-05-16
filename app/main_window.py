from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from app.pages.advanced_acoustics_page import AdvancedAcousticsPage
from app.pages.cases_page import CasesPage
from app.pages.compare_page import ComparePage
from app.pages.enhancement_page import EnhancementPage
from app.pages.home_page import HomePage
from app.pages.modes_page import ModesPage
from app.pages.resonance_page import ResonancePage
from app.pages.sound3d_page import Sound3DPage
from app.pages.standing_wave_page import StandingWavePage
from app.theme import APP_TITLE, build_stylesheet
from app.widgets.common import apply_glass_effect, polish_numeric_inputs
from app.widgets.glass import AnimatedGlassBackground


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1280, 800)
        self.setMinimumSize(1024, 640)
        self.setStyleSheet(build_stylesheet())
        self._setup_ui()

    def _setup_ui(self) -> None:
        shell = QWidget()
        shell_layout = QStackedLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setStackingMode(QStackedLayout.StackAll)

        self.background = AnimatedGlassBackground()
        self.background.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        shell_layout.addWidget(self.background)

        main_widget = QWidget()
        main_widget.setObjectName("MainContent")
        main_widget.setAttribute(Qt.WA_StyledBackground, True)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panel = self._create_side_panel()
        main_layout.addWidget(left_panel)

        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(0)
        self.stack = QStackedWidget()
        self._init_pages()
        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_area, 1)

        shell_layout.addWidget(main_widget)
        shell_layout.setCurrentWidget(main_widget)
        self.background.lower()
        main_widget.raise_()
        self.setCentralWidget(shell)
        self._connect_nav_signals()
        self._on_nav_click(self.nav_buttons[0][0], 0)

    def _create_side_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("SidePanel")
        panel.setFixedWidth(260)
        apply_glass_effect(panel, hoverable=False)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 20, 14, 20)
        layout.setSpacing(6)

        logo_label = QLabel("声场与振动\n可视化仿真平台")
        logo_label.setObjectName("TitleLabel")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setWordWrap(True)
        layout.addWidget(logo_label)
        layout.addSpacing(18)

        self.nav_buttons: list[tuple[QLabel, int]] = []
        nav_items = [
            ("平台总览", 0),
            ("一维驻波", 1),
            ("二维模态", 2),
            ("共振扫描", 3),
            ("进阶声学", 4),
            ("三维声波", 5),
            ("教学案例", 6),
            ("增强工具", 7),
            ("实验对比", 8),
        ]
        for name, index in nav_items:
            btn = QLabel(name)
            btn.setProperty("class", "nav-label")
            btn.setProperty("active", "false")
            btn.setAttribute(Qt.WA_Hover, True)
            btn.setCursor(Qt.PointingHandCursor)
            self.nav_buttons.append((btn, index))
            layout.addWidget(btn)

        layout.addStretch(1)

        footer = QLabel("声学仿真平台")
        footer.setObjectName("FooterLabel")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        return panel

    def _init_pages(self) -> None:
        self.home_page = HomePage()
        self.standing_wave_page = StandingWavePage()
        self.modes_page = ModesPage()
        self.resonance_page = ResonancePage()
        self.advanced_page = AdvancedAcousticsPage()
        self.sound3d_page = Sound3DPage()
        self.cases_page = CasesPage()
        self.compare_page = ComparePage()
        self.enhancement_page = EnhancementPage()

        for page in [
            self.home_page,
            self.standing_wave_page,
            self.modes_page,
            self.resonance_page,
            self.advanced_page,
            self.sound3d_page,
            self.cases_page,
            self.enhancement_page,
            self.compare_page,
        ]:
            self.stack.addWidget(page)
            polish_numeric_inputs(page)

        self.cases_page.case_requested.connect(self.apply_case_preset)

    def _connect_nav_signals(self) -> None:
        for btn, index in self.nav_buttons:
            btn.mousePressEvent = lambda event, b=btn, i=index: self._on_nav_click(b, i)

    def _reset_all_pages_animations(self) -> None:
        for i in range(self.stack.count()):
            page = self.stack.widget(i)
            if hasattr(page, 'stop_animation'):
                page.stop_animation()
            if hasattr(page, 'reset_defaults'):
                page.reset_defaults()

    def _on_nav_click(self, btn: QLabel, index: int) -> None:
        self._reset_all_pages_animations()
        self.stack.setCurrentIndex(index)
        self._set_active_nav(index)

    def _set_active_nav(self, index: int) -> None:
        for b, item_index in self.nav_buttons:
            b.setProperty("active", "true" if item_index == index else "false")
            b.style().unpolish(b)
            b.style().polish(b)

    def apply_case_preset(self, preset: dict) -> None:
        self._reset_all_pages_animations()
        target = preset.get("page")
        if target == "standing_wave":
            self.standing_wave_page.apply_preset(preset)
            self.stack.setCurrentIndex(1)
            self._set_active_nav(1)
        elif target == "modes":
            self.modes_page.apply_preset(preset)
            self.stack.setCurrentIndex(2)
            self._set_active_nav(2)
        elif target == "resonance":
            self.resonance_page.apply_preset(preset)
            self.stack.setCurrentIndex(3)
            self._set_active_nav(3)
        elif target == "advanced":
            self.advanced_page.apply_preset(preset)
            self.stack.setCurrentIndex(4)
            self._set_active_nav(4)
        elif target == "sound3d":
            self.sound3d_page.apply_preset(preset)
            self.stack.setCurrentIndex(5)
            self._set_active_nav(5)
