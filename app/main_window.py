import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow,QFileDialog,QMessageBox,QDockWidget,
                               QPlainTextEdit,QTableWidget,QTableWidgetItem)
from segy.reader import SegyReader
from plotting.seismic_view import SeismicView
from ui.trace_inspector import TraceInspectorDock

class MainWindow(QMainWindow):
    MAX_PREVIEW_TRACES=1200
    def __init__(self):
        super().__init__()
        self.resize(1400,850)
        self.setWindowTitle("SEG-Y Inspector")
        self.dataset=None
        self.view=SeismicView()
        self.setCentralWidget(self.view)
        self.inspector=TraceInspectorDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea,self.inspector)
        self.view.traceSelected.connect(self.inspector.select_zero_based_trace)

        fm=self.menuBar().addMenu("&File")
        fm.addAction("Open SEG-Y…").triggered.connect(self.open_dialog)
        vm=self.menuBar().addMenu("&View")
        vm.addAction("Textual Header").triggered.connect(self.show_text)
        vm.addAction("Binary Header").triggered.connect(self.show_binary)

    def open_dialog(self):
        p,_=QFileDialog.getOpenFileName(self,"Open SEG-Y","","SEG-Y (*.sgy *.segy);;All files (*)")
        if p:self.open_segy(p)

    def open_segy(self,path):
        try:
            self.dataset=SegyReader.open(path)
            self.inspector.set_dataset(self.dataset)
            n=self.dataset.trace_count
            inds=np.unique(np.linspace(0,n-1,min(n,self.MAX_PREVIEW_TRACES),dtype=int))
            data=self.dataset.read_traces(inds)
            self.view.set_section(data,inds,self.dataset.sample_interval_ms)
            self.statusBar().showMessage(
                f"{self.dataset.path.name} — {n:,} traces — "
                f"{self.dataset.samples_per_trace:,} samples — "
                f"dt {self.dataset.sample_interval_ms:g} ms")
        except Exception as e:
            QMessageBox.critical(self,"SEG-Y error",str(e))

    def show_text(self):
        if not self.dataset:return
        d=QDockWidget("Textual Header",self)
        e=QPlainTextEdit(self.dataset.textual_header)
        e.setReadOnly(True); e.setLineWrapMode(QPlainTextEdit.NoWrap)
        d.setWidget(e); self.addDockWidget(Qt.BottomDockWidgetArea,d)

    def show_binary(self):
        if not self.dataset:return
        d=QDockWidget("Binary Header",self)
        t=QTableWidget(len(self.dataset.binary_header),2)
        t.setHorizontalHeaderLabels(["Field","Value"])
        for r,(k,v) in enumerate(self.dataset.binary_header.items()):
            t.setItem(r,0,QTableWidgetItem(k)); t.setItem(r,1,QTableWidgetItem(str(v)))
        d.setWidget(t); self.addDockWidget(Qt.BottomDockWidgetArea,d)
