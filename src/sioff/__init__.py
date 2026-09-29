"""siOFF: siRNA off-target discovery pipeline.

The package exposes four in-memory functions, re-exported from `sioff.api`:
[`off_targets`][sioff.off_targets] (intersect RIsearch predictions with a transcriptome, add
accessibility penalties and compute off-target probabilities),
[`accessibility`][sioff.accessibility] (per-chromosome opening-energy profiles), [`index`][sioff.index]
(build a RIsearch index) and [`search`][sioff.search] (run RIsearch and return the hits).
They return Polars DataFrames (or a `Path` for ``index``), write
no files and raise ordinary Python exceptions; the ``sioff`` command line is a
file-writing wrapper over the same core. ``__version__`` reports the installed
distribution version.
"""

from importlib.metadata import PackageNotFoundError, version as _dist_version

from sioff.api import accessibility, index, off_targets, search

try:
    # Read the installed distribution so `sioff --version` reports what is
    # actually installed. A literal here silently disagrees with the wheel the
    # moment one is bumped without the other, and a version that lies is worse
    # than none.
    __version__ = _dist_version("sioff")
except PackageNotFoundError:  # running from a source tree, not installed
    __version__ = "0.1.0"

__all__ = ["off_targets", "accessibility", "index", "search", "__version__"]
