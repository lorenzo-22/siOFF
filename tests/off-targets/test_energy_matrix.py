"""Energy-parameter-set (DSM) selection must cover everything risearch ships.

risearch 3.0.0a4 bundles four nearest-neighbour scoring models, verified
against the installed bindings (Turner 1999, `t99`, was dropped upstream in
3.0.0a3):

    t04          Turner 2004            (RNA-RNA, default)
    slh04        SantaLucia-Hicks 2004  (DNA-DNA)
    s95-rna-dna  Sugimoto 1995          (RNA query / DNA target)
    s95-dna-rna  Sugimoto 1995          (DNA query / RNA target)

siOFF previously hard-rejected everything but the Turner tables, which put the
two Sugimoto hybrid tables out of reach — the ones that apply to DNA-based
oligos. The choice is not cosmetic: on the shipped fixtures the tables return
different E_min values, so it changes which off-targets are found and their
energies.
"""

import pytest

from sioff.services.risearch_service import (
    VALID_DSM_IDS,
    RIsearchError,
    RIsearchService,
)


class TestValidDsmIds:
    def test_every_model_risearch_ships_is_allowed(self):
        assert VALID_DSM_IDS == frozenset(
            {"t04", "slh04", "s95-rna-dna", "s95-dna-rna"}
        )

    @pytest.mark.parametrize("matrix", sorted(VALID_DSM_IDS))
    def test_each_one_passes_validation(self, tmp_path, matrix):
        """Validation runs before risearch is imported, so this needs no extra."""
        index = tmp_path / "g.idx"
        index.touch()
        (tmp_path / "q.fa").write_text(">q\nACGU\n")

        service = RIsearchService()
        service._target_registry[str(index)] = tmp_path / "g.fa"

        # Reaching the import means validation accepted the matrix. Without the
        # optional dependency installed that surfaces as a RIsearchError naming
        # the missing module, never one complaining about the matrix.
        try:
            service.run_search(
                query_path=tmp_path / "q.fa",
                index_path=index,
                target_fasta=tmp_path / "g.fa",
                matrix=matrix,
            )
        except RIsearchError as exc:
            assert "matrix" not in str(exc), f"{matrix} was rejected: {exc}"
        except Exception:
            pass  # any other failure is downstream of validation

    def test_an_unknown_id_is_rejected_with_the_valid_set_named(self, tmp_path):
        index = tmp_path / "g.idx"
        index.touch()
        (tmp_path / "q.fa").write_text(">q\nACGU\n")
        service = RIsearchService()
        service._target_registry[str(index)] = tmp_path / "g.fa"

        with pytest.raises(RIsearchError) as excinfo:
            service.run_search(
                query_path=tmp_path / "q.fa",
                index_path=index,
                target_fasta=tmp_path / "g.fa",
                matrix="bogus",
            )

        message = str(excinfo.value)
        assert "bogus" in message
        for valid in VALID_DSM_IDS:
            assert valid in message, f"error should list {valid}"
        assert "TSV" in message, "error should mention the custom-table option"

    def test_a_path_to_an_existing_tsv_table_is_accepted(self, tmp_path):
        """risearch 3.0.0a4 loads a custom long-form DSM table from a TSV path.

        siOFF only checks that the file exists; the table format itself is
        risearch's business and it raises on a malformed one.
        """
        index = tmp_path / "g.idx"
        index.touch()
        (tmp_path / "q.fa").write_text(">q\nACGU\n")
        table = tmp_path / "custom.tsv"
        table.write_text("q1\tq2\tt1\tt2\tdelta_g_kcal_per_mol\n")
        service = RIsearchService()
        service._target_registry[str(index)] = tmp_path / "g.fa"

        for matrix in (table, str(table)):
            try:
                service.run_search(
                    query_path=tmp_path / "q.fa",
                    index_path=index,
                    target_fasta=tmp_path / "g.fa",
                    matrix=matrix,
                )
            except RIsearchError as exc:
                assert "unknown matrix" not in str(exc), f"{matrix!r} rejected: {exc}"
            except Exception:
                pass  # downstream of validation (empty index / bad table)

    def test_a_missing_path_is_rejected_before_risearch_runs(self, tmp_path):
        index = tmp_path / "g.idx"
        index.touch()
        (tmp_path / "q.fa").write_text(">q\nACGU\n")
        service = RIsearchService()
        service._target_registry[str(index)] = tmp_path / "g.fa"

        with pytest.raises(RIsearchError) as excinfo:
            service.run_search(
                query_path=tmp_path / "q.fa",
                index_path=index,
                target_fasta=tmp_path / "g.fa",
                matrix=tmp_path / "nope.tsv",
            )
        message = str(excinfo.value)
        assert "nope.tsv" in message
        assert "TSV" in message

    def test_the_bare_directory_name_s95_is_not_a_valid_id(self, tmp_path):
        """`s95` is the data directory; the ids are s95-rna-dna / s95-dna-rna.

        risearch itself rejects it with "unknown DSM id 's95'", so accepting it
        here would only defer the failure.
        """
        index = tmp_path / "g.idx"
        index.touch()
        (tmp_path / "q.fa").write_text(">q\nACGU\n")
        service = RIsearchService()
        service._target_registry[str(index)] = tmp_path / "g.fa"

        with pytest.raises(RIsearchError, match="s95"):
            service.run_search(
                query_path=tmp_path / "q.fa",
                index_path=index,
                target_fasta=tmp_path / "g.fa",
                matrix="s95",
            )


class TestPublicApiExposesTheSearchKnobs:
    """`sioff.search` must offer what the CLI offers.

    `--matrix`/`-z` and the seed-geometry flags existed on the CLI while the
    Python API silently pinned every library user to the defaults.
    """

    @pytest.mark.parametrize(
        "parameter", ["matrix", "seed_start", "seed_end", "seed_wobble"]
    )
    def test_parameter_is_present(self, parameter):
        import inspect

        import sioff

        assert parameter in inspect.signature(sioff.search).parameters

    def test_defaults_match_the_core_layer(self):
        import inspect

        import sioff
        from sioff.core.risearch import run_search as core_search

        api = inspect.signature(sioff.search).parameters
        core = inspect.signature(core_search).parameters

        for name in ("matrix", "seed_start", "seed_end", "seed_wobble"):
            assert api[name].default == core[name].default, (
                f"{name} default drifted between the API and core layers"
            )
