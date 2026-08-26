import segyio
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSpinBox, QLineEdit, QTableView, QHeaderView)

def trace_field_names():
    names = {}
    for name, value in vars(segyio.TraceField).items():
        if not name.startswith("_") and isinstance(value, int):
            names.setdefault(int(value), name)
    return names

FIELD_NAMES = trace_field_names()

class TraceHeaderModel(QAbstractTableModel):
    columns = ("Byte", "Field", "Value")
    def __init__(self):
        super().__init__()
        self.all_rows, self.rows, self.query = [], [], ""

    def set_header(self, header):
        self.beginResetModel()
        self.all_rows = [(byte, FIELD_NAMES.get(byte, f"BYTE_{byte}"), v)
                         for byte, v in sorted(header.items())]
        self._apply_filter()
        self.endResetModel()

    def set_filter(self, text):
        self.beginResetModel()
        self.query = text.strip().lower()
        self._apply_filter()
        self.endResetModel()

    def _apply_filter(self):
        if not self.query:
            self.rows = self.all_rows
        else:
            q = self.query
            self.rows = [r for r in self.all_rows
                         if q in str(r[0]).lower()
                         or q in r[1].lower()
                         or q in str(r[2]).lower()]

    def rowCount(self, parent=QModelIndex()): return len(self.rows)
    def columnCount(self, parent=QModelIndex()): return 3

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.isValid():
            return str(self.rows[index.row()][index.column()])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.columns[section]

class TraceInspectorDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Trace Inspector", parent)
        self.dataset = None
        self.model = TraceHeaderModel()
        body = QWidget()
        layout = QVBoxLayout(body)

        nav = QHBoxLayout()
        self.first = QPushButton("⏮"); self.prev = QPushButton("◀")
        self.spin = QSpinBox()
        self.next = QPushButton("▶"); self.last = QPushButton("⏭")
        for w in (self.first,self.prev,self.spin,self.next,self.last): nav.addWidget(w)
        layout.addLayout(nav)

        self.summary = QLabel("No trace selected")
        layout.addWidget(self.summary)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter byte, field or value…")
        layout.addWidget(self.search)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        self.setWidget(body)

        self.search.textChanged.connect(self.model.set_filter)
        self.spin.valueChanged.connect(self.set_trace)
        self.first.clicked.connect(lambda: self.spin.setValue(1))
        self.prev.clicked.connect(lambda: self.spin.setValue(max(1,self.spin.value()-1)))
        self.next.clicked.connect(lambda: self.spin.setValue(min(self.spin.maximum(),self.spin.value()+1)))
        self.last.clicked.connect(lambda: self.spin.setValue(self.spin.maximum()))

    def set_dataset(self, dataset):
        self.dataset = dataset
        self.spin.blockSignals(True)
        self.spin.setRange(1, max(1,dataset.trace_count))
        self.spin.setValue(1)
        self.spin.blockSignals(False)
        self.set_trace(1)

    def select_zero_based_trace(self, index):
        if self.dataset: self.spin.setValue(index+1)

    def set_trace(self, number):
        if not self.dataset: return
        h = self.dataset.read_trace_header(number-1)
        self.model.set_header(h)
        def val(field): return h.get(int(field))
        self.summary.setText(
            f"Trace {number:,} / {self.dataset.trace_count:,}\n"
            )
