from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPixmap


def folder_icon():
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    path = QPainterPath()
    path.moveTo(3, 7)
    path.lineTo(9, 7)
    path.lineTo(11, 9)
    path.lineTo(21, 9)
    path.lineTo(21, 19)
    path.lineTo(3, 19)
    path.closeSubpath()

    painter.fillPath(path, QColor('#E8B84A'))
    painter.end()

    return QIcon(pixmap)
