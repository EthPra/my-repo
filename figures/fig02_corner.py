"""Figure 2 -- is rho.t a sufficient absorption coordinate? Two panels say no.

The project's own result (REPORT 23), and the one Walther was asked about. Absorption is
normally treated as a function of mass thickness rho.t: two specimens with the same rho.t are
assumed to absorb alike. If that held here, the two composition arms would fall on ONE curve in
each panel.

  Left  -- Ga K/L. The arms separate, and the gap widens with rho.t.
  Right -- As K/L. The arms very nearly coincide.

The finding is carried by the CONTRAST between the panels, not by either alone. Same physics,
same two specimens, same axis: one ratio is composition-sensitive beyond density and the other
is not. Ga La (1.098 keV) and As La (1.282 keV) sit differently against the absorption
structure of Bi, whose weight fraction falls from ~24% to ~1.4% between the arms -- but the
mechanism is NOT asserted here or on the figure, because that needs cited mass attenuation
coefficients this project does not hold.

Why it matters: a K/L ratio is used as a THICKNESS PROXY (Walther Figs 3-5). A proxy that also
tracks composition re-introduces the dependence it was meant to remove. Hence As K/L, not
Ga K/L, for the round-trip re-indexing.

Residual annotations come from `mcxray_wrapper.corner`, never hard-coded -- if the data changes,
the figure changes with it.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from figures.style import caption, new_figure, save, series_style, trim_spines
from mcxray_wrapper.corner import (
    REFERENCE_X_BI,
    RHO_T_COLUMN,
    TEST_X_BI,
    compare_arms,
    rho_t_table,
)

RATIOS_CSV = Path(r"C:\MCXRAY\Sim\Aggregated\diagnostic_ratios.csv")

# (panel title, ratio column). Left panel is the one that fails -- read first.
PANELS = (
    ("Ga K/L", "Ga_K_L_principal"),
    ("As K/L", "As_K_L_principal"),
)


def build(ratios_csv: Path | str = RATIOS_CSV):
    ratios = pd.read_csv(ratios_csv)
    table = rho_t_table(ratios)
    residuals = compare_arms(ratios).set_index(["ratio", "thickness_nm"])["residual_pct"]

    arms = (
        (f"x = {REFERENCE_X_BI:.2f}", REFERENCE_X_BI),
        (f"x = {TEST_X_BI:.2f}", TEST_X_BI),
    )

    # sharey is load-bearing, not cosmetic: the claim is that the LEFT panel's curves separate
    # and the RIGHT panel's do not. Independent y-scales would stretch each panel to fill its
    # own range and make the two gaps look comparable when they are not.
    fig, axes = new_figure(width=8.0, height=3.8, ncols=2, sharey=True)

    for ax, (panel_title, column) in zip(axes, PANELS):
        for index, (label, x_bi) in enumerate(arms):
            arm = table[table["x_bi"] == x_bi].sort_values(RHO_T_COLUMN)
            ax.plot(arm[RHO_T_COLUMN], arm[column], label=label, **series_style(index))

        ax.set_xscale("log")   # rho.t spans 11 to 5829; linear would bunch every thin foil
        ax.set_xlabel(r"Mass thickness $\rho t$  (g cm$^{-3}$ $\cdot$ nm)")
        trim_spines(ax)

        # The residual goes in the TITLE, not an annotation inside the axes: the curves rise
        # into the upper right and the legend holds the upper left, so any in-axes placement
        # collides with something at some data range.
        worst = residuals.loc[(column, 1024)]
        ax.set_title(f"{panel_title}   ({worst:+.1f}% at 1024 nm)")

    axes[0].set_ylabel("Line-intensity ratio (principal lines)")
    axes[0].legend(loc="upper left")

    fig.suptitle(
        r"If $\rho t$ determined absorption, each panel would show one curve",
        fontsize=11, y=1.02,
    )
    caption(
        fig,
        "GaAs(1-x)Bi(x), 200 keV, take-off 25 deg, free-standing foil. Both arms sweep "
        "thickness; only the Bi content differs. Ga K/L carries a large composition dependence "
        "beyond density, As K/L does not -- so As K/L is the sounder thickness proxy. "
        "Percentages are the deviation of the x = 0.01 arm from the x = 0.20 arm interpolated "
        "at matched rho.t.",
    )
    return fig


def make() -> list[Path]:
    return save(build(), "fig02_rho_t_insufficiency")


if __name__ == "__main__":
    for path in make():
        print(path)
