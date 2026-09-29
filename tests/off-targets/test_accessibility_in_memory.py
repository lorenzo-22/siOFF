"""GenomeAccessibilityService can serve profiles from in-memory DataFrames.

`sioff.accessibility` returns ``dict[chrom -> DataFrame]`` and never touches
disk; `off_targets` used to accept only a directory of Parquet files, so the
fold stage could not be piped in memory the way `sioff.search` output can.
The frame-backed service must answer queries identically to the Parquet-backed
one built from the same profiles.
"""

from pathlib import Path

import numpy as np
import polars as pl
import pytest

import sioff
from sioff.services.accessibility import (
    AccessibilityError,
    GenomeAccessibilityService,
)

DATA_DIR = Path(__file__).parent / "data"
GENOME_FASTA = DATA_DIR / "genome.fa"


@pytest.fixture(scope="module")
def profiles() -> dict[str, pl.DataFrame]:
    return sioff.accessibility(
        GENOME_FASTA, window_size=40, max_span=20, unpaired_prob=10
    )


@pytest.fixture
def parquet_dir(tmp_path: Path, profiles) -> Path:
    for chrom, frame in profiles.items():
        frame.write_parquet(tmp_path / f"{chrom}.accessibility.parquet")
    return tmp_path


def test_frames_and_parquet_answer_the_same_queries(profiles, parquet_dir):
    from_frames = GenomeAccessibilityService.from_frames(profiles)
    from_disk = GenomeAccessibilityService(parquet_dir)

    for strand in ("+", "-"):
        a = from_frames.query("chr1", 5, 30, strand)
        b = from_disk.query("chr1", 5, 30, strand)
        np.testing.assert_array_equal(a, b)


def test_frames_service_does_not_touch_disk(profiles, tmp_path):
    before = set(tmp_path.rglob("*"))
    service = GenomeAccessibilityService.from_frames(profiles)
    service.query("chr1", 1, 10, "+")
    assert set(tmp_path.rglob("*")) == before
    assert service.data_dir is None


def test_frames_service_names_the_missing_chromosome(profiles):
    service = GenomeAccessibilityService.from_frames(profiles)
    with pytest.raises(AccessibilityError, match="chrX"):
        service.query("chrX", 1, 10, "+")
