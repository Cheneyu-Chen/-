from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

SITE_PACKAGES = Path(__file__).resolve().parents[2] / ".venv_local" / "Lib" / "site-packages"
if SITE_PACKAGES.exists():
    sys.path.insert(0, str(SITE_PACKAGES))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from app.pages.advanced_acoustics_page import AdvancedAcousticsPage
from PySide6.QtWidgets import QApplication


class AdvancedAcousticsPageImportTest(unittest.TestCase):
    def test_page_exposes_diffraction_animation_hooks(self) -> None:
        self.assertTrue(hasattr(AdvancedAcousticsPage, "_plot_diffraction"))
        self.assertTrue(hasattr(AdvancedAcousticsPage, "_reset_diffraction_memory"))

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_single_slit_page_refreshes_in_offscreen_mode(self) -> None:
        page = AdvancedAcousticsPage()
        page.experiment_box.setCurrentIndex(1)
        page.refresh_plot()
        self.assertIsNotNone(page.diffraction_screen_exposure)
        self.assertGreaterEqual(len(page.canvas.figure.axes), 2)
