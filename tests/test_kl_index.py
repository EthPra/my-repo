"""Stage 7 (K/L re-indexing) acceptance tests.

Hermetic, same discipline as test_kfactors.py: hand-built intensity tables with numbers picked
so the join and the definition-matching are checkable independently of the implementation.
Never touches the real Results\\/Aggregated\\ directories.
"""

from __future__ import annotations

import pandas as pd
import pytest

from mcxray_wrapper.kl_index import (
    WALTHER_AXIS,
    axis_coverage,
    index_on_kl,
    write_kl_index,
)
from mcxray_wrapper.ratios import INTENSITY_COLUMN, compute_ratios
from mcxray_wrapper.spec import AS, BI, GA

_SYMBOL = {GA: "Ga", AS: "As", BI: "Bi"}


def _row(run_id, x_bi, thickness_nm, z, line, intensity):
    return {
        "run_id": run_id, "x_bi": x_bi, "thickness_nm": thickness_nm,
        "Atomic number": z, "Element": _SYMBOL[z], "Line": f"Line {line}",
        INTENSITY_COLUMN: intensity,
    }


def _toy_run(run_id, thickness_nm, ga_ka1, ga_la, as_ka1, as_la, bi_la, bi_ma, x_bi=0.2,
             bi_ka1=5.0):
    """Full shell membership, so BOTH line definitions are well defined.

    Sub-lines are set to round fractions of the principal so the summed shell totals are easy
    to compute by hand: K summed = 1.6 x Ka1, Ga/As L summed = 1.5 x La, Bi L summed = 2 x La.
    bi_ka1 defaults small -- Bi K is a real route that LO3 names, but a feeble one.
    """
    r = lambda z, line, val: _row(run_id, x_bi, thickness_nm, z, line, val)
    return pd.DataFrame([
        r(GA, "Ka1", ga_ka1), r(GA, "Ka2", 0.3 * ga_ka1),
        r(GA, "Kb1", 0.2 * ga_ka1), r(GA, "Kb2", 0.1 * ga_ka1),
        r(GA, "La", ga_la), r(GA, "Lb1", 0.5 * ga_la),
        r(AS, "Ka1", as_ka1), r(AS, "Ka2", 0.3 * as_ka1),
        r(AS, "Kb1", 0.2 * as_ka1), r(AS, "Kb2", 0.1 * as_ka1),
        r(AS, "La", as_la), r(AS, "Lb1", 0.5 * as_la),
        r(BI, "Ka1", bi_ka1), r(BI, "Ka2", 0.3 * bi_ka1),
        r(BI, "Kb1", 0.2 * bi_ka1), r(BI, "Kb2", 0.1 * bi_ka1),
        r(BI, "La", bi_la), r(BI, "Lb1", 0.4 * bi_la),
        r(BI, "Lb2", 0.4 * bi_la), r(BI, "Lg", 0.2 * bi_la),
        r(BI, "Ma", bi_ma),
    ])


def _set_a(**overrides):
    """Two Set A thicknesses with different K/L ratios, so ordering and joining are testable."""
    thin = _toy_run("thin", 2, ga_ka1=100, ga_la=80, as_ka1=200, as_la=160,
                    bi_la=30, bi_ma=20)
    thick = _toy_run("thick", 1024, ga_ka1=100, ga_la=25, as_ka1=200, as_la=40,
                     bi_la=30, bi_ma=20)
    return pd.concat([thin, thick], ignore_index=True)


# ---- the join: every k* row gets the ratios from its OWN run ----

def test_ratios_come_from_the_matching_run():
    combined = _set_a()
    out = index_on_kl(combined)
    ratios = compute_ratios(combined).set_index("run_id")

    for run_id in ("thin", "thick"):
        rows = out[(out["run_id"] == run_id) & (out["definition"] == "principal")]
        assert len(rows) == 16  # Bi_Ga 3x2 + Bi_As 3x2 + Ga_As 2x2
        for column, expected in (("ga_k_l", "Ga_K_L_principal"), ("as_k_l", "As_K_L_principal")):
            assert list(rows[column]) == pytest.approx(
                [ratios.at[run_id, expected]] * len(rows))


def test_ratio_definition_matches_the_row_definition():
    """A summed k* must be indexed by a summed K/L ratio -- never a mixed pair."""
    out = index_on_kl(_set_a())
    ratios = compute_ratios(_set_a()).set_index("run_id")

    summed = out[(out["run_id"] == "thin") & (out["definition"] == "summed")].iloc[0]
    principal = out[(out["run_id"] == "thin") & (out["definition"] == "principal")].iloc[0]

    assert summed["ga_k_l"] == pytest.approx(ratios.at["thin", "Ga_K_L_summed"])
    assert principal["ga_k_l"] == pytest.approx(ratios.at["thin", "Ga_K_L_principal"])
    # The toy numbers make the two definitions genuinely different, so this is a real check.
    assert summed["ga_k_l"] != pytest.approx(principal["ga_k_l"])


def test_hand_calculated_kl_ratio():
    """Ga K/L principal = Ka1/La = 100/80 = 1.25; summed = 160/120 = 1.3333."""
    out = index_on_kl(_set_a())
    thin_p = out[(out["run_id"] == "thin") & (out["definition"] == "principal")].iloc[0]
    thin_s = out[(out["run_id"] == "thin") & (out["definition"] == "summed")].iloc[0]
    assert thin_p["ga_k_l"] == pytest.approx(100 / 80)
    assert thin_s["ga_k_l"] == pytest.approx(160 / 120)


# ---- Walther's per-figure x-axis ----

def test_walther_x_uses_the_axis_that_figure_uses():
    out = index_on_kl(_set_a())
    for route, (figure, stem) in WALTHER_AXIS.items():
        rows = out[out["route"] == route]
        assert set(rows["walther_figure"]) == {figure}
        expected = rows["ga_k_l"] if stem == "Ga_K_L" else rows["as_k_l"]
        assert list(rows["walther_x"]) == pytest.approx(list(expected))


def test_bi_routes_never_indexed_on_a_bi_ratio():
    """Bi K lines are 77-87 keV -- unusable on a standard detector, so Bi has no K/L axis."""
    out = index_on_kl(_set_a())
    assert set(out["walther_x_label"]) <= {"Ga K/L", "As K/L"}


def test_curves_sorted_by_increasing_kl():
    out = index_on_kl(_set_a())
    one = out[(out["route"] == "Bi_As") & (out["heavy_shell"] == "L")
              & (out["light_shell"] == "K") & (out["definition"] == "principal")]
    assert list(one["walther_x"]) == sorted(one["walther_x"])
    # increasing K/L must correspond to increasing thickness -- the physical direction
    assert list(one["thickness_nm"]) == [2, 1024]


# ---- guards ----

def test_missing_ratio_row_fails_loudly():
    combined = _set_a()
    # A k* row whose run has no ratio row would silently become NaN on a left join.
    ratios = compute_ratios(combined)
    trimmed = ratios[ratios["run_id"] != "thick"]
    import mcxray_wrapper.kl_index as kl

    original = kl.compute_ratios
    kl.compute_ratios = lambda _df: trimmed
    try:
        with pytest.raises(ValueError, match="no ratio row"):
            index_on_kl(combined)
    finally:
        kl.compute_ratios = original


def test_no_recovered_x_columns():
    """Re-indexing only. Inverting against these curves is Stage 7, a separate step."""
    cols = index_on_kl(_set_a()).columns
    banned = [c for c in cols if any(t in c.lower() for t in ("recovered", "inverted", "quant"))]
    assert banned == []


# ---- coverage report and the writer ----

def test_axis_coverage_reports_real_spans():
    out = index_on_kl(_set_a())
    cov = axis_coverage(out)
    assert set(cov["walther_figure"]) == {"Fig 3 (bottom)", "Fig 4", "Fig 5"}
    fig4 = cov[cov["walther_figure"] == "Fig 4"].iloc[0]
    assert fig4["x_axis"] == "As K/L"
    assert fig4["x_min"] == pytest.approx(out[out["route"] == "Bi_As"]["walther_x"].min())
    assert fig4["n_curves"] == 12  # Bi's 3 heavy shells x 2 light shells x 2 definitions


def test_write_kl_index_round_trips(tmp_path):
    combined_csv = tmp_path / "combined.csv"
    _set_a().to_csv(combined_csv, index=False)

    out = write_kl_index(combined_csv, tmp_path / "Aggregated")
    assert out.name == "kstar_vs_kl_ratio_setA.csv"

    written = pd.read_csv(out)
    expected = index_on_kl(pd.read_csv(combined_csv))
    assert list(written["k_star"]) == pytest.approx(list(expected["k_star"]))
    assert list(written["walther_x"]) == pytest.approx(list(expected["walther_x"]))
