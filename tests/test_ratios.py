"""Stage 6 (ratios) acceptance tests.

Hermetic: mostly a hand-built intensity table with known numbers, so the ratio arithmetic is
checked against values computed independently of the implementation. One test also runs on the
real golden output via the parser, to confirm it works on the actual format.
"""

from __future__ import annotations

import pandas as pd
import pytest

from mcxray_wrapper.parser import parse_xray_intensities
from mcxray_wrapper.ratios import INTENSITY_COLUMN, compute_ratios
from mcxray_wrapper.spec import AS, BI, GA
from tests.conftest import GOLDEN_CSV, GOLDEN_RUN_ID

# Element symbols the parser attaches.
_SYMBOL = {GA: "Ga", AS: "As", BI: "Bi"}


def _row(run_id, z, line, intensity):
    return {
        "run_id": run_id, "x_bi": 0.1, "thickness_nm": 100, "n_electrons": 1000,
        "density_model": "walther_revised", "mass_density_g_cm3": 5.506,
        "detector_crystal_thickness_cm": 0.5,
        "Atomic number": z, "Element": _SYMBOL[z], "Line": f"Line {line}",
        INTENSITY_COLUMN: intensity,
    }


def _toy_run(run_id="toy"):
    """Round numbers so the two definitions are easy to check by hand."""
    return pd.DataFrame([
        # Ga: K = 100/50/20/10, L = 40/10  -> principal 100/40=2.5, summed 180/50=3.6
        _row(run_id, GA, "Ka1", 100), _row(run_id, GA, "Ka2", 50),
        _row(run_id, GA, "Kb1", 20), _row(run_id, GA, "Kb2", 10),
        _row(run_id, GA, "La", 40), _row(run_id, GA, "Lb1", 10),
        # As: K = 200/.../, L = 50/25 -> principal 200/50=4.0, summed 300/75=4.0
        _row(run_id, AS, "Ka1", 200), _row(run_id, AS, "Ka2", 60),
        _row(run_id, AS, "Kb1", 30), _row(run_id, AS, "Kb2", 10),
        _row(run_id, AS, "La", 50), _row(run_id, AS, "Lb1", 25),
        # Bi: L = 30/10/5/5, M = 20 -> principal 30/20=1.5, summed 50/20=2.5
        _row(run_id, BI, "La", 30), _row(run_id, BI, "Lb1", 10),
        _row(run_id, BI, "Lb2", 5), _row(run_id, BI, "Lg", 5),
        _row(run_id, BI, "Ma", 20),
    ])


def test_both_definitions_match_hand_calculation():
    r = compute_ratios(_toy_run()).iloc[0]
    assert r["Ga_K_L_principal"] == pytest.approx(100 / 40)          # 2.5
    assert r["Ga_K_L_summed"] == pytest.approx(180 / 50)             # 3.6
    assert r["As_K_L_principal"] == pytest.approx(200 / 50)          # 4.0
    assert r["As_K_L_summed"] == pytest.approx(300 / 75)             # 4.0
    assert r["Bi_L_M_principal"] == pytest.approx(30 / 20)           # 1.5
    assert r["Bi_L_M_summed"] == pytest.approx(50 / 20)              # 2.5


def test_metadata_carried_through():
    r = compute_ratios(_toy_run("keepme")).iloc[0]
    assert r["run_id"] == "keepme"
    assert r["thickness_nm"] == 100
    assert r["mass_density_g_cm3"] == 5.506


def test_no_kfactor_or_correction_columns():
    """Ratios only: no k-factor, absorption correction, or inverted composition sneaks in."""
    cols = compute_ratios(_toy_run()).columns
    banned = [c for c in cols if any(t in c.lower() for t in ("kfactor", "k_factor", "k*", "correct", "x_recovered", "quant"))]
    assert banned == []


def test_one_row_per_run():
    two = pd.concat([_toy_run("a"), _toy_run("b")], ignore_index=True)
    out = compute_ratios(two)
    assert len(out) == 2
    assert set(out["run_id"]) == {"a", "b"}


def test_zero_denominator_raises():
    df = _toy_run()
    df.loc[df["Line"] == "Line Ma", INTENSITY_COLUMN] = 0.0
    with pytest.raises(ValueError, match="zero denominator"):
        compute_ratios(df)


def test_missing_principal_line_raises():
    df = _toy_run()
    df = df[df["Line"] != "Line La"]  # drop Ga+Bi La (a principal line)
    with pytest.raises(ValueError, match="principal line"):
        compute_ratios(df)


def test_runs_on_real_golden_output():
    """Sanity: works on the actual parsed golden table, and the principal ratios match the
    values verified ad hoc earlier (Ga K/L and Bi L/M near 1.4-1.5 at 100 nm, x=0.1)."""
    golden = parse_xray_intensities(GOLDEN_CSV, GOLDEN_RUN_ID)
    # add the metadata columns compute_ratios carries (parser doesn't produce them)
    for col, val in (("x_bi", 0.1), ("thickness_nm", 100), ("n_electrons", 100000),
                     ("density_model", "walther_paper"), ("mass_density_g_cm3", 5.34),
                     ("detector_crystal_thickness_cm", 0.3)):
        golden[col] = val
    r = compute_ratios(golden).iloc[0]
    assert 1.0 < r["Ga_K_L_principal"] < 2.0
    assert 1.0 < r["Bi_L_M_principal"] < 2.0
    assert r["Ga_K_L_summed"] > r["Ga_K_L_principal"]  # summing K adds more than summing L
