#!/usr/bin/env python3
"""Generates the PDF figures of tok_1.tex (Smoothop palette).

Usage: ./.venv/bin/python publications/tok_1/figures/gen_figures.py
       (matplotlib required; text is rendered by the system LaTeX).

Each figure is written next to this script, independently of the current
working directory. This file is the *recipe* for every regenerable figure of
the tôk 1 publication; hand-made assets (logos, screenshots) live beside it but
are not produced here.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

OUT = os.path.dirname(os.path.abspath(__file__))

# Smoothop palette (docs/Style.md). Hue fixed within 1°; the shade suffix picks
# the column. Validated for CVD/contrast on a white background.
BLUE = "#0B85A6"     # S3 — smoothop blue
CYAN = "#05927F"     # C3
ORANGE = "#CC6318"   # O3
MAGENTA = "#9A23A3"  # M3
INK = "#404040"      # K5
MUTED = "#606060"    # K7
GRID = "#E1E1E1"     # W7

plt.rcParams.update({
    # Text rendered by LaTeX: same Computer Modern font as the document
    "text.usetex": True,
    "text.latex.preamble": r"\usepackage{amsmath}\usepackage{amssymb}",
    "font.family": "serif",
    "font.size": 11,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "axes.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK,
    "ytick.labelcolor": INK,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "legend.frameon": False,
})


def style(ax, grid_axis="both"):
    ax.spines[["top", "right"]].set_visible(False)
    if grid_axis:
        ax.grid(True, axis=grid_axis)
        ax.set_axisbelow(True)


# ---------------------------------------------------- tok_1_example.pdf
def fig_example():
    """Placeholder illustration for the tôk 1 publication — a clean styled
    figure in the Smoothop palette, wired end to end (generation, \\includegraphics,
    compilation), so the environment is proven functional. Replace with the real
    figures of the publication."""
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    xs = [j / 200.0 for j in range(201)]  # 0 .. 1
    ax.plot(xs, [x for x in xs], color=BLUE, lw=1.8, label="placeholder A")
    ax.plot(xs, [x * x for x in xs], color=ORANGE, lw=1.8, label="placeholder B")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("placeholder — replace with the real axis")
    ax.set_ylabel("placeholder")
    ax.xaxis.set_minor_formatter(NullFormatter())
    style(ax, grid_axis="y")
    ax.legend(loc="upper left")

    fig.savefig(os.path.join(OUT, "tok_1_example.pdf"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_example()
    print("OK:", sorted(f for f in os.listdir(OUT) if f.endswith(".pdf")))
