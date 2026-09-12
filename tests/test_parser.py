"""Golden regression test 2 -- the acceptance test for the output parser.

Every expected literal here was read from the golden CSV at test-writing time. None is
imported from memory, from a reference table, or from the build prompt -- both literals
the prompt supplied for this file were wrong (it said 18 rows, the file has 21; it said Bi
La is 10.839, the file says 10.84).
"""

from __future__ import annotations

import pandas as pd
import pytest

from mcxray_wrapper.parser import (
    FILE_COLUMNS,
    INTENSITY_COLUMNS,
    OUTPUT_COLUMNS,
    parse_xray_intensities,
)
from tests.conftest import GOLDEN_RUN_ID

# Read from the golden CSV: 21 rows, Ga 6, As 6, Bi 9.
EXPECTED_LINES = {
    ("Ga", "Line Ka1"), ("Ga", "Line Ka2"), ("Ga", "Line Kb1"),
    ("Ga", "Line Kb2"), ("Ga", "Line La"), ("Ga", "Line Lb1"),
    ("As", "Line Ka1"), ("As", "Line Ka2"), ("As", "Line Kb1"),
    ("As", "Line Kb2"), ("As", "Line La"), ("As", "Line Lb1"),
    ("Bi", "Line Ka1"), ("Bi", "Line Ka2"), ("Bi", "Line Kb1"),
    ("Bi", "Line Kb2"), ("Bi", "Line La"), ("Bi", "Line Lb1"),
    ("Bi", "Line Lb2"), ("Bi", "Line Lg"), ("Bi", "Line Ma"),
}
EXPECTED_ROW_COUNT = 21

# Read from the golden CSV. Energies are reported to ~4 significant figures.
EXPECTED_ENERGIES = {
    ("Bi", "Line La"): 10.84,
    ("Bi", "Line Ma"): 2.423,
    ("Ga", "Line Ka1"): 9.251,
    ("As", "Line Ka1"): 10.543,
}


@pytest.fixture
def parsed(golden_csv):
    return parse_xray_intensities(golden_csv, run_id=GOLDEN_RUN_ID)


def test_row_count(parsed):
    """21, not the 18 that appears in the project docs -- that is the number of lines
    cross-checked against Walther's Table 1, not a row count."""
    assert len(parsed) == EXPECTED_ROW_COUNT


def test_expected_element_line_pairs(parsed):
    actual = set(zip(parsed["Element"], parsed["Line"]))
    assert actual == EXPECTED_LINES


def test_rows_per_element(parsed):
    counts = parsed["Element"].value_counts().to_dict()
    assert counts == {"Bi": 9, "Ga": 6, "As": 6}


@pytest.mark.parametrize("key, expected", sorted(EXPECTED_ENERGIES.items()))
def test_line_energies(parsed, key, expected):
    element, line = key
    row = parsed[(parsed["Element"] == element) & (parsed["Line"] == line)]
    assert len(row) == 1
    assert row["Line energy (keV)"].iloc[0] == expected


def test_columns_and_order(parsed):
    assert list(parsed.columns) == OUTPUT_COLUMNS


def test_no_intensity_column_is_dropped(parsed):
    """The pairwise differences carry physics: Generated -> Emitted is specimen
    self-absorption, Emitted -> Emitted Detected is window plus detector efficiency."""
    for column in FILE_COLUMNS:
        assert column in parsed.columns


def test_no_trailing_empty_column(parsed):
    """The trailing comma yields an 11th, empty field. It must not propagate."""
    assert not any(str(column).startswith("Unnamed") for column in parsed.columns)
    assert len(parsed.columns) == len(FILE_COLUMNS) + 2  # + run_id + Element


def test_intensities_are_numeric_and_non_negative(parsed):
    for column in INTENSITY_COLUMNS:
        assert pd.api.types.is_float_dtype(parsed[column])
        assert parsed[column].notna().all()
        assert (parsed[column] >= 0).all()


def test_zero_intensity_rows_survive(parsed):
    """Ga Kb2 has all four intensity columns at 0 with a non-zero detector efficiency.
    Legitimate: assert non-negative, never strictly positive, and never drop it."""
    row = parsed[(parsed["Element"] == "Ga") & (parsed["Line"] == "Line Kb2")]
    assert len(row) == 1
    assert (row[INTENSITY_COLUMNS].iloc[0] == 0).all()
    assert row["Detector efficiency"].iloc[0] == 0.999731


def test_detector_efficiency_is_a_fraction(parsed):
    efficiency = parsed["Detector efficiency"]
    assert ((efficiency >= 0) & (efficiency <= 1)).all()


def test_line_labels_are_stripped(parsed):
    """Golden carries trailing spaces, e.g. "Line La "."""
    assert (parsed["Line"] == parsed["Line"].str.strip()).all()
    assert "Line La" in set(parsed["Line"])


def test_atomic_numbers_are_the_key(parsed):
    """Index Atom is only a position in the region's composition list."""
    assert set(parsed["Atomic number"]) == {31, 33, 83}
    mapping = dict(zip(parsed["Atomic number"], parsed["Element"]))
    assert mapping == {31: "Ga", 33: "As", 83: "Bi"}


def test_run_id_is_attached(parsed):
    assert (parsed["run_id"] == GOLDEN_RUN_ID).all()


def test_round_trip(parsed, tmp_path):
    path = tmp_path / "round_trip.csv"
    parsed.to_csv(path, index=False)
    reread = pd.read_csv(path)
    pd.testing.assert_frame_equal(parsed, reread)


def test_parser_computes_nothing_derived(parsed):
    """Raw intensities only. Open atomic-data questions mean any derived number may need
    re-deriving later, from the stored table rather than by re-simulating."""
    derived = [
        column for column in parsed.columns
        if any(word in column.lower() for word in ("ratio", "k-factor", "kfactor", "corrected"))
    ]
    assert derived == []


def test_non_numeric_value_is_an_error_not_a_nan(golden_csv, tmp_path):
    """Strict parsing: a non-numeric value in a numeric column stops the run."""
    corrupted = tmp_path / "corrupted.csv"
    text = golden_csv.read_text(encoding="ascii")
    corrupted.write_text(text.replace("9.251", "n/a"), encoding="ascii", newline="")
    with pytest.raises(ValueError, match="non-numeric"):
        parse_xray_intensities(corrupted, run_id="corrupted")


def test_unknown_atomic_number_is_an_error(golden_csv, tmp_path):
    """An unexpected element is an anomaly worth stopping for, not a NaN to carry on with."""
    corrupted = tmp_path / "unknown_z.csv"
    text = golden_csv.read_text(encoding="ascii")
    corrupted.write_text(text.replace(", 31, ", ", 79, "), encoding="ascii", newline="")
    with pytest.raises(ValueError, match="no element symbol"):
        parse_xray_intensities(corrupted, run_id="unknown_z")
