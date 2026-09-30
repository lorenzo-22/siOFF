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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sioff.api import accessibility, index, off_targets, search

    __version__: str

__all__ = ["off_targets", "accessibility", "index", "search", "__version__"]

_API_NAMES = frozenset({"off_targets", "accessibility", "index", "search"})


def __getattr__(name: str) -> object:
    # PEP 562 lazy re-exports. `sioff.api` drags in polars, numpy, pyarrow and
    # Biopython — seconds on a cold cache — and every `import sioff.<anything>`
    # runs this file first. Resolving on first access keeps `sioff --help` and
    # `sioff --version` from paying for a pipeline they never run. The resolved
    # value is cached in the module dict, so later lookups bypass this hook.
    if name in _API_NAMES:
        from sioff import api

        value = getattr(api, name)
        globals()[name] = value
        return value
    if name == "__version__":
        # Read the installed distribution so `sioff --version` reports what is
        # actually installed. A literal here silently disagrees with the wheel
        # the moment one is bumped without the other, and a version that lies
        # is worse than none. importlib.metadata itself costs ~150 ms, hence
        # lazy.
        from importlib.metadata import PackageNotFoundError, version

        try:
            resolved = version("sioff")
        except PackageNotFoundError:  # running from a source tree, not installed
            resolved = "0.1.0"
        globals()["__version__"] = resolved
        return resolved
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
