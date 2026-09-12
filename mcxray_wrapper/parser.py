"""Parse MC X-Ray's `<stem>_XrayIntensities.csv` into a tidy DataFrame.

LOCKED: the file's ten columns, their order, and their meaning. All four intensity columns
are preserved -- the pairwise differences carry physics (Generated -> Emitted is specimen
self-absorption; Emitted -> Emitted Detected is window plus detector efficiency), so
nothing may be dropped or collapsed.

GENUINE PARAMETER: run_id, supplied by the caller so tables from different runs can later
be concatenated with provenance intact.

This module computes NO ratios, k-factors, or derived quantities of any kind. That is a
hard architectural rule, not a stylistic one: open atomic-data questions (whether `La`
includes L-alpha-2; whether Bi M-lines beyond M-alpha are modelled) mean any derived
number may need re-deriving later. That must be possible from the stored raw table without
re-running simulations.

Format traps, all confirmed against the real validation output:

    * The separator is ", " (comma + space), not a bare comma.
    * Every row, header included, ends in a trailing comma -> 11 fields, the last empty.
      There are 10 real fields.
    * `Line` values carry trailing spaces ("Line La ").
    * Rows are keyed on `Atomic number`. `Index Atom` is only the element's position in
      the region's composition list and carries no chemical meaning.
    * The file is LF-only, unlike the CRLF inputs. These are not harmonised.
    * Zero-intensity rows are legitimate and are never dropped: in the golden output Ga
      Line Kb2 has all four intensity columns at 0 with a non-zero detector efficiency.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from mcxray_wrapper.spec import ELEMENT_SYMBOLS

# The ten real columns, in file order, after stripping whitespace from the header.
FILE_COLUMNS = [
    "Index Region",
    "Index Atom",
    "Atomic number",
    "Line",
    "Line energy (keV)",
    "Intensity Generated (photons/e/sr)",
    "Intensity Generated Detected (photons)",
    "Intensity Emitted (photons/e/sr)",
    "Intensity Emitted Detected (photons)",
    "Detector efficiency",
]

INT_COLUMNS = ["Index Region", "Index Atom", "Atomic number"]
TEXT_COLUMNS = ["Line"]
FLOAT_COLUMNS = [
    "Line energy (keV)",
    "Intensity Generated (photons/e/sr)",
    "Intensity Generated Detected (photons)",
    "Intensity Emitted (photons/e/sr)",
    "Intensity Emitted Detected (photons)",
    "Detector efficiency",
]

INTENSITY_COLUMNS = [
    "Intensity Generated (photons/e/sr)",
    "Intensity Generated Detected (photons)",
    "Intensity Emitted (photons/e/sr)",
    "Intensity Emitted Detected (photons)",
]

# run_id leads (it is the provenance key); Element sits beside the atomic number it
# derives from; the file's own ten columns keep their order otherwise.
OUTPUT_COLUMNS = [
    "run_id",
    "Index Region",
    "Index Atom",
    "Atomic number",
    "Element",
    "Line",
    "Line energy (keV)",
    "Intensity Generated (photons/e/sr)",
    "Intensity Generated Detected (photons)",
    "Intensity Emitted (photons/e/sr)",
    "Intensity Emitted Detected (photons)",
    "Detector efficiency",
]


def _to_numeric_strict(values: pd.Series, column: str, path: Path) -> pd.Series:
    """Convert or raise. A non-numeric value is an error, never a silently coerced NaN."""
    try:
        return pd.to_numeric(values, errors="raise")
    except (ValueError, TypeError) as exc:
        raise ValueError(f"non-numeric value in column {column!r} of {path}: {exc}") from exc


def parse_xray_intensities(path: Path | str, run_id: str) -> pd.DataFrame:
    """Read one `_XrayIntensities.csv`; return one row per emission line per region."""
    path = Path(path)
    # na_filter=False keeps pandas' NA sentinels out of the path entirely. With it on,
    # values like "n/a", "NA" or "null" become NaN during read -- the exact silent
    # coercion this parser exists to refuse -- and would surface as "missing" rather than
    # as the non-numeric junk they are. Every field arrives as a string; emptiness is
    # judged here, not by pandas.
    raw = pd.read_csv(path, dtype=str, skipinitialspace=True, na_filter=False)

    # The trailing comma gives an eleventh, empty field. Handle it explicitly rather than
    # letting an empty column propagate.
    if len(raw.columns) != len(FILE_COLUMNS) + 1:
        raise ValueError(
            f"{path}: expected {len(FILE_COLUMNS)} real columns plus one empty trailing "
            f"field, got {len(raw.columns)}: {list(raw.columns)}"
        )
    trailing = raw.columns[-1]
    if not (raw[trailing].str.strip() == "").all():
        raise ValueError(
            f"{path}: the trailing 11th field is not empty; it holds "
            f"{raw[trailing][raw[trailing].str.strip() != ''].unique()[:5]}"
        )
    raw = raw.drop(columns=[trailing])

    raw.columns = [str(column).strip() for column in raw.columns]
    if list(raw.columns) != FILE_COLUMNS:
        raise ValueError(
            f"{path}: unexpected columns.\n  found:    {list(raw.columns)}\n"
            f"  expected: {FILE_COLUMNS}"
        )

    # `Line` labels carry trailing spaces; strip every text field on read.
    for column in raw.columns:
        raw[column] = raw[column].str.strip()

    empty = [column for column in raw.columns if (raw[column] == "").any()]
    if empty:
        raise ValueError(f"{path}: empty values in column(s) {empty}")

    parsed = pd.DataFrame(index=raw.index)
    parsed["run_id"] = run_id
    for column in INT_COLUMNS:
        numbers = _to_numeric_strict(raw[column], column, path)
        if (numbers % 1 != 0).any():
            raise ValueError(f"{path}: non-integer value in integer column {column!r}")
        parsed[column] = numbers.astype("int64")
    for column in TEXT_COLUMNS:
        parsed[column] = raw[column]
    for column in FLOAT_COLUMNS:
        parsed[column] = _to_numeric_strict(raw[column], column, path).astype("float64")

    # Key on Atomic number, never Index Atom. An unknown Z is an anomaly worth stopping
    # for, not a NaN to carry downstream.
    unknown = sorted(set(parsed["Atomic number"]) - set(ELEMENT_SYMBOLS))
    if unknown:
        raise ValueError(
            f"{path}: atomic number(s) {unknown} have no element symbol; this parser knows "
            f"{sorted(ELEMENT_SYMBOLS)} (Ga/As/Bi)"
        )
    parsed["Element"] = parsed["Atomic number"].map(ELEMENT_SYMBOLS)

    return parsed[OUTPUT_COLUMNS]
