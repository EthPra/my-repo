"""Golden-set paths and the validation RunSpec.

`Golden/` is read-only ground truth: a matched pair of the six inputs that were actually
fed to MC X-Ray and the outputs that run actually produced. Nothing here writes to it.

Note the input stem (GaAsBi_val) and the output stem (GaAsBi_100nm_x010_ATW_rho534) differ.
That is a historical artifact of the validation run, not a design: run_id now drives both,
so the generated filenames intentionally differ from the golden ones and files are compared
by role rather than by name.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mcxray_wrapper.spec import WALTHER_PAPER, RunSpec

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN_INPUTS = REPO_ROOT / "Golden" / "inputs"
GOLDEN_OUTPUTS = REPO_ROOT / "Golden" / "outputs"

GOLDEN_INPUT_STEM = "GaAsBi_val"
GOLDEN_RUN_ID = "GaAsBi_100nm_x010_ATW_rho534"
GOLDEN_CSV = GOLDEN_OUTPUTS / f"{GOLDEN_RUN_ID}_XrayIntensities.csv"

INPUT_ROLES = ("sim", "sam", "mic", "par", "mdl", "rp")

# Established from the golden files themselves, not from documentation: the four files the
# operator authored are CRLF, the two the vendor ships are LF, and MC X-Ray read both in
# the same successful run.
GOLDEN_NEWLINES = {
    "sim": "CRLF",
    "sam": "CRLF",
    "mic": "CRLF",
    "par": "CRLF",
    "mdl": "LF",
    "rp": "LF",
}


def validation_run_spec() -> RunSpec:
    """The spec that reproduces the golden run. Importable outside pytest too.

    Pins density_model=WALTHER_PAPER and detector_crystal_thickness_cm=0.3 explicitly:
    the golden set was generated before Walther's 2026-07-19 revisions, so it carries the
    paper density (5.34 at x=0.1) and the 0.3 cm crystal. Production runs default to
    WALTHER_REVISED / 0.5 cm; this fixture must not follow those defaults or the byte-for-
    byte golden gate would break. That divergence is the point -- it documents exactly what
    the golden set embeds.
    """
    return RunSpec(
        run_id=GOLDEN_RUN_ID,
        x_bi=0.1,
        thickness_nm=100,
        n_electrons=100000,
        window="ATW",
        density_model=WALTHER_PAPER,
        detector_crystal_thickness_cm=0.3,
    )


@pytest.fixture
def golden_inputs() -> Path:
    return GOLDEN_INPUTS


@pytest.fixture
def golden_outputs() -> Path:
    return GOLDEN_OUTPUTS


@pytest.fixture
def golden_csv() -> Path:
    return GOLDEN_CSV


@pytest.fixture
def validation_spec() -> RunSpec:
    return validation_run_spec()
