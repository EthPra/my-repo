"""Figure 3 -- the measurability limit. LO4's headline.

THE QUESTION THE WHOLE PROJECT IS FOR: down to what Bi content can x be quantified, and which
Bi line should be used to do it? Three mechanisms limit the answer and they do not limit the
same routes, so neither panel alone settles it.

  Left  -- total ABSOLUTE error on recovered x against composition, for the three Bi shells,
           all measured against arsenic so that only the Bi line differs. A horizontal line
           marks Walther's own bar, Delta x = 0.01 (J. Microsc. 2025, p.2), adopted as the
           production threshold 2026-08-21 in place of the unanchored 10% relative one
           (VERDICT_BRIEF.md decision 1).

           The distinction that matters is not which line is best at the nominal setting but
           which survives the assumptions being wrong -- so the counts in the title and caption
           are computed from the data, not asserted. The threshold change moves them: a
           relative bar scales its absolute demand with x and so penalises a line purely for
           being measured at low x, which is exactly the regime Set C exists to probe.

           NOTE the panel scores accuracy alone. A line can clear Delta x = 0.01 and still be
           impractical because of the acquisition time it needs to get there; that cost is
           fig06's subject. Reading a recommendation off this panel by itself would miss it.

  Right -- the same recommended Bi L route, taken apart into the mechanisms that make it up.
           The point is that its budget is NOT dominated by the artefact the project set out to
           study: counting statistics and overlap (i) are comparable, and the sum peak
           contributes essentially nothing because it lands 8.4 keV away from Bi La.

THE SHADED BAND on the left panel is the spread across all 27 swept scenarios -- every
combination of sum-peak level, overlap coupling and dose. None of those three magnitudes is
known, so a single line would be a claim the data cannot support. The band is the claim: a line
that stays below target across the whole grid does so robustly, not merely at a convenient
corner -- and one that crosses it somewhere is only as good as the assumption that rescues it.

Everything is read from `Aggregated\\error_budget.csv`. Nothing here recomputes physics and no
number is typed in.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from figures.style import MUTED, caption, new_figure, save, series_style, trim_spines
from mcxray_wrapper.budget import DEFAULT_TARGET_ABSOLUTE
from mcxray_wrapper.counting import WALTHER_DOSE_SCALE

BUDGET_CSV = Path(r"C:\MCXRAY\Sim\Aggregated\error_budget.csv")

# All three against arsenic, so the ONLY difference between the series is which Bi shell is used.
# Comparing a Bi M route against Ga with a Bi L route against As would confound two changes.
ROUTE = "Bi_As"
LIGHT_SHELL = "K"
DEFINITION = "principal"

SHELLS = (
    ("Bi L", "L"),
    ("Bi M", "M"),
    ("Bi K", "K"),
)

# The nominal scenario the solid lines are drawn at: the middle of each swept ladder, on
# Walther's own acquisition. Stated on the figure, because it is a choice and not a measurement.
NOMINAL = {"level": 0.01, "coupling": 0.01, "dose_scale": WALTHER_DOSE_SCALE}

# Mechanisms in the right-hand panel. bias_method is carried in the total but not drawn: for this
# route it is ~1e-7 in x (k* for Bi L / As K is invariant to the fifth decimal), which on a log
# axis would be four decades of empty space below everything else.
MECHANISMS = (
    ("Counting statistics", "sigma_counting"),
    ("Overlap (i): As K$\\alpha$ / Bi L$\\alpha$", "sigma_overlap"),
    ("Sum peak on Bi M$\\alpha$", "bias_sumpeak"),
)


def _nominal(budget: pd.DataFrame) -> pd.DataFrame:
    mask = pd.Series(True, index=budget.index)
    for column, value in NOMINAL.items():
        mask &= budget[column] == value
    return budget[mask]


def _misses_at_lowest_x(budget: pd.DataFrame) -> "dict[str, tuple[int, int]]":
    """Per shell, how many swept scenarios exceed the target at the lowest simulated x.

    Derived, never typed: the counts appear in the panel title and the caption, and the whole
    point of the threshold change is that they move. A hand-written "9 of 27" survived the
    2026-08-21 threshold decision as a false statement precisely because it was prose.
    """
    lowest = budget[budget["true_x_bi"] == budget["true_x_bi"].min()]
    counts = {}
    for _, shell in SHELLS:
        rows = lowest[lowest["heavy_shell"] == shell]
        counts[shell] = (int((rows["total_error"] > DEFAULT_TARGET_ABSOLUTE).sum()), len(rows))
    return counts


def _left_title(misses: "dict[str, tuple[int, int]]") -> str:
    """State which shells miss, from the counts -- never an assertion typed ahead of the data.

    Deliberately descriptive of THIS panel only. A shell clearing the accuracy target here is not
    a recommendation: the dose it needs to do so is fig06's subject, not this one's.
    """
    failing = [label for label, shell in SHELLS if misses[shell][0] > 0]
    clearing = [label for label, shell in SHELLS if misses[shell][0] == 0]
    if len(failing) == 1:
        return f"Only {failing[0]} misses the target at the lowest $x$"
    if not failing:
        return "Every Bi line clears the target at the lowest $x$"
    return f"{' and '.join(failing)} miss the target at the lowest $x$" + (
        f"; {' and '.join(clearing)} clear it" if clearing else "")


def build(budget_csv: Path | str = BUDGET_CSV):
    budget = pd.read_csv(budget_csv)
    budget = budget[(budget["route"] == ROUTE) & (budget["definition"] == DEFINITION)
                    & (budget["light_shell"] == LIGHT_SHELL)]
    nominal = _nominal(budget)
    misses = _misses_at_lowest_x(budget)
    lowest_x = budget["true_x_bi"].min()

    fig, axes = new_figure(width=8.6, height=3.9, ncols=2)
    left, right = axes

    # ---- left: total error per Bi shell, with the scenario band ----
    for index, (label, shell) in enumerate(SHELLS):
        line = nominal[nominal["heavy_shell"] == shell].sort_values("true_x_bi")
        left.plot(line["true_x_bi"], line["total_error"],
                  label=label, **series_style(index))

        # Envelope over every scenario, not a confidence interval -- it is the range of ANSWERS
        # the unsettled assumptions permit.
        spread = budget[budget["heavy_shell"] == shell].groupby("true_x_bi")["total_error"]
        band = spread.agg(["min", "max"]).sort_index()
        left.fill_between(band.index, band["min"], band["max"],
                          color=series_style(index)["color"], alpha=0.12, linewidth=0)

    left.axhline(DEFAULT_TARGET_ABSOLUTE, color=MUTED, linestyle="--", linewidth=1.0)
    left.text(0.011, DEFAULT_TARGET_ABSOLUTE * 1.15,
              f"$\\Delta x$ = {DEFAULT_TARGET_ABSOLUTE} target", fontsize=8, color=MUTED)

    left.set_xscale("log")
    left.set_yscale("log")
    left.set_xlabel("True Bi content $x$")
    left.set_ylabel("Total error on recovered $x$  (absolute)")
    left.set_title(_left_title(misses))
    # Absolute error RISES with x (relative error fell), so the series now run bottom-left to
    # top-right and upper right is occupied. Upper left is the empty corner on this metric.
    left.legend(loc="upper left")
    trim_spines(left)

    # ---- right: what makes up the recommended route's budget ----
    recommended = nominal[nominal["heavy_shell"] == "L"].sort_values("true_x_bi")
    for index, (label, column) in enumerate(MECHANISMS):
        # A mechanism that is identically zero cannot be drawn on a log axis. Saying so in the
        # legend is more informative than an absent series the reader has to notice is missing.
        if (recommended[column] <= 0).all():
            left_out = f"{label} (zero)"
            right.plot([], [], label=left_out, **series_style(index))
            continue
        right.plot(recommended["true_x_bi"], recommended[column],
                   label=label, **series_style(index))

    right.plot(recommended["true_x_bi"], recommended["total_error"],
               color=MUTED, linewidth=1.0, linestyle=":", label="Total", zorder=1)

    right.set_xscale("log")
    right.set_yscale("log")
    right.set_xlabel("True Bi content $x$")
    right.set_ylabel(r"Contribution to $\sigma_x$  (absolute)")
    right.set_title("Bi L$\\alpha$ / As K$\\alpha$: what limits it")
    # The three series occupy the top and the bottom of the panel and leave a wide empty band
    # across the middle; upper left collides with the counting series at every composition.
    right.legend(loc="center left")
    trim_spines(right)

    fig.suptitle("Which bismuth line can measure how little bismuth", fontsize=11, y=1.03)
    caption(
        fig,
        f"GaAs(1-x)Bi(x), 100 nm, 200 keV, take-off 25 deg. All routes referenced to As K, "
        f"{DEFINITION} line definition. Solid lines: sum-peak level 1%, overlap coupling 1%, "
        f"Walther's 715.5 s acquisition. Shaded band: full range over all 27 combinations of "
        f"level, coupling and dose (0.1/1/10% and 100 s / 715.5 s / 2 h). Total = |bias| + "
        f"quadrature sum of the variances, a conservative envelope. Target is Walther's own bar, "
        f"Delta x = {DEFAULT_TARGET_ABSOLUTE} (J. Microsc. 2025, p.2), not a relative percentage. "
        f"At x = {lowest_x:g} the scenarios exceeding it are: "
        + ", ".join(f"{label} {misses[shell][0]} of {misses[shell][1]}" for label, shell in SHELLS)
        + f". This panel scores ACCURACY only -- the acquisition time a line needs to reach it is "
        f"fig06's subject, not this one's. The sum peak "
        f"lands at 2.42 keV and Bi La at 10.84 keV, so it cannot reach the Bi L route directly; "
        f"the residual shown is the indirect path through parent-line depletion.",
    )
    return fig


def make() -> list[Path]:
    return save(build(), "fig03_measurability_limit")


if __name__ == "__main__":
    for path in make():
        print(path)
