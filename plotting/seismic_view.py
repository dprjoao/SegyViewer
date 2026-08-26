import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Signal, Qt

class SeismicView(pg.PlotWidget):
    traceSelected = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trace_indices = np.array([], dtype=int)
        self.image = pg.ImageItem()
        self.addItem(self.image)
        self.setLabel("left","Time",units="ms")
        self.setLabel("bottom","Trace")
        self.getViewBox().invertY(True)
        self.scene().sigMouseClicked.connect(self._clicked)

    def set_section(self, data, indices, dt_ms):
        self.trace_indices = np.asarray(indices,dtype=int)
        image = np.asarray(data,dtype=np.float32)
        self.image.setImage(image, autoLevels=True)
        if len(indices):
            x0=float(indices[0])
            dx=float(indices[1]-indices[0]) if len(indices)>1 else 1.0
            self.image.setRect(x0,0.0,dx*image.shape[1],dt_ms*image.shape[0])
        self.autoRange()

    def _clicked(self,event):
        if event.button()!=Qt.LeftButton or not len(self.trace_indices): return
        p=self.getViewBox().mapSceneToView(event.scenePos())
        i=int(self.trace_indices[np.argmin(np.abs(self.trace_indices-p.x()))])
        self.traceSelected.emit(i)
