from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from segy import SegyDataset


class TextualHeaderDialog(QDialog):
    def __init__(self, dataset: SegyDataset, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Textual Header — {dataset.filename}")
        self.resize(900, 650)

        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setLineWrapMode(QPlainTextEdit.NoWrap)
        text.setPlainText(dataset.textual_header_wrapped)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(text)
        layout.addWidget(buttons)


class BinaryHeaderDialog(QDialog):
    def __init__(self, dataset: SegyDataset, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Binary Header — {dataset.filename}")
        self.resize(760, 650)

        rows = sorted(dataset.binary_header.items())
        table = QTableWidget(len(rows), 2)
        table.setHorizontalHeaderLabels(["Field", "Value"])
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)

        for row, (name, value) in enumerate(rows):
            name_item = QTableWidgetItem(str(name))
            value_item = QTableWidgetItem(str(value))
            value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 0, name_item)
            table.setItem(row, 1, value_item)

        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnToContents(0)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(table)
        layout.addWidget(buttons)
