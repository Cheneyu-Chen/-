from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from app.splash_screen import SplashScreen
from app.theme import build_stylesheet


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(build_stylesheet())

    state: dict[str, object] = {}

    splash = SplashScreen()
    state["splash"] = splash

    def open_main_window() -> None:
        window = MainWindow()
        state["window"] = window
        window.show()
        splash.close()

    splash.finished.connect(open_main_window)
    splash.show()
    splash.start()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
