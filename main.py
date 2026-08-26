import sys
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow

app=QApplication(sys.argv)
window=MainWindow()
window.show()
if len(sys.argv)>1: window.open_segy(sys.argv[1])
sys.exit(app.exec())