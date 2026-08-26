from pathlib import Path

import numpy as np

from segy.dataset import SegyDataset


def test_sample_interval_ms() -> None:
    dataset = SegyDataset(
        path=Path("example.sgy"),
        trace_count=10,
        samples_per_trace=3,
        sample_interval_us=2000.0,
        sample_axis=np.array([0.0, 2.0, 4.0]),
        textual_header="",
    )

    assert dataset.sample_interval_ms == 2.0
    assert dataset.duration_ms == 4.0
