import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal


class SeismicView(pg.PlotWidget):
    traceSelected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setBackground("#11171C")

        self.trace_indices = np.array(
            [],
            dtype=int,
        )

        self.image = pg.ImageItem()
        self.addItem(self.image)

        self.setLabel(
            "left",
            "Time",
            units="s",
            color="#C8D2DA",
        )
        self.setLabel(
            "bottom",
            "Trace",
            color="#C8D2DA",
        )

        for axis_name in (
            "left",
            "bottom",
        ):
            axis = self.getAxis(axis_name)
            axis.setPen("#596874")
            axis.setTextPen("#B8C4CD")

        self.getViewBox().invertY(True)
        self.getViewBox().setBorder(
            pg.mkPen("#394650")
        )

        self.scene().sigMouseClicked.connect(
            self._mouse_clicked
        )

    def set_section(
        self,
        data,
        trace_indices,
        sample_axis_ms,
    ):
        self.trace_indices = np.asarray(
            trace_indices,
            dtype=int,
        )

        image = np.asarray(
            data,
            dtype=np.float32,
        )

        self.image.setImage(
            image,
            autoLevels=True,
        )

        # segyio provides the sample axis in milliseconds. Convert it to
        # seconds for the conventional seismic time display.
        sample_axis_s = np.asarray(
            sample_axis_ms,
            dtype=np.float64,
        ) / 1000.0

        if len(trace_indices):
            x0 = float(trace_indices[0])

            dx = (
                float(
                    trace_indices[1]
                    - trace_indices[0]
                )
                if len(trace_indices) > 1
                else 1.0
            )

            if len(sample_axis_s) > 1:
                y0 = float(
                    sample_axis_s[0]
                )
                dy = float(
                    sample_axis_s[1]
                    - sample_axis_s[0]
                )
            else:
                y0 = 0.0
                dy = 1.0

            self.image.setRect(
                x0,
                y0,
                dx * image.shape[1],
                dy * image.shape[0],
            )

        self.autoRange()

    def _mouse_clicked(self, event):
        if (
            event.button() != Qt.LeftButton
            or not len(self.trace_indices)
        ):
            return

        point = (
            self.getViewBox()
            .mapSceneToView(event.scenePos())
        )

        trace_index = int(
            self.trace_indices[
                np.argmin(
                    np.abs(
                        self.trace_indices
                        - point.x()
                    )
                )
            ]
        )

        self.traceSelected.emit(
            trace_index
        )
