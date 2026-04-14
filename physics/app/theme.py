from __future__ import annotations

APP_TITLE = "声场与振动可视化虚拟仿真平台"


def build_stylesheet() -> str:
    return """
    QWidget {
        background-color: #0f172a;
        color: #e5e7eb;
        font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI', sans-serif;
        font-size: 14px;
    }
    QMainWindow {
        background-color: #0b1220;
    }
    QFrame#Card, QFrame#Panel, QListWidget, QTextBrowser, QTabWidget::pane {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
    }
    QLabel#TitleLabel {
        font-size: 28px;
        font-weight: 700;
        color: #f8fafc;
    }
    QLabel#SubtitleLabel {
        font-size: 15px;
        color: #94a3b8;
    }
    QLabel#SectionTitle {
        font-size: 18px;
        font-weight: 600;
        color: #f8fafc;
    }
    QPushButton {
        background-color: #1d4ed8;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 16px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #2563eb;
    }
    QPushButton:pressed {
        background-color: #1e40af;
    }
    QPushButton:disabled {
        background-color: #334155;
        color: #94a3b8;
    }
    QPushButton#NavButton {
        text-align: left;
        padding: 12px 14px;
        background-color: transparent;
        border: 1px solid transparent;
        color: #cbd5e1;
    }
    QPushButton#NavButton:hover {
        background-color: #172554;
        border: 1px solid #1d4ed8;
    }
    QPushButton#NavButton[active='true'] {
        background-color: #1d4ed8;
        border: 1px solid #60a5fa;
        color: white;
    }
    QComboBox, QDoubleSpinBox, QSpinBox {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 6px 10px;
        min-height: 28px;
    }
    QDoubleSpinBox::up-button, QSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 32px;
        border-left: 1px solid #334155;
        border-top-right-radius: 6px;
        background: #1e293b;
    }
    QDoubleSpinBox::up-button:hover, QSpinBox::up-button:hover {
        background: #334155;
    }
    QDoubleSpinBox::down-button, QSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 32px;
        border-left: 1px solid #334155;
        border-bottom-right-radius: 6px;
        background: #1e293b;
    }
    QDoubleSpinBox::down-button:hover, QSpinBox::down-button:hover {
        background: #334155;
    }
    QDoubleSpinBox::up-arrow, QSpinBox::up-arrow {
        image: url(app/up_arrow.svg);
        width: 14px;
        height: 14px;
    }
    QDoubleSpinBox::down-arrow, QSpinBox::down-arrow {
        image: url(app/down_arrow.svg);
        width: 14px;
        height: 14px;
    }
    QListWidget {
        padding: 8px;
    }
    QListWidget::item {
        padding: 10px;
        border-radius: 8px;
    }
    QListWidget::item:selected {
        background-color: #1d4ed8;
        color: white;
    }
    QSlider::groove:horizontal {
        border-radius: 4px;
        height: 8px;
        background: #1f2937;
    }
    QSlider::handle:horizontal {
        background: #60a5fa;
        width: 18px;
        margin: -6px 0;
        border-radius: 9px;
    }
    QTabBar::tab {
        background-color: #111827;
        color: #cbd5e1;
        border: 1px solid #334155;
        padding: 10px 14px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 4px;
    }
    QTabBar::tab:selected {
        background-color: #1d4ed8;
        color: white;
    }
    QScrollArea {
        border: none;
    }
    """
