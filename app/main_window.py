import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTabWidget,
)

from plotting.seismic_view import SeismicView
from segy.reader import SegyReader
from ui.file_inspector import FileInspectorDock
from ui.trace_inspector import TraceInspectorWidget


class MainWindow(QMainWindow):
    MAX_PREVIEW_TRACES = 1200

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SEG-Y Viewer")
        self.resize(1700, 950)

        self.dataset = None

        self.setDockOptions(
            QMainWindow.AnimatedDocks
            | QMainWindow.AllowTabbedDocks
        )

        # -------------------------------------------------------------
        # Main workspace
        # -------------------------------------------------------------
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)

        self.seismic_view = SeismicView()
        self.trace_inspector = (
            TraceInspectorWidget()
        )

        self.tabs.addTab(
            self.seismic_view,
            "Seismic View",
        )
        self.tabs.addTab(
            self.trace_inspector,
            "Trace Inspector",
        )

        self.setCentralWidget(self.tabs)

        # -------------------------------------------------------------
        # File inspector
        # -------------------------------------------------------------
        self.file_inspector = (
            FileInspectorDock(self)
        )

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self.file_inspector,
        )

        self.resizeDocks(
            [self.file_inspector],
            [315],
            Qt.Horizontal,
        )

        # -------------------------------------------------------------
        # Menus / toolbar
        # -------------------------------------------------------------
        file_menu = self.menuBar().addMenu(
            "&File"
        )

        self.open_action = QAction(
            "Open SEG-Y...",
            self,
        )
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(
            self.open_dialog
        )
        file_menu.addAction(self.open_action)

        view_menu = self.menuBar().addMenu(
            "&View"
        )

        seismic_action = QAction(
            "Seismic View",
            self,
        )
        seismic_action.triggered.connect(
            lambda:
            self.tabs.setCurrentWidget(
                self.seismic_view
            )
        )
        view_menu.addAction(seismic_action)

        trace_action = QAction(
            "Trace Inspector",
            self,
        )
        trace_action.triggered.connect(
            lambda:
            self.tabs.setCurrentWidget(
                self.trace_inspector
            )
        )
        view_menu.addAction(trace_action)

        view_menu.addSeparator()

        file_inspector_action = QAction(
            "File Inspector",
            self,
        )
        file_inspector_action.triggered.connect(
            self.file_inspector.show
        )
        view_menu.addAction(
            file_inspector_action
        )

        # -------------------------------------------------------------
        # Open button inside File Inspector
        # -------------------------------------------------------------
        self.file_inspector.set_open_action(
            self.open_action
        )

        # -------------------------------------------------------------
        # Cross-selection
        # -------------------------------------------------------------
        self.seismic_view.traceSelected.connect(
            self._trace_selected_from_seismic
        )

        self.statusBar().showMessage(
            "Open a SEG-Y file to begin"
        )

    def open_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open SEG-Y",
            "",
            (
                "SEG-Y files (*.sgy *.segy);;"
                "All files (*)"
            ),
        )

        if path:
            self.open_segy(path)

    def open_segy(self, path):
        try:
            self.dataset = SegyReader.open(
                path
            )

            self.file_inspector.set_dataset(
                self.dataset
            )
            self.trace_inspector.set_dataset(
                self.dataset
            )

            self._load_preview()

            self.setWindowTitle(
                f"{self.dataset.path} — "
                "SEG-Y Viewer"
            )

            self.statusBar().showMessage(
                f"{self.dataset.path.name}    |    "
                f"{self.dataset.trace_count:,} traces    |    "
                f"{self.dataset.samples_per_trace:,} samples    |    "
                f"dt {self.dataset.sample_interval_ms} ms"
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "SEG-Y error",
                str(exc),
            )

    def _load_preview(self):
        count = min(
            self.dataset.trace_count,
            self.MAX_PREVIEW_TRACES,
        )

        indices = np.unique(
            np.linspace(
                0,
                self.dataset.trace_count - 1,
                count,
                dtype=int,
            )
        )

        data = self.dataset.read_traces(
            indices
        )

        self.seismic_view.set_section(
            data,
            indices,
            self.dataset.sample_axis,
        )

    def _trace_selected_from_seismic(
        self,
        trace_index,
    ):
        self.trace_inspector.select_zero_based_trace(
            trace_index
        )
