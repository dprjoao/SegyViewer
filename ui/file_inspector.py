from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDockWidget,
    QFormLayout,
    QFrame,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.icons import folder_icon


def section_title(text):
    label = QLabel(text)
    label.setObjectName("SectionTitle")
    return label


class FileInspectorDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("", parent)

        self.setObjectName("FileInspectorDock")

        # Remove the empty QDockWidget title bar so the file tools
        # start immediately below the application menu.
        dock_title_bar = QWidget()
        dock_title_bar.setFixedHeight(0)
        self.setTitleBarWidget(dock_title_bar)
        self.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
        )
        self.setMinimumWidth(305)

        container = QWidget()
        container.setObjectName("FileInspectorContainer")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # -------------------------------------------------------------
        # File actions
        # -------------------------------------------------------------
        self.open_button = QPushButton()
        self.open_button.setObjectName("FileOpenButton")
        self.open_button.setIcon(folder_icon())
        self.open_button.setToolTip("Open SEG-Y...")
        self.open_button.setFixedSize(28, 26)

        layout.addWidget(
            self.open_button,
            0,
            Qt.AlignLeft,
        )

        # -------------------------------------------------------------
        # File Info
        # -------------------------------------------------------------
        layout.addWidget(section_title("File Info"))

        file_widget = QWidget()
        file_widget.setObjectName("FileInfoPanel")
        file_layout = QFormLayout(file_widget)
        file_layout.setContentsMargins(9, 7, 9, 8)
        file_layout.setHorizontalSpacing(12)
        file_layout.setVerticalSpacing(4)

        self.file_name = QLabel("—")
        self.file_path = QLabel("—")
        self.file_path.setWordWrap(True)
        self.file_size = QLabel("—")
        self.trace_count = QLabel("—")
        self.samples_per_trace = QLabel("—")
        self.sample_interval = QLabel("—")
        self.duration = QLabel("—")
        self.endian = QLabel("—")

        values = (
            self.file_name,
            self.file_path,
            self.file_size,
            self.trace_count,
            self.samples_per_trace,
            self.sample_interval,
            self.duration,
            self.endian,
        )
        for value in values:
            value.setTextInteractionFlags(
                Qt.TextSelectableByMouse
            )

        file_layout.addRow("File", self.file_name)
        file_layout.addRow("Path", self.file_path)
        file_layout.addRow("File size", self.file_size)
        file_layout.addRow("Traces", self.trace_count)
        file_layout.addRow(
            "Samples / trace",
            self.samples_per_trace,
        )
        file_layout.addRow(
            "Sample interval",
            self.sample_interval,
        )
        file_layout.addRow("Duration", self.duration)
        file_layout.addRow("Endian", self.endian)

        layout.addWidget(file_widget)

        # -------------------------------------------------------------
        # Textual Header
        # -------------------------------------------------------------
        self.text_title = section_title(
            "Textual Header"
        )
        layout.addWidget(self.text_title)

        self.textual_header = QPlainTextEdit()
        self.textual_header.setObjectName("TextualHeaderView")
        self.textual_header.setReadOnly(True)
        self.textual_header.setLineWrapMode(
            QPlainTextEdit.NoWrap
        )
        self.textual_header.setMaximumHeight(235)
        self.textual_header.setFrameShape(
            QFrame.NoFrame
        )

        fixed_font = QFontDatabase.systemFont(
            QFontDatabase.FixedFont
        )
        fixed_font.setPointSize(9)
        self.textual_header.setFont(fixed_font)

        layout.addWidget(self.textual_header)

        # -------------------------------------------------------------
        # Binary Header
        # -------------------------------------------------------------
        self.binary_title = section_title(
            "Binary Header"
        )
        layout.addWidget(self.binary_title)

        self.binary_table = QTableWidget()
        self.binary_table.setObjectName("BinaryHeaderTable")
        self.binary_table.setColumnCount(3)
        self.binary_table.setHorizontalHeaderLabels(
            ("Byte", "Field", "Value")
        )
        self.binary_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.binary_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.binary_table.setAlternatingRowColors(True)
        self.binary_table.verticalHeader().setVisible(
            False
        )
        self.binary_table.setShowGrid(True)
        self.binary_table.setFrameShape(
            QFrame.NoFrame
        )

        header = self.binary_table.horizontalHeader()
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents,
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.Stretch,
        )
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents,
        )

        layout.addWidget(self.binary_table, 1)

        self.setWidget(container)

    def set_open_action(self, action):
        self.open_button.clicked.connect(
            action.trigger
        )

    def set_dataset(self, dataset):
        size = dataset.path.stat().st_size

        self.file_name.setText(dataset.path.name)
        self.file_path.setText(str(dataset.path))
        self.file_size.setText(
            self._format_size(size)
        )
        self.trace_count.setText(
            f"{dataset.trace_count:,}"
        )
        self.samples_per_trace.setText(
            f"{dataset.samples_per_trace:,}"
        )
        self.sample_interval.setText(
            f"{dataset.sample_interval_ms} ms"
        )
        self.duration.setText(
            f"{dataset.duration_s:g} s"
        )
        self.endian.setText(dataset.endian)

        self.textual_header.setPlainText(
            dataset.textual_header_wrapped
        )
        self.text_title.setText(
            "Textual Header    40 lines"
        )

        rows = sorted(
            dataset.binary_header.items(),
            key=lambda item: item[1]["byte"],
        )

        self.binary_title.setText(
            f"Binary Header    {len(rows)} fields"
        )
        self.binary_table.setRowCount(len(rows))

        for row, (name, info) in enumerate(rows):
            byte_item = QTableWidgetItem(
                str(info["byte"])
            )
            field_item = QTableWidgetItem(name)
            value_item = QTableWidgetItem(
                str(info["value"])
            )

            byte_item.setTextAlignment(
                Qt.AlignCenter
            )
            value_item.setTextAlignment(
                Qt.AlignCenter
            )

            self.binary_table.setItem(
                row,
                0,
                byte_item,
            )
            self.binary_table.setItem(
                row,
                1,
                field_item,
            )
            self.binary_table.setItem(
                row,
                2,
                value_item,
            )

    @staticmethod
    def _format_size(size):
        value = float(size)

        for unit in (
            "B",
            "KB",
            "MB",
            "GB",
            "TB",
        ):
            if value < 1024.0 or unit == "TB":
                return f"{value:.2f} {unit}"

            value /= 1024.0

        return f"{size} B"
