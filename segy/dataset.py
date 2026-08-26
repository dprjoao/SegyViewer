from dataclasses import dataclass
from pathlib import Path
import numpy as np
import segyio

@dataclass
class SegyDataset:
    path: Path
    trace_count: int
    samples_per_trace: int
    sample_interval_ms: float
    textual_header_raw: bytes
    textual_header: str
    binary_header: dict
    endian: str = "big"

    def _open(self):
        return segyio.open(str(self.path), "r", strict=False,
                           ignore_geometry=True, endian=self.endian)

    def read_trace(self, index):
        with self._open() as f:
            return np.asarray(f.trace[index], dtype=np.float32).copy()

    def read_traces(self, indices):
        with self._open() as f:
            return np.stack([np.asarray(f.trace[int(i)], dtype=np.float32)
                             for i in indices])

    def read_trace_header(self, trace_index):
        if not 0 <= trace_index < self.trace_count:
            raise IndexError(
                f"Trace index {trace_index} out of range!"
                f"[0, {self.trace_count - 1}]"
            )
            
        with self._open() as f:
            h = f.header[trace_index]
            return {byte: int(h[byte]) for byte in segyio.tracefield.keys.values()}

    def read_header_field(self, byte):
        with self._open() as f:
            return np.asarray(f.attributes(byte)[:], dtype=np.int64)
