"""Figure 1 -- the three diagnostic ratios against foil thickness.

The replication of Walther (2025) Fig. 1: "Plot of Ga K/L, As K/L, Bi L/M ratios from Monte
Carlo simulations as function of GaAsBi thickness (acceleration voltage: 200 kV, take-off angle:
25 deg, density 5.36 g cm-3 for x = 0.2)."

These three ratios have been reproduced in DATA since July -- all monotonic in thickness, the
shape his figure shows -- but never plotted. This is the one replication the project could not
show.

TWO DELIBERATE DEPARTURES from his presentation, both stated on the figure itself rather than
left for a reader to notice:

  Log thickness axis. The runs are a geometric doubling series, 2 -> 1024 nm. On the linear
  axis his figures use, every point below ~100 nm collapses into the origin and the thin-foil
  behaviour -- where the ratios are flattest and most useful -- becomes invisible.

  Density 5.692 g/cm3 at x = 0.2, not his 5.36. This follows the revised model Walther himself
  supplied on 2026-07-19 (rho = 5.32 + 1.86x), which supersedes his published value. REPORT 10,
  15.

Eleven points, not ten: the Set B run at 100 nm shares Set A's conditions exactly (x = 0.20,
same density model, same detector), so the thickness curve gains a free extra point.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from figures.style import caption, new_figure, save, series_style, trim_spines

RATIOS_CSV = Path(r"C:\MCXRAY\Sim\Aggregated\diagnostic_ratios.csv")

SET_A_X_BI = 0.20

# label, column stem. Order fixes the colour assignment, so it must not be reordered casually.
SERIES = (
    ("Ga K/L", "Ga_K_L"),
    ("As K/L", "As_K_L"),
    ("Bi L/M", "Bi_L_M"),
)


def build(ratios_csv: Path | str = RATIOS_CSV, definition: str = "principal"):
    """Render Figure 1. `definition` is 'principal' or 'summed'.

    The two line definitions differ by 40-90% and the choice for the final inversion is still
    formally open (deferred 2026-07-25), so the figure states which one it is drawing rather
    than silently picking one.
    """
    if definition not in ("principal", "summed"):
        raise ValueError(f"definition must be 'principal' or 'summed', got {definition!r}")

    ratios = pd.read_csv(ratios_csv)
    arm = ratios[ratios["x_bi"] == SET_A_X_BI].sort_values("thickness_nm")
    if arm.empty:
        raise ValueError(f"no runs at x_bi={SET_A_X_BI} in {ratios_csv}")

    fig, ax = new_figure()

    for index, (label, stem) in enumerate(SERIES):
        column = f"{stem}_{definition}"
        if column not in arm.columns:
            raise ValueError(f"{column!r} missing from the ratio table")
        ax.plot(arm["thickness_nm"], arm[column], label=label, **series_style(index))

    ax.set_xscale("log")
    ax.set_xlabel("Foil thickness (nm)")
    ax.set_ylabel(f"Line-intensity ratio ({definition} lines)")
    ax.set_title("Diagnostic X-ray line ratios vs foil thickness")

    # Tick the LO4 doubling series only. Every simulated thickness is plotted, but 100 nm (the
    # shared Set B point) sits too close to 128 nm in log space to label both legibly, and tick
    # labels are for orientation rather than an inventory of the data.
    ticks = [t for t in arm["thickness_nm"] if t != 100]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{int(t)}" for t in ticks])
    ax.minorticks_off()

    ax.legend(loc="upper left")
    trim_spines(ax)

    density = arm["mass_density_g_cm3"].iloc[0]
    n_points = len(arm)
    caption(
        fig,
        f"GaAs(1-x)Bi(x), x = {SET_A_X_BI:.2f}, rho = {density:.3f} g/cm3. "
        f"200 keV, take-off 25 deg, free-standing foil, Si:Li 0.5 cm. "
        f"{n_points} simulated thicknesses; log axis. "
        f"Replicates Walther (2025) Fig. 1.",
    )
    return fig


def make(definition: str = "principal") -> list[Path]:
    suffix = "" if definition == "principal" else f"_{definition}"
    return save(build(definition=definition), f"fig01_ratios_vs_thickness{suffix}")


if __name__ == "__main__":
    for path in make():
        print(path)
