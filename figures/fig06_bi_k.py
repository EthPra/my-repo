"""Figure 6 -- Bi K answers LO3, and the answer is a measured negative result.

LO3 asks how bismuth K, L and M absorption compares against gallium or arsenic references. Bi K
was carried through the whole pipeline for exactly this reason, despite being expected to fail --
omitting it would leave the objective silently unaddressed, whereas measuring its failure
answers it.

THE TWO PANELS SAY OPPOSITE THINGS, WHICH IS THE POINT.

  Left  -- escape fraction relative to the thin-foil limit. In a thin foil the number of photons
           generated is proportional to thickness, so I(t)/t would be constant if nothing were
           reabsorbed; dividing by its value at the thinnest foil isolates absorption from
           generation. Across three decades of thickness Bi Ma falls to 0.45 -- more than half
           of it reabsorbed at 1 um -- Bi La to 0.96, and Bi Ka1 not at all. On absorption
           alone, Bi K is the best line in the matrix.

           Bi Ka1 in fact drifts slightly ABOVE 1, reaching 1.03 at 1024 nm. That is not
           negative absorption: it is the thin-foil assumption behind the normalisation giving
           way, as beam broadening and the longer mean path at 25 deg take-off make generation
           marginally super-linear in thickness. For a 77 keV photon the attenuation it would
           otherwise show is small enough for that second-order effect to win, which is itself
           the cleanest statement of how absorption-immune the line is.

  Right -- absolute detected photons, the same runs. Bi Ka1 sits roughly two orders of magnitude
           below Bi La throughout. Fluorescence yield and the 200 keV beam's ionisation cross
           section for a 90.5 keV K edge are both against it, and the detector's efficiency at
           77 keV is 0.237 against ~1.0 for Bi La.

SO WHAT LIMITS THE ROUTE IS PHOTONS, NOT ABSORPTION. That distinction matters for the write-up:
an absorption problem might be fixed by a thinner specimen or a different take-off angle, and
this one cannot.

WHAT THAT COSTS, under the production threshold (Delta x = 0.01, VERDICT_BRIEF decision 1):
because Bi K is counting-dominated, its error in composition units GROWS with x. It clears the
bar at x = 0.01 -- even at the shortest acquisition swept, 100 s -- and then crosses it partway
up the range, failing in 18 of 27 scenarios where Bi L fails in none. So Bi K is rejected on
RANGE, and this figure supplies the mechanism behind that rather than a separate argument.

    Corrected 2026-08-24. This docstring previously said Bi K "needs more than ten times
    Walther's acquisition to reach 10% on x". That was computed against the 10%-relative
    accuracy bar retired on 2026-08-21 and does NOT transfer to an absolute threshold; against
    Delta x = 0.01 no dose multiplier is needed at x = 0.01 at all. Both PANELS are unaffected --
    escape fraction and detected-photon counts are threshold-independent, so the figure did not
    need re-rendering, only this framing. Do not reinstate a dose multiplier here.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from figures.style import caption, new_figure, save, series_style, trim_spines
from mcxray_wrapper.matrix import SET_A_THICKNESSES_NM, SET_A_X_BI
from mcxray_wrapper.ratios import INTENSITY_COLUMN
from mcxray_wrapper.spec import BI

COMBINED_CSV = Path(r"C:\MCXRAY\Sim\Aggregated\combined_intensities.csv")

# (label, line). One per Bi shell, each the shell's principal line.
LINES = (
    (r"Bi K$\alpha_1$  (77.1 keV)", "Ka1"),
    (r"Bi L$\alpha$  (10.84 keV)", "La"),
    (r"Bi M$\alpha$  (2.42 keV)", "Ma"),
)


def build(combined_csv: Path | str = COMBINED_CSV):
    combined = pd.read_csv(combined_csv)
    combined = combined[(combined["x_bi"] == SET_A_X_BI)
                        & (combined["thickness_nm"].isin(SET_A_THICKNESSES_NM))]
    combined = combined.assign(_line=combined["Line"].str.replace("Line ", "", regex=False))

    fig, axes = new_figure(width=8.6, height=3.9, ncols=2, sharex=True)
    left, right = axes

    # Collected as the curves are drawn and formatted into the caption below, so the stated
    # endpoints can never drift from the plotted ones -- the same discipline as fig02's
    # residuals.
    endpoints: dict[str, float] = {}
    ratio_to_bi_l: dict[str, float] = {}

    for index, (label, line) in enumerate(LINES):
        arm = combined[(combined["Atomic number"] == BI) & (combined["_line"] == line)]
        arm = arm.sort_values("thickness_nm")
        thickness = arm["thickness_nm"]
        intensity = arm[INTENSITY_COLUMN]

        # Photons generated go as t in a thin foil, so I/t is flat when nothing is reabsorbed.
        # Referencing to the thinnest foil makes the curve an escape fraction rather than an
        # absolute yield, which is what puts the three lines on one axis honestly.
        per_thickness = intensity / thickness
        escape = per_thickness / per_thickness.iloc[0]

        left.plot(thickness, escape, label=label, **series_style(index))
        right.plot(thickness, intensity, label=label, **series_style(index))

        endpoints[line] = float(escape.iloc[-1])
        ratio_to_bi_l[line] = float(intensity.mean())

    left.set_xscale("log")
    # Linear y here, unlike every other panel in the set: the range is 0.45 to 1.03, and a log
    # axis over less than one decade produces 9x10^-1 style tick labels that are harder to read
    # than the plain fractions they stand for.
    left.set_xlabel("Foil thickness (nm)")
    left.set_ylabel("Escape fraction, relative to thin-foil limit")
    left.set_title("Absorption: Bi K is the best line here")
    left.legend(loc="lower left")
    trim_spines(left)

    right.set_xscale("log")
    right.set_yscale("log")
    right.set_xlabel("Foil thickness (nm)")
    right.set_ylabel("Detected photons")
    right.set_title("Photons: and the worst by two orders")
    trim_spines(right)

    fig.suptitle(
        "Bi K is the best line on absorption and the worst on photons",
        fontsize=11, y=1.03,
    )
    caption(
        fig,
        f"GaAs(1-x)Bi(x), x = {SET_A_X_BI}, 200 keV, take-off 25 deg, free-standing foil, "
        f"10^6 trajectories (10^7 at 16 nm and below). Left: I(t)/t normalised to the 2 nm run, "
        f"so a flat curve means no reabsorption. At 1024 nm Bi Ma retains {endpoints['Ma']:.2f}, "
        f"Bi La {endpoints['La']:.2f}, and Bi Ka1 {endpoints['Ka1']:.2f} -- the last above unity "
        f"because the thin-foil proportionality behind the normalisation weakens as the beam "
        f"broadens, not because anything is gained. Right: the same runs, unnormalised; Bi Ka1 "
        f"averages {ratio_to_bi_l['La'] / ratio_to_bi_l['Ka1']:.0f}x below Bi La. What limits Bi K "
        f"is counting statistics and detector efficiency at 77 keV (0.237), not absorption, and "
        f"no specimen geometry fixes it -- which is why its error grows with x and it crosses the "
        f"Delta x = 0.01 bar partway up the range (18 of 27 scenarios) while Bi L crosses in none.",
    )
    return fig


def make() -> list[Path]:
    return save(build(), "fig06_bi_k_absorption_vs_photons")


if __name__ == "__main__":
    for path in make():
        print(path)
