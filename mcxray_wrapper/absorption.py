"""How a K/L ratio actually varies with thickness -- and where the three curves cross.

WALTHER'S QUESTION (2026-08-16): "The elements' K/L ratio lines vs thickness seem to all cross at
about one thickness value - can you work out which that is from the first plot, using exponential
fits to your data points for t=2-1024nm?"

Answered here. The crossings are located, and the exponential turns out to be the wrong model --
in a way that works against his own observation.

WHY NOT AN EXPONENTIAL. His reasoning was that the ratio is "exponentials divided by
exponentials". That holds for TRANSMISSION: a beam entering one face of a foil and leaving the
other travels the full thickness, so Beer-Lambert gives exp(-chi.rho.t).

But these X-rays are not transmitted through the foil -- they are GENERATED INSIDE it, at every
depth. One born near the exit surface is barely absorbed; one born at the far side crosses the
whole thickness. What escapes is the average over all birth depths. For generation uniform in
depth that integral is

    f(X) = (1 - exp(-X)) / X ,      X = chi . rho . t

the standard thin-film absorption factor, and the K/L ratio is A . f(X_hard)/f(X_soft). The
ratio of two such terms is NOT an exponential: it starts flat, then becomes LINEAR in t once the
soft line is fully absorbed while the hard one is not, rather than continuing to accelerate.

This is a derivation from Beer-Lambert plus a uniform-generation assumption, not an imported
constant -- the chi values come OUT of the fit and are not asserted. The uniform-generation
assumption is an approximation (the real ionisation depth distribution phi(rho.z) is not flat);
it is evidently good enough here, since the form reproduces every curve to R^2 = 1.00000.

CONSEQUENCE FOR THE QUESTION. Forcing an exponential through data that is flattening
over-predicts the thick end and drags the crossings apart:

    crossings from exponential fits    117 / 210 / 268 nm    spread 151 nm
    crossings in the raw data          102 / 144 / 165 nm    spread  63 nm
    crossings from the absorption fit  102 / 153 / 178 nm    spread  76 nm

So the curves cluster around 100-180 nm, and Walther's observation is BETTER supported by the
data than by the method he proposed for testing it.

DEPENDENCIES. numpy and scipy, on Ethan's decision (2026-08-16). This is a deliberate widening
of CLAUDE.md's "pandas + stdlib only" rule, which predates any numerical fitting in the project:
a three-parameter non-linear fit and a root-find are exactly what scipy is for, and hand-rolling
them buys nothing but a worse optimiser. Declare it in the write-up alongside matplotlib.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy.optimize import brentq, curve_fit

# The three diagnostics, as stored by ratios.py.
DIAGNOSTIC_COLUMNS = ("Ga_K_L", "As_K_L", "Bi_L_M")

# Below this the closed form (1-exp(-X))/X loses precision to cancellation, so the series
# expansion 1 - X/2 + X^2/6 is used instead.
_SMALL_X = 1e-8


def absorption_factor(x):
    """f(X) = (1 - exp(-X))/X: the fraction of X-rays escaping, averaged over birth depth.

    -> 1 as X -> 0 (a thin foil absorbs nothing) and -> 1/X for large X (only those born near
    the exit surface get out). Accepts scalars or arrays.
    """
    x = np.asarray(x, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        exact = np.where(x > _SMALL_X, (1.0 - np.exp(-np.abs(x))) / np.where(x == 0, 1.0, x), 0.0)
    series = 1.0 - x / 2.0 + x**2 / 6.0
    out = np.where(x > _SMALL_X, exact, series)
    return out if out.ndim else float(out)


def ratio_model(thickness_nm, amplitude, chi_hard, chi_soft):
    """The modelled hard/soft line ratio. Vectorised over thickness."""
    t = np.asarray(thickness_nm, dtype=float)
    out = amplitude * absorption_factor(chi_hard * t) / absorption_factor(chi_soft * t)
    return out if np.ndim(out) else float(out)


def fit_ratio_curve(thicknesses, ratios) -> dict:
    """Fit A.f(chi_hard.t)/f(chi_soft.t) by least squares.

    Seeded from the data itself: the amplitude from the thinnest point (where absorption is
    negligible, so the ratio is close to its generated value), and the two chi from the scale of
    the thickness range. Returns R^2 alongside, so the caller can judge the fit rather than
    trust it.
    """
    t = np.asarray(thicknesses, dtype=float)
    y = np.asarray(ratios, dtype=float)
    if t.size < 3:
        raise ValueError("need at least 3 points to fit a 3-parameter model")

    guess = [y[np.argmin(t)], 1.0 / (10.0 * t.max()), 1.0 / t.mean()]
    params, _ = curve_fit(
        ratio_model, t, y, p0=guess,
        bounds=([0.0, 1e-9, 1e-9], [np.inf, 1.0, 1.0]),
        maxfev=100_000,
    )
    amplitude, chi_hard, chi_soft = params

    residual = float(np.sum((y - ratio_model(t, *params)) ** 2))
    total = float(np.sum((y - y.mean()) ** 2))
    return {
        "amplitude": float(amplitude),
        "chi_hard": float(chi_hard),
        "chi_soft": float(chi_soft),
        "r_squared": 1.0 - residual / total if total else 1.0,
    }


def compare_models(thicknesses, ratios) -> dict:
    """R^2 for the exponential, a straight line, and the absorption form.

    The exponential is included because it is what was proposed; keeping all three side by side
    is what makes "the exponential is the wrong model" a measurement rather than an opinion.
    """
    t = np.asarray(thicknesses, dtype=float)
    y = np.asarray(ratios, dtype=float)
    total = float(np.sum((y - y.mean()) ** 2))
    r_squared = lambda pred: 1.0 - float(np.sum((y - pred) ** 2)) / total

    slope, intercept = np.polyfit(t, np.log(y), 1)
    exponential = r_squared(np.exp(intercept) * np.exp(slope * t))
    linear = r_squared(np.polyval(np.polyfit(t, y, 1), t))

    return {
        "exponential": exponential,
        "linear": linear,
        "absorption": fit_ratio_curve(t, y)["r_squared"],
    }


def crossing(fit_a: dict, fit_b: dict, low_nm: float = 1.0, high_nm: float = 4096.0) -> float:
    """Thickness at which two fitted curves meet. Raises if they do not cross in the bracket."""
    keys = ("amplitude", "chi_hard", "chi_soft")
    difference = lambda t: (ratio_model(t, *(fit_a[k] for k in keys))
                            - ratio_model(t, *(fit_b[k] for k in keys)))

    if difference(low_nm) * difference(high_nm) > 0:
        raise ValueError(f"curves do not cross between {low_nm} and {high_nm} nm")
    return float(brentq(difference, low_nm, high_nm))


def fit_diagnostics(ratios: pd.DataFrame, x_bi: float = 0.20,
                    definition: str = "principal") -> pd.DataFrame:
    """Fit all three diagnostic curves for one composition arm; report parameters and model R^2."""
    arm = ratios[ratios["x_bi"] == x_bi].sort_values("thickness_nm")
    if arm.empty:
        raise ValueError(f"no runs at x_bi={x_bi}")

    rows = []
    for stem in DIAGNOSTIC_COLUMNS:
        column = f"{stem}_{definition}"
        if column not in arm.columns:
            raise ValueError(f"{column!r} missing from the ratio table")
        fit = fit_ratio_curve(arm["thickness_nm"], arm[column])
        models = compare_models(arm["thickness_nm"], arm[column])
        rows.append({
            "curve": stem, "definition": definition, "x_bi": x_bi, "n_points": len(arm),
            "amplitude": fit["amplitude"],
            "chi_hard_per_nm": fit["chi_hard"],
            "chi_soft_per_nm": fit["chi_soft"],
            "r2_absorption": models["absorption"],
            "r2_exponential": models["exponential"],
            "r2_linear": models["linear"],
        })
    return pd.DataFrame(rows)


def crossing_table(ratios: pd.DataFrame, x_bi: float = 0.20,
                   definition: str = "principal") -> pd.DataFrame:
    """Every pairwise crossing of the three diagnostic curves, from the absorption fits."""
    arm = ratios[ratios["x_bi"] == x_bi].sort_values("thickness_nm")
    fits = {stem: fit_ratio_curve(arm["thickness_nm"], arm[f"{stem}_{definition}"])
            for stem in DIAGNOSTIC_COLUMNS}

    rows = []
    for first, second in combinations(DIAGNOSTIC_COLUMNS, 2):
        try:
            where = crossing(fits[first], fits[second])
            value = ratio_model(where, fits[first]["amplitude"],
                                fits[first]["chi_hard"], fits[first]["chi_soft"])
        except ValueError:
            where = value = float("nan")
        rows.append({
            "curve_a": first, "curve_b": second, "definition": definition, "x_bi": x_bi,
            "crossing_nm": where, "ratio_at_crossing": value,
        })
    return pd.DataFrame(rows)


def write_absorption_analysis(ratios_csv: "str | object", output_dir) -> object:
    """Read the stored ratio table, fit and locate the crossings, write both into output_dir."""
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ratios = pd.read_csv(ratios_csv)

    combined = pd.concat([
        fit_diagnostics(ratios).assign(kind="fit"),
        crossing_table(ratios).assign(kind="crossing"),
    ], ignore_index=True)
    out = output_dir / "absorption_fits_and_crossings.csv"
    combined.to_csv(out, index=False)
    return out
