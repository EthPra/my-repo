"""Figure generation for the GaAsBi EDXS project. PRESENTATION LAYER ONLY.

Deliberately separate from `mcxray_wrapper`. CLAUDE.md mandates "pandas + stdlib only" for the
pipeline, and that holds: nothing in `mcxray_wrapper/` imports matplotlib, and nothing here is
imported by it. The dependency boundary runs exactly along this package's edge, so the
simulation and analysis code stays installable and testable with no plotting stack at all.

Every figure READS the stored tables in `Sim\\Aggregated\\` and renders them. No figure
recomputes a ratio, a k-factor or a residual -- if a number appears on a plot, some tested
module in `mcxray_wrapper` produced it. That keeps the figures re-derivable and stops a
presentation-layer computation quietly becoming a result nobody can trace.

Output: `C:\\MCXRAY\\Sim\\Figures\\`, a sibling of `Aggregated\\` and never inside `Results\\`.
PNG (200 dpi, for slides) and PDF (vector, for LaTeX) from a single call.

    python -m figures.make_all
"""
