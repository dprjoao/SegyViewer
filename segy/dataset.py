from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import segyio


@dataclass
class SegyDataset:
    path: Path
    trace_count: int
    samples_per_trace: int
    sample_interval_us: float
    sample_axis: np.ndarray
    textual_header_raw: bytes
    textual_header_wrapped: str
    binary_header: dict
    endian: str = "big"
    _header_cache: dict[int, np.ndarray] = field(default_factory=dict, repr=False)

    @property
    def sample_interval_ms(self) -> int:
        return int(round(self.sample_interval_us / 1000.0))

    @property
    def duration_s(self) -> float:
        if self.samples_per_trace == 0:
            return 0.0

        return (
            self.samples_per_trace
            * self.sample_interval_ms
            / 1000.0
        )

    def _open(self):
        return segyio.open(
            str(self.path),
            mode="r",
            strict=False,
            ignore_geometry=True,
            endian=self.endian,
        )

    def read_trace(self, index):
        with self._open() as f:
            return np.asarray(f.trace[index], dtype=np.float32).copy()

    def read_traces(self, indices):
        with self._open() as f:
            return np.stack(
                [np.asarray(f.trace[int(index)], dtype=np.float32) for index in indices]
            )

    def read_trace_header(self, index):
        with self._open() as f:
            h = f.header[index]
            return {byte: int(h[byte]) for byte in segyio.tracefield.keys.values()}

    def read_header_field(self, byte, use_cache=True):
        byte = int(byte)

        if use_cache and byte in self._header_cache:
            return self._header_cache[byte]

        with self._open() as f:
            values = np.asarray(f.attributes(byte)[:], dtype=np.int64).copy()

        if use_cache:
            self._header_cache[byte] = values

        return values

    def clear_header_cache(self):
        self._header_cache.clear()
