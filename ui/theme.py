import ctypes
import sys
from ctypes import wintypes


APP_QSS = """
* {
    font-family: "Segoe UI";
    font-size: 11px;
}

QMainWindow,
QWidget {
    background-color: #182028;
    color: #E7EDF3;
}

QMenuBar {
    background-color: #141B21;
    color: #E7EDF3;
    border-bottom: 1px solid #34404A;
    padding: 2px;
}

QMenuBar::item {
    background: transparent;
    padding: 4px 8px;
}

QMenuBar::item:selected {
    background-color: #26313A;
}

QMenu {
    background-color: #1B242C;
    color: #E7EDF3;
    border: 1px solid #3A4650;
}

QMenu::item {
    padding: 5px 26px 5px 10px;
}

QMenu::item:selected {
    background-color: #2B3944;
}

QStatusBar {
    background-color: #141B21;
    color: #AEBAC5;
    border-top: 1px solid #34404A;
}

QToolBar {
    background-color: #1A222A;
    border: none;
    border-bottom: 1px solid #34404A;
    spacing: 2px;
    padding: 2px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
    padding: 4px 7px;
}

QToolButton:hover {
    background-color: #26313A;
    border-color: #43515D;
}

QDockWidget {
    color: #E7EDF3;
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}

QDockWidget::title {
    background-color: #151D24;
    color: #DCE5EC;
    border-bottom: 1px solid #36434D;
    padding: 5px 7px;
    text-align: left;
}

QTabWidget::pane {
    border: 1px solid #36434D;
    background-color: #182028;
    top: -1px;
}

QTabBar::tab {
    background-color: #1C252D;
    color: #AEBAC5;
    border: 1px solid #36434D;
    border-bottom: none;
    padding: 5px 11px;
    margin-right: 1px;
    min-width: 74px;
}

QTabBar::tab:selected {
    background-color: #24313A;
    color: #F2F6F9;
    border-top: 2px solid #4FA3DD;
    padding-top: 4px;
}

QTabBar::tab:hover:!selected {
    background-color: #222D35;
}

QPushButton {
    background-color: #222C34;
    color: #E7EDF3;
    border: 1px solid #43515D;
    border-radius: 3px;
    padding: 4px 9px;
    min-height: 18px;
}

QPushButton:hover {
    background-color: #2A3741;
    border-color: #536472;
}

QPushButton:pressed {
    background-color: #172027;
}

QPushButton:disabled {
    color: #707D87;
    background-color: #1B232A;
    border-color: #303A42;
}

QLineEdit,
QSpinBox,
QPlainTextEdit {
    background-color: #12191F;
    color: #EEF3F7;
    border: 1px solid #41505C;
    border-radius: 3px;
    padding: 4px 6px;
    selection-background-color: #245E8B;
}

QLineEdit:focus,
QSpinBox:focus,
QPlainTextEdit:focus {
    border: 1px solid #4F9DD2;
}

QSpinBox::up-button,
QSpinBox::down-button {
    background-color: #222C34;
    border-left: 1px solid #41505C;
    width: 15px;
}

QTableView,
QTableWidget {
    background-color: #151D23;
    alternate-background-color: #192229;
    color: #E5ECF1;
    gridline-color: #34414B;
    border: 1px solid #3B4853;
    selection-background-color: #126AA4;
    selection-color: #FFFFFF;
    outline: 0;
}

QTableView::item,
QTableWidget::item {
    padding: 2px 5px;
    border: none;
}

QTableView::item:hover,
QTableWidget::item:hover {
    background-color: #21313D;
}

QHeaderView::section {
    background-color: #202A32;
    color: #DCE5EB;
    border: none;
    border-right: 1px solid #3A4650;
    border-bottom: 1px solid #46545F;
    padding: 4px 6px;
    font-weight: 600;
}

QHeaderView::section:first {
    border-left: none;
}

QScrollBar:vertical {
    background: #151D23;
    width: 11px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #46545F;
    min-height: 26px;
    border-radius: 5px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background: #5B6B77;
}

QScrollBar:horizontal {
    background: #151D23;
    height: 11px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #46545F;
    min-width: 26px;
    border-radius: 5px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background: #5B6B77;
}

QScrollBar::add-line,
QScrollBar::sub-line {
    width: 0;
    height: 0;
}

QSplitter::handle {
    background-color: #35414B;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}

QLabel#SectionTitle {
    background-color: #1B252D;
    color: #EDF3F7;
    border-top: 1px solid #3B4853;
    border-bottom: 1px solid #3B4853;
    padding: 5px 7px;
    font-weight: 700;
}

QLabel#PanelTitle {
    color: #EAF1F5;
    font-weight: 700;
    padding: 1px 0px;
}

QLabel#MutedLabel {
    color: #9CAAB5;
}


QFrame#FlatPanel {
    background-color: #182028;
    border: 1px solid #394650;
}

QCheckBox {
    spacing: 6px;
}

QCheckBox::indicator {
    width: 13px;
    height: 13px;
    border-radius: 2px;
    border: 1px solid #667783;
    background-color: #12191F;
}

QCheckBox::indicator:checked {
    background-color: #1683C3;
    border-color: #53A8DB;
}

QPushButton#FileOpenButton {
    background-color: #1A222A;
    border: none;
    border-radius: 0px;
    padding: 2px 4px;
    margin: 0px;
    min-width: 28px;
    max-width: 28px;
    min-height: 26px;
    max-height: 26px;
}

QPushButton#FileOpenButton:hover {
    background-color: #26313A;
}

QPushButton#FileOpenButton:pressed {
    background-color: #172027;
}


QMainWindow::separator {
    background-color: #596873;
    width: 4px;
    height: 4px;
}

QMainWindow::separator:hover {
    background-color: #738591;
}

QWidget#FileInspectorContainer {
    background-color: #202830;
    border-right: 2px solid #596873;
}

QWidget#TraceInspectorLeft {
    background-color: #161E25;
    border: 1px solid #46545F;
    border-radius: 3px;
}

QFrame#SelectedDataPanel {
    background-color: #1B242B;
    border: 1px solid #53636F;
    border-radius: 3px;
}

QSplitter#TraceInspectorSplitter::handle {
    background-color: #657681;
}

QSplitter#TraceInspectorSplitter::handle:horizontal {
    width: 6px;
}

QSplitter#TraceInspectorSplitter::handle:hover {
    background-color: #81939F;
}

QToolTip {
    background-color: #10171C;
    color: #EEF3F7;
    border: 1px solid #4B5A66;
    padding: 4px;
}
"""


def apply_dark_title_bar(window):
    if sys.platform != "win32":
        return

    hwnd = int(window.winId())
    value = ctypes.c_int(1)

    for attribute in (20, 19):
        result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            attribute,
            ctypes.byref(value),
            ctypes.sizeof(value),
        )
        if result == 0:
            break
