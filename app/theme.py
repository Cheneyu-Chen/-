from __future__ import annotations

APP_TITLE = "声场与振动可视化虚拟仿真平台"

CHART_BG = "#ffffff"
CHART_FG = "#111827"
CHART_FG_MUTED = "#6b7280"
CHART_SPINE = "#d1d5db"
CHART_TICK = "#374151"
CHART_GRID = "#e5e7eb"
CHART_LINE_PRIMARY = "#2563eb"
CHART_LINE_AMBER = "#f59e0b"
CHART_LINE_GREEN = "#16a34a"
CHART_LINE_RED = "#dc2626"
CHART_NODE_LINE = "#6b7280"
CHART_CONTOUR = "#0f766e"
CHART_LEGEND_FC = "#ffffff"
CHART_LEGEND_EC = "#e5e7eb"


def build_stylesheet() -> str:
    return """
    QWidget {
        background-color: #f3f4f6;
        color: #111827;
        font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI', sans-serif;
        font-size: 14px;
        font-weight: 400;
    }
    QMainWindow, QStackedWidget {
        background-color: #f3f4f6;
        border: none;
    }
    QLabel {
        background-color: transparent;
        border: none;
    }
    QLabel#TitleLabel {
        font-size: 20px;
        font-weight: 700;
        color: #111827;
    }
    QLabel#SubtitleLabel, QLabel#MutedLabel {
        font-size: 14px;
        color: #6b7280;
        line-height: 1.45;
    }
    QLabel#SectionTitle {
        font-size: 16px;
        font-weight: 700;
        color: #111827;
    }
    QLabel#MetricTitle {
        font-size: 12px;
        color: #6b7280;
    }
    QLabel#MetricValue {
        font-size: 20px;
        font-weight: 700;
        color: #111827;
    }
    QLabel#MetricHint {
        font-size: 12px;
        color: #6b7280;
    }
    QLabel#FooterLabel {
        font-size: 12px;
        color: #9ca3af;
    }
    QLabel#CodeLabel {
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 13px;
        color: #374151;
    }
    QFrame#SidePanel {
        background-color: #f9fafb;
        border-right: 1px solid #e5e7eb;
    }
    QLabel[class='nav-label'] {
        padding: 10px 16px;
        border-radius: 6px;
        color: #374151;
        font-size: 14px;
        background-color: transparent;
    }
    QLabel[class='nav-label']:hover {
        background-color: #eef2ff;
        color: #111827;
    }
    QLabel[class='nav-label'][active='true'] {
        background-color: #e0f2fe;
        color: #0f766e;
        font-weight: 700;
    }
    QFrame#Card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
    }
    QPushButton {
        background-color: #0f766e;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px 14px;
        font-size: 14px;
        font-weight: 700;
        min-height: 32px;
    }
    QPushButton:hover {
        background-color: #0d9488;
    }
    QPushButton:pressed {
        background-color: #115e59;
    }
    QComboBox, QDoubleSpinBox, QSpinBox {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 14px;
        color: #111827;
        min-height: 32px;
        selection-background-color: #ccfbf1;
        selection-color: #115e59;
    }
    QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {
        border-color: #0f766e;
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
        background-color: transparent;
    }
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        selection-background-color: #ccfbf1;
        selection-color: #115e59;
        outline: none;
        color: #111827;
    }
    QDoubleSpinBox::up-button, QSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 28px;
        border-left: 1px solid #d1d5db;
        background-color: #f9fafb;
    }
    QDoubleSpinBox::down-button, QSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 28px;
        border-left: 1px solid #d1d5db;
        background-color: #f9fafb;
    }
    QDoubleSpinBox::up-arrow, QSpinBox::up-arrow {
        image: url(app/up_arrow.svg);
        width: 12px;
        height: 12px;
    }
    QDoubleSpinBox::down-arrow, QSpinBox::down-arrow {
        image: url(app/down_arrow.svg);
        width: 12px;
        height: 12px;
    }
    QListWidget {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 8px;
        outline: none;
    }
    QListWidget::item {
        padding: 10px 12px;
        border-radius: 6px;
        color: #374151;
        background-color: transparent;
    }
    QListWidget::item:hover {
        background-color: #f9fafb;
    }
    QListWidget::item:selected {
        background-color: #ccfbf1;
        color: #115e59;
        font-weight: 700;
    }
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollBar:vertical {
        background-color: transparent;
        width: 8px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background-color: #d1d5db;
        border-radius: 4px;
        min-height: 32px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    """
