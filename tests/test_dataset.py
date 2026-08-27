from pathlib import Path

import numpy as np

from segy.dataset import SegyDataset


def build_dataset(
    *,
    sample_interval_us: float = 2000.0,
    sample_axis: np.ndarray | None = None,
    samples_per_trace: int = 3,
) -> SegyDataset:
    if sample_axis is None:
        sample_axis = np.array(
            [0.0, 2.0, 4.0],
            dtype=float,
        )

    return SegyDataset(
        path=Path("example.sgy"),
        trace_count=10,
        samples_per_trace=samples_per_trace,
        sample_interval_us=sample_interval_us,
        sample_axis=sample_axis,
        textual_header_raw=b"",
        textual_header_wrapped="",
        binary_header={},
    )


def test_sample_interval_ms() -> None:
    dataset = build_dataset(
        sample_interval_us=2000.0,
    )

    assert dataset.sample_interval_ms == 2.0


def test_duration_ms() -> None:
    dataset = build_dataset(
        sample_axis=np.array(
            [0.0, 2.0, 4.0],
            dtype=float,
        ),
    )

    assert dataset.duration_ms == 4.0


def test_duration_ms_for_empty_trace() -> None:
    dataset = build_dataset(
        samples_per_trace=0,
        sample_axis=np.array(
            [],
            dtype=float,
        ),
    )

    assert dataset.duration_ms == 0.0


def test_clear_header_cache() -> None:
    dataset = build_dataset()

    dataset._header_cache[189] = np.array(
        [100, 101, 102],
        dtype=np.int64,
    )

    dataset.clear_header_cache()

    assert dataset._header_cache == {}
