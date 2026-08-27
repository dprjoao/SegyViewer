from pathlib import Path

import numpy as np
import segyio

from .dataset import SegyDataset


class SegyReader:
    @staticmethod
    def open(path, endian="big"):
        segy_path = Path(path).expanduser().resolve()

        with segyio.open(
            str(segy_path),
            mode="r",
            strict=False,
            ignore_geometry=True,
            endian=endian,
        ) as f:
            trace_count = f.tracecount
            samples_per_trace = len(f.samples)
            sample_interval_us = float(segyio.tools.dt(f))
            sample_axis = np.asarray(f.samples, dtype=np.float64).copy()

            textual_header_raw = bytes(f.text[0])
            textual_header_wrapped = segyio.tools.wrap(textual_header_raw)

            binary_header = {}
            for name, byte in segyio.binfield.keys.items():
                try:
                    binary_header[name] = {
                        "byte": int(byte),
                        "value": int(f.bin[byte]),
                    }
                except Exception:
                    pass

        return SegyDataset(
            path=segy_path,
            trace_count=trace_count,
            samples_per_trace=samples_per_trace,
            sample_interval_us=sample_interval_us,
            sample_axis=sample_axis,
            textual_header_raw=textual_header_raw,
            textual_header_wrapped=textual_header_wrapped,
            binary_header=binary_header,
            endian=endian,
        )
