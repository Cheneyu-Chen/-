from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
