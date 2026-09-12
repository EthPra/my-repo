"""Shared visual language, so every figure reads as one set.

Design decisions worth knowing before changing anything here:

  Palette. Three hues, in this order: blue #2a78d6, orange #eb6834, aqua #1baf7a. Not chosen by
  eye -- this exact triple was checked with a colour-vision validator and clears the all-pairs
  separation gates (worst simulated-deuteranopia dE 9.2, worst normal-vision dE 24.0). A fourth
  hue does not clear them, which is why no figure here carries more than three colour-coded
  series; a fourth dimension goes to line style or a second panel instead.

  Double encoding. Colour AND marker shape on every series. A dissertation gets printed,
  photocopied and read by colour-blind examiners; a figure that survives only in colour is a
  figure that fails silently. Aqua also sits below 3:1 contrast on white, so it must never be
  the only thing distinguishing a series.

  Fonts. matplotlib's bundled DejaVu Sans, deliberately. Naming a font that is not installed
  makes matplotlib substitute one without erroring -- the figure still renders, just not as
  designed, and nothing tells you.

  Output. PNG at 200 dpi for slides, PDF vector for LaTeX, written together so the two can
  never drift apart.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

# No display on this machine, and figures are written to file rather than shown. Must be set
# before pyplot is imported.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  (import order is required by matplotlib.use)

FIGURES_DIR = Path(r"C:\MCXRAY\Sim\Figures")

# Validated categorical triple -- see the module docstring. Order is part of the validation.
SERIES_COLOURS = ("#2a78d6", "#eb6834", "#1baf7a")
SERIES_MARKERS = ("o", "s", "^")

# Chart chrome. Grey with a slight cool bias, to sit with the blue-led palette.
INK = "#141a19"
INK_SECONDARY = "#4e5654"
MUTED = "#838b89"
GRID = "#e4e8e6"
AXIS = "#c3cac7"

# A thesis text block is ~6.3in wide; this leaves a margin and scales cleanly onto a 16:9 slide.
FIG_WIDTH_IN = 6.5
FIG_HEIGHT_IN = 4.0

PNG_DPI = 200


def apply_style() -> None:
    """Set the rcParams every figure in this package shares. Call once, before plotting."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "axes.labelcolor": INK,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.8,
        "axes.facecolor": "white",
        "axes.grid": True,
        "axes.axisbelow": True,          # grid behind the data, never over it
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "text.color": INK,
        "xtick.color": INK_SECONDARY,
        "ytick.color": INK_SECONDARY,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "lines.linewidth": 1.8,
        "lines.markersize": 5,
        "lines.markeredgewidth": 1.0,
        "figure.facecolor": "white",
        "figure.dpi": 110,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
    })


def new_figure(width: float = FIG_WIDTH_IN, height: float = FIG_HEIGHT_IN, **kwargs):
    """A styled figure + axes. kwargs pass through to plt.subplots (nrows, ncols, sharey...)."""
    apply_style()
    return plt.subplots(figsize=(width, height), **kwargs)


def series_style(index: int) -> dict:
    """Colour + marker for series `index`, wrapping if a figure somehow exceeds three.

    Wrapping repeats a colour, which is a real ambiguity -- but the marker still differs, so the
    series stay distinguishable. Prefer a second panel to a fourth series.
    """
    return {
        "color": SERIES_COLOURS[index % len(SERIES_COLOURS)],
        "marker": SERIES_MARKERS[index % len(SERIES_MARKERS)],
        "markerfacecolor": "white",
        "markeredgecolor": SERIES_COLOURS[index % len(SERIES_COLOURS)],
    }


def trim_spines(ax) -> None:
    """Drop the top and right spines -- less ink around the data."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def caption(fig, text: str) -> None:
    """A small conditions note under the axes, so a figure lifted into slides stays self-describing."""
    fig.text(0.0, -0.04, text, fontsize=8, color=MUTED, ha="left", va="top", wrap=True)


def save(fig, name: str, directory: Path | str = FIGURES_DIR) -> list[Path]:
    """Write `<name>.png` and `<name>.pdf`. Returns both paths."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    written = []
    for suffix, kwargs in ((".png", {"dpi": PNG_DPI}), (".pdf", {})):
        path = directory / f"{name}{suffix}"
        fig.savefig(path, **kwargs)
        written.append(path)
    plt.close(fig)
    return written
