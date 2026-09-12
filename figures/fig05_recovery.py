"""Figure 5 -- recovered composition, simulated against as-measured. The round trip under fire.

WHAT A ROUND TRIP IS. Calibrate k* on Set A, where the composition is known and the thickness is
swept. Then take a Set B run, pretend both its composition AND its thickness are unknown, read
its own As K/L ratio to place it on the calibration, and invert to a composition. The true value
is attached afterwards, only for grading. If the pipeline is sound, recovered lands on true.

WHAT THIS FIGURE ADDS. Every recovery so far has run on pristine simulated intensities, which no
detector produces. Here the unknown runs -- and only the unknown runs, as Walther's own practice
requires -- carry the synthesised sum peak first. The calibration stays simulated and clean.

  Left  -- a Bi M route. The sum peak lands directly on its numerator, so recovered x runs high,
           and worst where the artefact is relatively largest. At x = 0.01 and a 1% level the
           recovered value roughly doubles.
  Right -- a Bi L route, identical treatment. Bi La is at 10.84 keV and the artefact at 2.42, so
           there is no path from one to the other; the points stay on the diagonal.

The contrast IS the result: it is what makes "use a Bi L pair" a finding rather than a
preference. Both panels share axes so the eye compares them directly.

A NOTE ON WHY THE CALIBRATION IS LEFT CLEAN. Corrupting both sides makes the error largely
self-cancel -- measured on this data it removed the effect at x = 0.20 entirely (REPORT 26.6).
That variant would understate the damage, and Walther's answer rules it out.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from figures.style import MUTED, caption, new_figure, save, series_style, trim_spines

SWEEP_CSV = Path(r"C:\MCXRAY\Sim\Aggregated\sumpeak_roundtrip_sweep.csv")

# The switch setting the solid series are drawn at. Every combination is run and stored; one has
# to be drawn, so it is named here and on the figure rather than left implicit.
SWITCHES = {"parents": "alpha_only", "basis": "intensity",
            "conserve": True, "m_band_factor": 1.0}

PANELS = (
    ("Bi M$\\alpha$ / As K$\\alpha$", "Bi_As", "M", "K"),
    ("Bi L$\\alpha$ / As K$\\alpha$", "Bi_As", "L", "K"),
)
DEFINITION = "principal"


def build(sweep_csv: Path | str = SWEEP_CSV):
    sweep = pd.read_csv(sweep_csv)
    sweep = sweep[sweep["definition"] == DEFINITION]

    corrupted = sweep[sweep["level"] > 0]
    for column, value in SWITCHES.items():
        corrupted = corrupted[corrupted[column] == value]
    clean = sweep[sweep["level"] == 0]

    levels = sorted(corrupted["level"].unique())

    fig, axes = new_figure(width=8.6, height=4.0, ncols=2, sharex=True, sharey=True)

    for ax, (title, route, heavy, light) in zip(axes, PANELS):
        def rows(frame):
            return frame[(frame["route"] == route) & (frame["heavy_shell"] == heavy)
                         & (frame["light_shell"] == light)].sort_values("true_x_bi")

        reference = rows(clean)
        # Perfect recovery, for the eye to measure departure against.
        ax.plot(reference["true_x_bi"], reference["true_x_bi"], color=MUTED, linestyle="--",
                linewidth=1.0, zorder=1, label="true = recovered")
        ax.plot(reference["true_x_bi"], reference["recovered_x"], color=MUTED, linestyle=":",
                linewidth=1.4, marker="x", markersize=4, zorder=2, label="clean (simulated)")

        for index, level in enumerate(levels):
            arm = rows(corrupted[corrupted["level"] == level])
            ax.plot(arm["true_x_bi"], arm["recovered_x"],
                    label=f"as-measured, {level:.1%}", **series_style(index))

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("True Bi content $x$")
        ax.set_title(title)
        trim_spines(ax)

    axes[0].set_ylabel("Recovered Bi content $x$")
    # Curves run lower-left to upper-right in both panels, so the lower right is the only corner
    # a legend does not sit on top of data.
    axes[0].legend(loc="lower right")

    # In the right panel every series lands on the diagonal and the last drawn hides the rest.
    # Without saying so, a reader sees one line and cannot tell the others were plotted at all.
    axes[1].text(0.5, 0.06, "all levels coincide", transform=axes[1].transAxes,
                 fontsize=9, color=MUTED, ha="center")

    fig.suptitle(
        "The sum peak destroys a Bi M recovery and cannot touch a Bi L one",
        fontsize=11, y=1.03,
    )
    caption(
        fig,
        "GaAs(1-x)Bi(x), 100 nm, 200 keV, take-off 25 deg, principal lines. k* calibrated on "
        "Set A (x = 0.20, 2-1024 nm) and the unknown placed on that calibration by its own "
        "As K/L ratio, so the recovery is held out in composition AND thickness -- no true value "
        "is used to produce a recovered one. The sum peak is applied to the unknown runs only, "
        "never to the calibration. Switches: alpha parents, intensity basis, photon conservation "
        "on, simulated Ma baseline; all sixteen combinations are stored alongside.",
    )
    return fig


def make() -> list[Path]:
    return save(build(), "fig05_recovery_as_measured")


if __name__ == "__main__":
    for path in make():
        print(path)
