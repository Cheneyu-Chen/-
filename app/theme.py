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
        background-color: transparent;
        color: #111827;
        font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI', sans-serif;
        font-size: 14px;
        font-weight: 400;
    }
    QMainWindow, QStackedWidget {
        background-color: transparent;
        border: none;
    }
    QWidget#MainContent {
        background-color: rgba(255, 255, 255, 0);
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
        font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', 'Consolas', monospace;
        font-size: 13px;
        color: #374151;
    }
    QFrame#SidePanel {
        background-color: rgba(255, 255, 255, 0.58);
        border-right: 1px solid rgba(255, 255, 255, 0.70);
    }
    QLabel[class='nav-label'] {
        padding: 11px 16px;
        border-radius: 8px;
        color: #374151;
        font-size: 14px;
        background-color: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.10);
    }
    QLabel[class='nav-label']:hover {
        background-color: rgba(255, 255, 255, 0.58);
        color: #111827;
        border: 1px solid rgba(20, 184, 166, 0.28);
    }
    QLabel[class='nav-label'][active='true'] {
        background-color: rgba(204, 251, 241, 0.72);
        color: #115e59;
        font-weight: 700;
        border: 1px solid rgba(20, 184, 166, 0.45);
    }
    QFrame#Card {
        background-color: rgba(255, 255, 255, 0.68);
        border: 1px solid rgba(255, 255, 255, 0.78);
        border-radius: 8px;
    }
    QFrame#Card[raised='true'] {
        background-color: rgba(255, 255, 255, 0.78);
        border: 1px solid rgba(20, 184, 166, 0.34);
    }
    QWidget#SplashContent {
        background-color: rgba(255, 255, 255, 0);
    }
    QFrame#SplashCard {
        background-color: rgba(255, 255, 255, 0.70);
        border: 1px solid rgba(255, 255, 255, 0.82);
        border-radius: 8px;
    }
    QLabel#SplashBadge {
        background-color: rgba(204, 251, 241, 0.78);
        border: 1px solid rgba(20, 184, 166, 0.35);
        border-radius: 6px;
        color: #115e59;
        font-size: 13px;
        font-weight: 700;
        padding: 7px 12px;
    }
    QLabel#SplashTitle {
        color: #0f172a;
        font-size: 30px;
        font-weight: 800;
        line-height: 1.15;
    }
    QLabel#SplashSubtitle {
        color: #475569;
        font-size: 15px;
        line-height: 1.45;
    }
    QLabel#SplashFeature {
        background-color: rgba(255, 255, 255, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.76);
        border-radius: 6px;
        color: #334155;
        font-weight: 700;
        padding: 8px 10px;
    }
    QLabel#SplashStatus {
        color: #0f766e;
        font-size: 14px;
        font-weight: 700;
    }
    QProgressBar {
        background-color: rgba(255, 255, 255, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.84);
        border-radius: 6px;
        height: 12px;
    }
    QProgressBar::chunk {
        background-color: #0f766e;
        border-radius: 5px;
    }
    QPushButton {
        background-color: rgba(15, 118, 110, 0.92);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.45);
        border-radius: 6px;
        padding: 8px 14px;
        font-size: 14px;
        font-weight: 700;
        min-height: 32px;
    }
    QPushButton:hover {
        background-color: rgba(13, 148, 136, 0.96);
        border: 1px solid rgba(255, 255, 255, 0.72);
    }
    QPushButton:pressed {
        background-color: rgba(17, 94, 89, 0.96);
    }
    QComboBox, QDoubleSpinBox, QSpinBox {
        background-color: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(255, 255, 255, 0.84);
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 14px;
        color: #111827;
        min-height: 32px;
        selection-background-color: #ccfbf1;
        selection-color: #115e59;
    }
    QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {
        background-color: rgba(255, 255, 255, 0.88);
        border-color: rgba(15, 118, 110, 0.62);
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
        background-color: transparent;
    }
    QComboBox QAbstractItemView {
        background-color: rgba(255, 255, 255, 0.96);
        border: 1px solid rgba(20, 184, 166, 0.22);
        selection-background-color: #ccfbf1;
        selection-color: #115e59;
        outline: none;
        color: #111827;
    }
    QListWidget {
        background-color: rgba(255, 255, 255, 0.52);
        border: 1px solid rgba(255, 255, 255, 0.78);
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
        background-color: rgba(255, 255, 255, 0.72);
    }
    QListWidget::item:selected {
        background-color: rgba(204, 251, 241, 0.82);
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
        background-color: rgba(15, 118, 110, 0.32);
        border-radius: 4px;
        min-height: 32px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: rgba(15, 118, 110, 0.48);
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    """
