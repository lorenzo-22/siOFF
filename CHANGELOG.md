# Changelog

All notable changes to siOFF are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/) with pre-release tags while the
`risearch` dependency is itself in alpha.

The release workflow publishes the section for the tagged version as the
GitHub release notes, so every release needs its section here first.

## [Unreleased]

### Changed

- The default install no longer pulls the compat (SSE4-only) polars runtime.
  polars prefers that runtime whenever it is present, so since 0.1.0 every
  install, AVX2 machines included, ran the slow one. `polars` is now a plain
  dependency (floor `1.43.2`, the same as risearch); CPUs without AVX2 install
  `sioff[lts-cpu]`, which also selects risearch's `lts-cpu` extra so the two
  packages agree on the runtime. For development, the `lts` dependency group
  (on by default) keeps `uv sync` working on the non-AVX2 development server;
  CI syncs with `--no-group lts` and therefore tests the default runtime.

## [0.1.0] - 2026-09-29

First public version, published on PyPI under the name `sioff`. The entries
below describe changes relative to the last internal pre-release build.

### Added

- API reference site at <https://lorenzo-22.github.io/siOFF/>, rendered from the
  docstrings with Zensical and mkdocstrings and published by GitHub Actions on
  every push to `main`. The public API (`sioff.off_targets`, `sioff.accessibility`,
  `sioff.index`, `sioff.search`) and the `sioff.core` layer now carry complete
  numpy-style docstrings, and CI fails on a docstring that does not match its
  signature or that the site cannot render.
- `sioff.off_targets(predictions=...)` takes an in-memory `polars.DataFrame`
  in the `sioff.search` schema, so `sioff.search` output feeds the analysis
  directly without an intermediate predictions file.
- `sioff.off_targets(accessibility=...)` takes the `dict[chrom -> DataFrame]`
  that `sioff.accessibility` returns, so the whole search → fold → score
  pipeline can run in memory.
- `sioff search -z/--matrix` and `sioff.search(matrix=...)` accept the path of
  a custom long-form DSM TSV table (`q1 q2 t1 t2 delta_g_kcal_per_mol`), as
  risearch 3.0.0a4 does, in addition to the bundled ids.
- Tag-triggered release workflow: builds and checks the distributions,
  publishes to PyPI via trusted publishing and creates the GitHub release.

### Changed

- `risearch` is installed from PyPI as a normal dependency, pinned exactly to
  `3.0.0a4`. `pip install sioff` now gives the complete pipeline, in-process
  `index` / `search` included. Reported energies differ from the previous git
  pin by at most 0.05 kcal/mol (regenerated upstream energy tables); hits and
  coordinates are unchanged.
- Package metadata declares the licence as the SPDX expression `BUSL-1.1`.

### Removed

- The `t99` (Turner 1999) energy parameter set, dropped upstream in risearch
  3.0.0a3. Use `t04`.

[Unreleased]: https://github.com/lorenzo-22/siOFF/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/lorenzo-22/siOFF/releases/tag/v0.1.0
