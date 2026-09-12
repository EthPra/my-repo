"""Figure 4 -- the sum peak is composition-selective. Why it decides the low-x question.

THE ARTEFACT. Ga La (1.098 keV) and As La (1.282) arriving within the detector's resolving time
are recorded as one photon at 2.380 keV. Bi Ma sits at 2.423 -- a 43 eV gap, which is 0.47 of the
detector linewidth, so the fake counts are physically indistinguishable from bismuth.

WHY IT IS WORSE WHERE IT MATTERS MOST. The pile-up rate is set by the Ga and As lines, which
barely change with Bi content, while the Bi M signal it contaminates falls away with x. The same
instrumental imperfection therefore does far more damage at low Bi content -- exactly the regime
the measurability question lives in.

  Left  -- fake counts as a fraction of the true Bi M signal. At a 1% level this is 97% of Bi M
           at x = 0.01 and 4% at x = 0.20: a factor of ~23 across the sampled range.
  Right -- what that does to the observable. Bi L/M is the diagnostic ratio Walther plots, and
           the corrupted curve departs from the clean one increasingly as Bi runs out.

The level is SWEPT (0.1 / 1 / 10%) and never defaulted. Walther fitted ~15% to close a gap
between his measured and simulated Bi L/M, but that number is entangled with his own Bi M
reference and is not portable -- so it is bracketed rather than adopted.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from matplotlib.ticker import ScalarFormatter

from figures.style import MUTED, caption, new_figure, save, series_style, trim_spines
from mcxray_wrapper.matrix import SET_B_THICKNESS_NM, SET_B_X_BI

SUMPEAK_CSV = Path(r"C:\MCXRAY\Sim\Aggregated\sumpeak_sensitivity.csv")


def build(sumpeak_csv: Path | str = SUMPEAK_CSV):
    data = pd.read_csv(sumpeak_csv)
    # Set B: thickness fixed, composition swept. The composition axis is the whole point, so the
    # thickness arms would only confuse it.
    data = data[(data["thickness_nm"] == SET_B_THICKNESS_NM)
                & (data["x_bi"].isin(SET_B_X_BI))].sort_values("x_bi")

    levels = sorted(data["level"].unique())
    fig, axes = new_figure(width=8.6, height=3.9, ncols=2)
    left, right = axes

    for index, level in enumerate(levels):
        arm = data[data["level"] == level]
        left.plot(arm["x_bi"], arm["fake_fraction_of_bi_m"] * 100,
                  label=f"level {level:.1%}", **series_style(index))
        right.plot(arm["x_bi"], arm["bi_l_m_corrupted"],
                   label=f"level {level:.1%}", **series_style(index))

    # 100% means the artefact is as large as the signal it sits on -- the point past which the
    # Bi M peak is more pile-up than bismuth.
    left.axhline(100, color=MUTED, linestyle="--", linewidth=1.0)
    # Placed right of where the 10% series crosses the line (~x = 0.045); at the left edge the
    # label runs under that curve.
    left.text(0.052, 118, "fake counts = true Bi M", fontsize=8, color=MUTED)

    left.set_xscale("log")
    left.set_yscale("log")
    left.set_xlabel("True Bi content $x$")
    left.set_ylabel("Fake counts as % of true Bi M")
    left.set_title("The same artefact, ~23x worse at $x$ = 0.01")
    left.legend(loc="upper right")
    trim_spines(left)

    # The clean curve is one line, not three -- it does not depend on the level. Drawn in grey so
    # it reads as the reference rather than as a fourth swept series.
    clean = data[data["level"] == levels[0]]
    right.plot(clean["x_bi"], clean["bi_l_m_clean"], color=MUTED, linestyle=":",
               linewidth=1.4, label="clean (simulated)", zorder=1)

    right.set_xscale("log")
    right.set_yscale("log")
    right.set_xlabel("True Bi content $x$")
    right.set_ylabel("Bi L/M intensity ratio")
    # Since m_band_factor moved to the measured 1.743 (2026-08-21) this axis spans well under one
    # decade, so every visible tick is a log MINOR tick and matplotlib renders them as
    # "2 x 10^-1" -- wide enough to overrun the y-label. Plain decimals are narrower and read
    # better over a sub-decade range. Applied to both locators because which one is populated
    # depends on where the data lands.
    right.yaxis.set_major_formatter(ScalarFormatter())
    right.yaxis.set_minor_formatter(ScalarFormatter())
    right.set_title("What a detector would actually record")
    # The curves all climb left-to-right, so the lower left is where the most damaged series
    # actually sits; the space below the convergence at high x is the only clear region.
    right.legend(loc="lower right")
    trim_spines(right)

    fig.suptitle("The Ga L + As L sum peak lands on Bi M$\\alpha$", fontsize=11, y=1.03)
    caption(
        fig,
        "GaAs(1-x)Bi(x), 100 nm, 200 keV, take-off 25 deg. Sum peak synthesised analytically "
        "onto the stored intensities -- MC X-Ray cannot produce pile-up. Settings: alpha parents "
        "only, level multiplying the geometric mean of the Ga L and As L intensities, photon "
        "conservation on, simulated Ma baseline. All four are swept elsewhere (see the switch "
        "sensitivity table); the level is bracketed at 0.1/1/10% rather than set to Walther's "
        "fitted ~15%, which is entangled with his own Bi M reference and is not portable.",
    )
    return fig


def make() -> list[Path]:
    return save(build(), "fig04_sumpeak_selectivity")


if __name__ == "__main__":
    for path in make():
        print(path)
