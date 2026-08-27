import sys

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from ui.theme import APP_QSS, apply_dark_title_bar


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_QSS)

    window = MainWindow()

    window.winId()
    apply_dark_title_bar(window)

    if len(sys.argv) > 1:
        window.open_segy(sys.argv[1])

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
