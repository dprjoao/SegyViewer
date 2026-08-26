from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QGroupBox,
)

from segy import SegyDataset


class FileInfoPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._filename = QLabel("—")
        self._path = QLabel("—")
        self._path.setWordWrap(True)
        self._size = QLabel("—")
        self._traces = QLabel("—")
        self._samples = QLabel("—")
        self._dt = QLabel("—")
        self._duration = QLabel("—")
        self._endian = QLabel("—")

        file_box = QGroupBox("File")
        file_form = QFormLayout(file_box)
        file_form.addRow("Name", self._filename)
        file_form.addRow("Path", self._path)
        file_form.addRow("Size", self._size)

        data_box = QGroupBox("SEG-Y")
        data_form = QFormLayout(data_box)
        data_form.addRow("Traces", self._traces)
        data_form.addRow("Samples / trace", self._samples)
        data_form.addRow("Sample interval", self._dt)
        data_form.addRow("Duration", self._duration)
        data_form.addRow("Endian", self._endian)

        layout = QVBoxLayout(self)
        layout.addWidget(file_box)
        layout.addWidget(data_box)
        layout.addStretch(1)

    def set_dataset(self, dataset: SegyDataset) -> None:
        self._filename.setText(dataset.filename)
        self._path.setText(str(dataset.path))
        self._size.setText(f"{dataset.size_mb:,.1f} MB")
        self._traces.setText(f"{dataset.trace_count:,}")
        self._samples.setText(f"{dataset.samples_per_trace:,}")
        self._dt.setText(f"{dataset.sample_interval_ms:g} ms")
        self._duration.setText(f"{dataset.duration_ms:,.1f} ms")
        self._endian.setText(dataset.endian)
