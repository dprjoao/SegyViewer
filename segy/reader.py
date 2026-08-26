from pathlib import Path
import segyio
from .dataset import SegyDataset

class SegyReader:
    @staticmethod
    def open(path, endian="big"):
        path = Path(path).expanduser().resolve()
        with segyio.open(str(path), "r", strict=False,
                         ignore_geometry=True, endian=endian) as f:
            raw = bytes(f.text[0])
            binary_header = {}
            try:
                binary_header = {
                    name: {
                    "byte": byte,
                    "value": int(segyio.bin[byte]),
                }
                for name, byte
                            in segyio.binfield.keys.items()
                }
            except Exception:
                pass
            return SegyDataset(
                path=path,
                trace_count=f.tracecount,
                samples_per_trace=len(f.samples),
                sample_interval_ms=float(segyio.tools.dt(f))/1000.0,
                textual_header_raw=raw,
                textual_header=segyio.tools.wrap(raw),
                binary_header=binary_header,
                endian=endian,
            )
