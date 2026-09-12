"""Stage 7 (part 2) -- k* re-indexed on a measurable K/L ratio instead of thickness.

Reproduces the x-axis of Walther's Figures 3 (bottom), 4 and 5, which plot k* against a
K/L line-intensity ratio rather than against foil thickness. His stated reason (Fig. 1
discussion) is that doing so "reduces both the dependence on real foil thickness measurements
and the effect of detector sensitivities changing with detector type or entrance window
thickness ... providing an inherent self-calibration."

WHY THIS MATTERS HERE, beyond matching a figure. roundtrip.py looks up k*(100 nm) using the
KNOWN thickness of the Set B runs. A real experimenter does not have that number -- so that
round trip is held out in x but NOT in t: it is handed one of the two unknowns. A K/L ratio is
measured from the same spectrum being quantified, so re-indexing on it is what makes a round
trip held out in both. This module builds the calibration table that change needs; it does not
itself perform the inversion (that stays in roundtrip.py / Stage 7, Ethan's).

WHICH K/L RATIO -- deliberately not chosen here. Walther uses a different element per figure:

    Fig. 3 (Bi vs Ga lines)  ->  Ga K/L
    Fig. 4 (Bi vs As lines)  ->  As K/L
    Fig. 5 (Ga vs As lines)  ->  Ga K/L

For the two Bi routes that is the reference (lighter) element -- Bi's own K lines sit at
77-87 keV and are, in his words, too hard for any standard EDS detector, so Bi has no usable
K/L ratio. For Ga-vs-As he uses Ga, the heavier of that pair, not the reference element, so
there is no single rule covering all three. Rather than invent one, BOTH available ratios
(Ga K/L and As K/L) are attached to every row, and `walther_figure` records which one his
corresponding figure uses. Same store-both discipline as ratios.py's two line definitions:
the choice for inversion is Stage 7, Ethan's.

The K/L ratio is taken under the SAME line definition as the k* on that row -- a `summed` k*
is indexed by a `summed` K/L ratio, never mixed.

Both inputs are already-derived tables read back from Aggregated\\: no simulator, no
re-derivation of anything kfactors.py or ratios.py already expose.
"""

from __future__ import annotations

import pandas as pd

from mcxray_wrapper.kfactors import calibration_curves
from mcxray_wrapper.ratios import compute_ratios

# Which of his figures each route corresponds to, and the element whose K/L ratio he uses
# as that figure's x-axis. Column names match ratios.compute_ratios' output.
WALTHER_AXIS = {
    "Bi_Ga": ("Fig 3 (bottom)", "Ga_K_L"),
    "Bi_As": ("Fig 4", "As_K_L"),
    "Ga_As": ("Fig 5", "Ga_K_L"),
}

# Both ratios are attached to every row regardless of route; these are the column stems.
_RATIO_STEMS = ("Ga_K_L", "As_K_L")


def index_on_kl(combined: pd.DataFrame) -> pd.DataFrame:
    """Set A k* curves with both K/L ratios attached, ready to plot on Walther's axes.

    One row per (run, route, heavy shell, light shell, definition) -- the same grain as
    kfactors.calibration_curves, which it calls rather than recomputing k*. Adds:

      ga_k_l, as_k_l   both ratios at this run, under this row's own line definition
      walther_figure   which published figure this route reproduces
      walther_x        the ratio value that figure uses as its x-axis
      walther_x_label  which element's K/L that is, e.g. "As K/L"

    Sorted so each (route, shells, definition) group reads bottom-to-top as a curve in
    increasing K/L -- i.e. increasing thickness, the direction his figures are drawn in.
    """
    cal = calibration_curves(combined)
    ratios = compute_ratios(combined)

    wanted = ["run_id"] + [f"{stem}_{d}" for stem in _RATIO_STEMS for d in ("principal", "summed")]
    missing = [c for c in wanted if c not in ratios.columns]
    if missing:
        raise ValueError(f"ratio table is missing expected columns: {missing}")

    merged = cal.merge(ratios[wanted], on="run_id", how="left", validate="many_to_one")
    if merged[wanted[1]].isna().any():
        orphans = sorted(merged.loc[merged[wanted[1]].isna(), "run_id"].unique())
        raise ValueError(f"no ratio row for run(s): {orphans}")

    # Pick each row's ratios under that row's own line definition -- never mix a summed k*
    # with a principal K/L.
    for stem in _RATIO_STEMS:
        merged[stem.lower()] = merged.apply(
            lambda r, s=stem: r[f"{s}_{r['definition']}"], axis=1)

    merged["walther_figure"] = merged["route"].map(lambda r: WALTHER_AXIS[r][0])
    axis_stem = merged["route"].map(lambda r: WALTHER_AXIS[r][1])
    merged["walther_x"] = [merged.at[i, stem.lower()] for i, stem in zip(merged.index, axis_stem)]
    merged["walther_x_label"] = axis_stem.map(lambda s: s.replace("_K_L", " K/L"))

    keep = [
        "run_id", "x_bi", "thickness_nm", "route", "heavy_shell", "light_shell", "definition",
        "ga_k_l", "as_k_l", "walther_figure", "walther_x", "walther_x_label", "k_star",
    ]
    out = merged[[c for c in keep if c in merged.columns]]
    return out.sort_values(
        ["route", "heavy_shell", "light_shell", "definition", "walther_x"]
    ).reset_index(drop=True)


def axis_coverage(indexed: pd.DataFrame) -> pd.DataFrame:
    """Per figure, the span of K/L this run matrix actually covers.

    Walther's figures are drawn on 0-6 axes. Whether our curves overlay his or only cover part
    of his range is a property of the run matrix (Set A stops at 1024 nm), so it is reported
    rather than assumed -- an overlay claim needs the spans stated beside it.
    """
    rows = []
    for (fig, label), group in indexed.groupby(["walther_figure", "walther_x_label"], sort=False):
        rows.append({
            "walther_figure": fig,
            "x_axis": label,
            "x_min": group["walther_x"].min(),
            "x_max": group["walther_x"].max(),
            "k_star_min": group["k_star"].min(),
            "k_star_max": group["k_star"].max(),
            "n_curves": group.groupby(
                ["route", "heavy_shell", "light_shell", "definition"]).ngroups,
        })
    return pd.DataFrame(rows).sort_values("walther_figure").reset_index(drop=True)


def write_kl_index(combined_csv: "str | object", output_dir) -> object:
    """Read Stage 5's combined table, re-index Set A's k* on K/L, write it into output_dir."""
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    combined = pd.read_csv(combined_csv)
    indexed = index_on_kl(combined)
    out = output_dir / "kstar_vs_kl_ratio_setA.csv"
    indexed.to_csv(out, index=False)
    return out
