from __future__ import annotations

import csv

import segyio
from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
    Signal,
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)


FIELD_NAMES = {
    int(byte): name
    for name, byte in segyio.tracefield.keys.items()
}


class HeaderSelectionModel(QAbstractTableModel):
    selectionChanged = Signal(list)

    COLUMNS = ("Select", "Byte", "Field")

    def __init__(self):
        super().__init__()

        self._all_rows = sorted(
            (
                (int(byte), name)
                for name, byte
                in segyio.tracefield.keys.items()
            ),
            key=lambda row: row[0],
        )

        self._rows = self._all_rows.copy()
        self._checked = set()
        self._filter = ""

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.COLUMNS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        byte, name = self._rows[index.row()]

        if index.column() == 0:
            if role == Qt.CheckStateRole:
                if byte in self._checked:
                    return Qt.CheckState.Checked
                return Qt.CheckState.Unchecked

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            return None

        if role == Qt.DisplayRole:
            if index.column() == 1:
                return str(byte)

            if index.column() == 2:
                return name

        if role == Qt.TextAlignmentRole and index.column() == 1:
            return Qt.AlignCenter

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if index.column() == 0:
            flags |= Qt.ItemIsUserCheckable

        return flags

    def setData(self, index, value, role=Qt.EditRole):
        if (
            not index.isValid()
            or index.column() != 0
            or role != Qt.CheckStateRole
        ):
            return False

        byte = self._rows[index.row()][0]

        checked = value in (
            Qt.CheckState.Checked,
            Qt.Checked,
            2,
        )

        if checked:
            self._checked.add(byte)
        else:
            self._checked.discard(byte)

        self.dataChanged.emit(
            index,
            index,
            [Qt.CheckStateRole],
        )

        self.selectionChanged.emit(
            self.selected_bytes()
        )

        return True

    def headerData(
        self,
        section,
        orientation,
        role=Qt.DisplayRole,
    ):
        if (
            role == Qt.DisplayRole
            and orientation == Qt.Horizontal
        ):
            return self.COLUMNS[section]

        return None

    def set_filter(self, text):
        self.beginResetModel()

        self._filter = text.strip().lower()

        if not self._filter:
            self._rows = self._all_rows.copy()
        else:
            query = self._filter
            self._rows = [
                row
                for row in self._all_rows
                if (
                    query in str(row[0]).lower()
                    or query in row[1].lower()
                )
            ]

        self.endResetModel()

    def selected_bytes(self):
        return sorted(self._checked)

    def select_all(self):
        self.beginResetModel()

        self._checked = {
            byte
            for byte, _ in self._all_rows
        }

        self.endResetModel()
        self.selectionChanged.emit(
            self.selected_bytes()
        )

    def clear_all(self):
        self.beginResetModel()
        self._checked.clear()
        self.endResetModel()
        self.selectionChanged.emit([])


class SelectedHeaderDataModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()

        self.dataset = None
        self._bytes = []
        self._columns = {}

    @property
    def selected_bytes(self):
        return self._bytes

    def set_dataset(self, dataset):
        self.beginResetModel()

        self.dataset = dataset
        self._bytes = []
        self._columns = {}

        self.endResetModel()

    def set_selected_headers(self, bytes_):
        self.beginResetModel()

        self._bytes = list(bytes_)
        self._columns = {}

        if self.dataset is not None:
            for byte in self._bytes:
                self._columns[byte] = (
                    self.dataset.read_header_field(
                        byte
                    )
                )

        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        if (
            parent.isValid()
            or self.dataset is None
        ):
            return 0

        return self.dataset.trace_count

    def columnCount(self, parent=QModelIndex()):
        if (
            parent.isValid()
            or self.dataset is None
        ):
            return 0

        return 1 + len(self._bytes)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return str(index.row() + 1)

            byte = self._bytes[
                index.column() - 1
            ]

            return str(
                self._columns[byte][
                    index.row()
                ]
            )

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        return None

    def headerData(
        self,
        section,
        orientation,
        role=Qt.DisplayRole,
    ):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                return "Trace Index"

            byte = self._bytes[
                section - 1
            ]

            return FIELD_NAMES.get(
                byte,
                f"BYTE_{byte}",
            )

        return str(section + 1)

    def value_at(self, row, column):
        if column == 0:
            return row + 1

        byte = self._bytes[column - 1]
        return int(
            self._columns[byte][row]
        )



class TraceInspectorWidget(QWidget):
    traceChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dataset = None

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(3)

        # -------------------------------------------------------------
        # Main two-column layout
        # -------------------------------------------------------------
        splitter = QSplitter(Qt.Horizontal)
        splitter.setObjectName(
            "TraceInspectorSplitter"
        )
        splitter.setHandleWidth(5)

        left_container = QWidget()
        left_container.setObjectName(
            "TraceInspectorLeft"
        )
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(
            5,
            5,
            5,
            5,
        )
        left_layout.setSpacing(3)

        # -------------------------------------------------------------
        # Controls
        # -------------------------------------------------------------
        controls_title = QLabel(
            "Trace Controls"
        )
        controls_title.setObjectName(
            "PanelTitle"
        )
        left_layout.addWidget(controls_title)

        controls = QFrame()
        controls.setObjectName("FlatPanel")
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(
            4,
            3,
            4,
            3,
        )
        controls_layout.setSpacing(2)

        self.first_btn = QPushButton("|<")
        self.prev_btn = QPushButton("<")
        self.next_btn = QPushButton(">")
        self.last_btn = QPushButton(">|")

        for button in (
            self.first_btn,
            self.prev_btn,
            self.next_btn,
            self.last_btn,
        ):
            button.setFixedWidth(34)

        controls_layout.addWidget(
            self.first_btn
        )
        controls_layout.addWidget(
            self.prev_btn
        )
        controls_layout.addWidget(
            self.next_btn
        )
        controls_layout.addWidget(
            self.last_btn
        )

        controls_layout.addSpacing(10)
        controls_layout.addWidget(
            QLabel("Trace index")
        )

        self.trace_spin = QSpinBox()
        self.trace_spin.setMinimumWidth(105)
        self.trace_spin.setMaximumWidth(125)
        self.trace_spin.setKeyboardTracking(False)
        controls_layout.addWidget(
            self.trace_spin
        )

        self.trace_total = QLabel("/ 0")
        self.trace_total.setObjectName(
            "MutedLabel"
        )
        controls_layout.addWidget(
            self.trace_total
        )

        controls_layout.addStretch(1)

        left_layout.addWidget(controls)

        # -------------------------------------------------------------
        # Header selection area
        # -------------------------------------------------------------
        # Header controls + available headers
        selector_container = QWidget()
        selector_container_layout = QVBoxLayout(
            selector_container
        )
        selector_container_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        selector_container_layout.setSpacing(5)

        # Header controls
        controls_panel = QFrame()
        controls_panel.setObjectName("FlatPanel")
        header_controls_layout = QVBoxLayout(
            controls_panel
        )
        header_controls_layout.setContentsMargins(
            7,
            6,
            7,
            6,
        )
        header_controls_layout.setSpacing(5)

        controls_title = QLabel(
            "Header Controls"
        )
        controls_title.setObjectName(
            "PanelTitle"
        )
        header_controls_layout.addWidget(
            controls_title
        )

        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search header name or byte..."
        )
        self.search.setClearButtonEnabled(True)
        header_controls_layout.addWidget(
            self.search
        )

        controls_footer = QHBoxLayout()

        self.select_all_btn = QPushButton(
            "Select All"
        )
        self.clear_all_btn = QPushButton(
            "Clear All"
        )
        self.selection_count = QLabel(
            "0 headers selected"
        )
        self.selection_count.setObjectName(
            "MutedLabel"
        )

        controls_footer.addWidget(
            self.select_all_btn
        )
        controls_footer.addWidget(
            self.clear_all_btn
        )
        controls_footer.addStretch(1)
        controls_footer.addWidget(
            self.selection_count
        )

        header_controls_layout.addLayout(
            controls_footer
        )

        selector_container_layout.addWidget(
            controls_panel
        )

        # Available headers table
        headers_panel = QFrame()
        headers_panel.setObjectName("FlatPanel")
        headers_layout = QVBoxLayout(
            headers_panel
        )
        headers_layout.setContentsMargins(
            7,
            6,
            7,
            6,
        )
        headers_layout.setSpacing(5)

        headers_title_row = QHBoxLayout()

        headers_title = QLabel(
            "Available Headers"
        )
        headers_title.setObjectName(
            "PanelTitle"
        )

        headers_note = QLabel(
            "(select to display)"
        )
        headers_note.setObjectName(
            "MutedLabel"
        )

        headers_title_row.addWidget(
            headers_title
        )
        headers_title_row.addWidget(
            headers_note
        )
        headers_title_row.addStretch(1)

        headers_layout.addLayout(
            headers_title_row
        )

        self.selection_model = (
            HeaderSelectionModel()
        )

        self.selection_table = QTableView()
        self.selection_table.setModel(
            self.selection_model
        )
        self.selection_table.setAlternatingRowColors(
            True
        )
        self.selection_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.selection_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.selection_table.verticalHeader().setVisible(
            False
        )
        self.selection_table.setShowGrid(True)

        header = (
            self.selection_table.horizontalHeader()
        )
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents,
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents,
        )
        header.setSectionResizeMode(
            2,
            QHeaderView.Stretch,
        )

        headers_layout.addWidget(
            self.selection_table,
            1,
        )

        selector_container_layout.addWidget(
            headers_panel,
            1,
        )

        # Selected data
        data_panel = QFrame()
        data_panel.setObjectName(
            "SelectedDataPanel"
        )
        data_layout = QVBoxLayout(data_panel)
        data_layout.setContentsMargins(
            7,
            6,
            7,
            6,
        )
        data_layout.setSpacing(5)

        data_title_row = QHBoxLayout()

        data_title = QLabel(
            "Selected Headers Data"
        )
        data_title.setObjectName(
            "PanelTitle"
        )

        self.data_showing = QLabel(
            "Showing: 0 headers"
        )
        self.data_showing.setObjectName(
            "MutedLabel"
        )

        data_title_row.addWidget(data_title)
        data_title_row.addStretch(1)
        data_title_row.addWidget(
            self.data_showing
        )

        data_layout.addLayout(
            data_title_row
        )

        self.data_model = (
            SelectedHeaderDataModel()
        )

        self.data_table = QTableView()
        self.data_table.setModel(
            self.data_model
        )
        self.data_table.setAlternatingRowColors(
            True
        )
        self.data_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.data_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.data_table.setSortingEnabled(False)
        self.data_table.setShowGrid(True)

        data_header = (
            self.data_table.horizontalHeader()
        )
        data_header.setStretchLastSection(
            False
        )
        data_header.setSectionResizeMode(
            QHeaderView.Fixed
        )
        data_header.resizeSection(0, 85)

        data_layout.addWidget(
            self.data_table,
            1,
        )

        data_footer = QHBoxLayout()

        self.export_btn = QPushButton(
            "Export to CSV..."
        )
        self.copy_btn = QPushButton(
            "Copy to Clipboard"
        )
        self.data_info = QLabel(
            "Rows: 0    |    Columns: 0"
        )
        self.data_info.setObjectName(
            "MutedLabel"
        )

        data_footer.addWidget(
            self.export_btn
        )
        data_footer.addWidget(
            self.copy_btn
        )
        data_footer.addStretch(1)
        data_footer.addWidget(
            self.data_info
        )

        data_layout.addLayout(data_footer)

        left_layout.addWidget(
            selector_container,
            1,
        )

        splitter.addWidget(left_container)
        splitter.addWidget(data_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([445, 1200])

        root.addWidget(splitter, 1)

        # -------------------------------------------------------------
        # Connections
        # -------------------------------------------------------------
        self.search.textChanged.connect(
            self.selection_model.set_filter
        )
        self.selection_model.selectionChanged.connect(
            self._selection_changed
        )

        self.select_all_btn.clicked.connect(
            self.selection_model.select_all
        )
        self.clear_all_btn.clicked.connect(
            self.selection_model.clear_all
        )

        self.trace_spin.valueChanged.connect(
            self.set_trace
        )

        self.first_btn.clicked.connect(
            lambda:
            self.trace_spin.setValue(1)
        )
        self.prev_btn.clicked.connect(
            lambda:
            self.trace_spin.setValue(
                max(
                    1,
                    self.trace_spin.value() - 1,
                )
            )
        )
        self.next_btn.clicked.connect(
            lambda:
            self.trace_spin.setValue(
                min(
                    self.trace_spin.maximum(),
                    self.trace_spin.value() + 1,
                )
            )
        )
        self.last_btn.clicked.connect(
            lambda:
            self.trace_spin.setValue(
                self.trace_spin.maximum()
            )
        )

        self.data_table.clicked.connect(
            self._data_row_clicked
        )
        self.export_btn.clicked.connect(
            self._export_csv
        )
        self.copy_btn.clicked.connect(
            self._copy_selection
        )

        self._set_dataset_enabled(False)

    def set_dataset(self, dataset):
        self.dataset = dataset

        self.selection_model.clear_all()
        self.data_model.set_dataset(dataset)

        self.trace_spin.blockSignals(True)
        self.trace_spin.setRange(
            1,
            max(1, dataset.trace_count),
        )
        self.trace_spin.setValue(1)
        self.trace_spin.blockSignals(False)

        self.trace_total.setText(
            f"/ {dataset.trace_count:,}"
        )

        self._set_dataset_enabled(True)
        self.set_trace(1)

    def _set_dataset_enabled(self, enabled):
        for widget in (
            self.first_btn,
            self.prev_btn,
            self.next_btn,
            self.last_btn,
            self.trace_spin,
            self.search,
            self.selection_table,
            self.select_all_btn,
            self.clear_all_btn,
            self.data_table,
            self.export_btn,
            self.copy_btn,
        ):
            widget.setEnabled(enabled)

    def select_zero_based_trace(
        self,
        trace_index,
    ):
        if self.dataset is None:
            return

        self.trace_spin.setValue(
            int(trace_index) + 1
        )

    def set_trace(self, one_based_index):
        if self.dataset is None:
            return

        trace_index = one_based_index - 1

        if self.data_model.rowCount() > 0:
            row_index = self.data_model.index(
                trace_index,
                0,
            )

            self.data_table.selectRow(
                trace_index
            )
            self.data_table.scrollTo(
                row_index,
                QAbstractItemView.PositionAtCenter,
            )

        self.traceChanged.emit(trace_index)

    def _resize_data_columns(self):
        header = self.data_table.horizontalHeader()

        if self.data_model.columnCount() == 0:
            return

        # Trace Index remains compact.
        header.resizeSection(0, 85)

        # Every selected trace-header column uses the same width.
        for column in range(
            1,
            self.data_model.columnCount(),
        ):
            header.resizeSection(
                column,
                125,
            )

    def _selection_changed(
        self,
        selected_bytes,
    ):
        count = len(selected_bytes)

        self.selection_count.setText(
            f"{count} header"
            f"{'s' if count != 1 else ''} selected"
        )

        self.data_showing.setText(
            f"Showing: {count} header"
            f"{'s' if count != 1 else ''}"
        )

        self.data_model.set_selected_headers(
            selected_bytes
        )

        self._resize_data_columns()

        rows = self.data_model.rowCount()
        columns = self.data_model.columnCount()

        self.data_info.setText(
            f"Rows: {rows:,}    |    "
            f"Columns: {columns:,}"
        )

    def _data_row_clicked(self, index):
        if not index.isValid():
            return

        self.trace_spin.setValue(
            index.row() + 1
        )

    def _export_csv(self):
        if (
            self.dataset is None
            or not self.data_model.selected_bytes
        ):
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export trace headers",
            "trace_headers.csv",
            "CSV files (*.csv)",
        )

        if not path:
            return

        if not path.lower().endswith(".csv"):
            path += ".csv"

        headers = [
            "Trace Index",
            *[
                FIELD_NAMES.get(
                    byte,
                    f"BYTE_{byte}",
                )
                for byte
                in self.data_model.selected_bytes
            ],
        ]

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8",
        ) as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)

            for row in range(
                self.data_model.rowCount()
            ):
                writer.writerow(
                    [
                        self.data_model.value_at(
                            row,
                            column,
                        )
                        for column
                        in range(
                            self.data_model.columnCount()
                        )
                    ]
                )

    def _copy_selection(self):
        indexes = (
            self.data_table.selectionModel()
            .selectedIndexes()
        )

        if not indexes:
            return

        rows = sorted(
            {index.row() for index in indexes}
        )
        columns = sorted(
            {index.column() for index in indexes}
        )

        text_rows = []

        for row in rows:
            values = [
                str(
                    self.data_model.value_at(
                        row,
                        column,
                    )
                )
                for column in columns
            ]
            text_rows.append(
                "\t".join(values)
            )

        QGuiApplication.clipboard().setText(
            "\n".join(text_rows)
        )
