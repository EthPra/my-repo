"""Step 0 -- validate the golden set itself, before anything is built on it.

Cheap, and it catches a copy error before it becomes a phantom bug. Every expectation here
is asserted against the artifact; none is taken from prose. Two errors have already been
caught this way -- the density field and the "18 lines" -- both from documents that
recorded what someone intended rather than what the files contain.
"""

from __future__ import annotations

import pytest

from mcxray_wrapper.inputgen import newline_convention
from tests.conftest import (
    GOLDEN_INPUT_STEM,
    GOLDEN_NEWLINES,
    GOLDEN_RUN_ID,
    INPUT_ROLES,
)


def test_all_six_inputs_present(golden_inputs):
    missing = [
        role for role in INPUT_ROLES
        if not (golden_inputs / f"{GOLDEN_INPUT_STEM}.{role}").is_file()
    ]
    assert missing == [], f"golden inputs missing: {missing}"


def test_intensity_csv_present(golden_csv):
    assert golden_csv.is_file(), f"golden output CSV missing: {golden_csv}"


@pytest.mark.parametrize("role", INPUT_ROLES)
def test_inputs_have_no_bom(golden_inputs, role):
    raw = (golden_inputs / f"{GOLDEN_INPUT_STEM}.{role}").read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), f".{role} starts with a UTF-8 BOM"


@pytest.mark.parametrize("role", INPUT_ROLES)
def test_input_line_endings_match_the_files(golden_inputs, role):
    """Per-file, not a blanket rule.

    The four files the operator authored are CRLF; .mdl and .rp are unmodified vendor
    files and are LF-only. "CRLF on every input" is a documentation error -- the exe read
    both conventions in the same successful run.
    """
    raw = (golden_inputs / f"{GOLDEN_INPUT_STEM}.{role}").read_bytes()
    assert newline_convention(raw) == GOLDEN_NEWLINES[role]


@pytest.mark.parametrize("role", INPUT_ROLES)
def test_inputs_end_with_a_newline(golden_inputs, role):
    raw = (golden_inputs / f"{GOLDEN_INPUT_STEM}.{role}").read_bytes()
    assert raw.endswith(b"\n")
    if GOLDEN_NEWLINES[role] == "CRLF":
        assert raw.endswith(b"\r\n"), f".{role} is CRLF but lacks a trailing CRLF at EOF"


def test_sam_carries_the_corrected_density(golden_inputs):
    """The density-0 defect is corrected in this set. At 0, MC X-Ray auto-mixes from
    elemental densities and gives ~6.12-6.16 against the true 5.34 -- no error raised."""
    text = (golden_inputs / f"{GOLDEN_INPUT_STEM}.sam").read_text(encoding="ascii")
    density_lines = [
        line for line in text.splitlines() if line.startswith("UserDefinedMassDensity=")
    ]
    assert density_lines == ["UserDefinedMassDensity=5.34"]


def test_par_basefilename_stem_matches_the_output_files(golden_inputs, golden_outputs):
    """If the stem does not match, the inputs and outputs are not a matched pair, and
    everything downstream assumes they are."""
    text = (golden_inputs / f"{GOLDEN_INPUT_STEM}.par").read_text(encoding="ascii")
    base = [line for line in text.splitlines() if line.startswith("BaseFileName=")]
    assert base == [f"BaseFileName=Results/{GOLDEN_RUN_ID}"]

    produced = [path.name for path in golden_outputs.iterdir() if path.suffix != ".md"]
    assert produced, "golden/outputs contains no output files"
    mismatched = [name for name in produced if not name.startswith(GOLDEN_RUN_ID)]
    assert mismatched == [], (
        f"output file(s) {mismatched} do not carry the .par's stem {GOLDEN_RUN_ID!r}; "
        "inputs and outputs are not a matched pair"
    )


def test_output_csv_is_lf_only(golden_csv):
    """The output CSV is LF-only, unlike the CRLF inputs. These are not harmonised."""
    assert newline_convention(golden_csv.read_bytes()) == "LF"
