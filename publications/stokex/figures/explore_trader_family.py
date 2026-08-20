#!/usr/bin/env python3
"""Exploration of the family of trader functions fₚ(x) = xᵖ − x^(1−p).

A curiosity companion to the annex "The family of admissible trader
functions": what the members look like, why p = 1 saturates on the
selling side, and how the market price depends on the choice of p.

Usage: python explore_trader_family.py   (matplotlib required)
Produces: trader_family.png, family_price.png (next to the script).
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

# Smoothop palette (dataviz-validated, white background; green requires
# direct labels, present below)
COLORS = {1.0: "#0F8EB1", 1.5: "#6E39FF", 2.0: "#CC6018", 3.0: "#08B51F"}
INK, MUTED, GRID = "#333333", "#6E6E6E", "#E4E4E4"

plt.rcParams.update({
    "mathtext.fontset": "cm", "font.family": "serif", "font.size": 11,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "axes.linewidth": 0.8,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.labelcolor": INK, "ytick.labelcolor": INK,
    "grid.color": GRID, "grid.linewidth": 0.6, "legend.frameon": False,
})


def f_p(x, p):
    """Member p of the family: xᵖ − x^(1−p). The $tôkEx is p = 2."""
    return x ** p - x ** (1.0 - p)


def family_price(parts, p):
    """Closed-form market price of member p (annex, family eq.)."""
    num = sum(w * v ** (p - 1.0) for v, w in parts)
    den = sum(w * v ** (-p) for v, w in parts)
    return (num / den) ** (1.0 / (2.0 * p - 1.0))


def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, axis="y")
    ax.set_axisbelow(True)


# ---------------------------------------------------------- figure 1
# The members of the family: the saturation of f₁ on the selling side
def fig_family():
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(11, 4.6))

    # left panel: linear zoom around the equilibrium, slopes 2p−1
    xs = [0.02 + i / 500.0 for i in range(1500)]
    for p, c in COLORS.items():
        axl.plot(xs, [f_p(x, p) for x in xs], color=c, lw=1.8)
        axl.annotate(f"$p={p:g}$", (2.6, f_p(2.6, p)), color=c,
                     ha="left", va="center", fontsize=11,
                     xytext=(6, 0), textcoords="offset points")
    axl.plot([1], [0], "o", ms=6, color=INK, zorder=5)
    axl.set_xlim(0, 3)
    axl.set_ylim(-4, 8)
    axl.set_xlabel("price ratio $x$")
    axl.set_ylabel("$f_p(x)$")
    axl.set_title("near the equilibrium: slope $2p-1$ at $x=1$", fontsize=11)
    style(axl)

    # right panel: log scale, selling saturates for p = 1
    xs = [10 ** (-3 + i / 200.0) for i in range(1201)]
    for p, c in COLORS.items():
        axr.plot(xs, [f_p(x, p) for x in xs], color=c, lw=1.8)
    axr.axhline(-1.0, color=MUTED, lw=0.9, ls=(0, (4, 3)))
    axr.annotate("$f_1 > -1$: selling urgency saturates",
                 (10 ** -2.9, -1.0), xytext=(0, -14),
                 textcoords="offset points", color=INK, fontsize=10,
                 ha="left", va="top")
    axr.annotate("$p>1$: urgency unbounded\non both sides",
                 (10 ** 0.6, -5.0), color=INK, fontsize=10, ha="left")
    axr.set_xscale("log")
    axr.set_xlim(1e-3, 1e3)
    axr.set_ylim(-8, 12)
    axr.set_xlabel("price ratio $x$ (log scale)")
    axr.set_title("far from it: $p=1$ never hurries to sell", fontsize=11)
    style(axr)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "trader_family.png"), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------- figure 2
# The market price of the same market, according to the chosen member
def fig_price_vs_p():
    # small market: two camps with distant estimates, unequal weights
    parts = [(0.5, 1.0), (2.0, 0.5), (20.0, 0.25)]
    harmonic = sum(w for _, w in parts) / sum(w / v for v, w in parts)
    geo_extremes = math.sqrt(0.5 * 20.0)

    ps = [1.0 + i / 50.0 for i in range(0, 451)]
    Vs = [family_price(parts, p) for p in ps]

    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    ax.plot(ps, Vs, color=COLORS[2.0], lw=1.8)
    ax.axhline(geo_extremes, color=MUTED, lw=0.9, ls=(0, (4, 3)))
    for p_mark, label in ((1.0, "harmonic mean"), (2.0, "\\$tôkEx")):
        V = family_price(parts, p_mark)
        ax.plot([p_mark], [V], "o", ms=7, color=COLORS[p_mark],
                markeredgecolor="white", markeredgewidth=1.2, zorder=5)
        ax.annotate(f"$p={p_mark:g}$: {label}\n$V={V:.3f}$", (p_mark, V),
                    xytext=(12, 0), textcoords="offset points",
                    color=INK, fontsize=10, va="top")
    ax.annotate(r"$p\to\infty$: $\sqrt{v_{\min}\,v_{\max}}$"
                f" $= {geo_extremes:.3f}$",
                (ps[-1], geo_extremes), xytext=(0, 8),
                textcoords="offset points", ha="right", color=INK, fontsize=10)
    ax.set_xlabel("family member $p$")
    ax.set_ylabel(r"market price $[\alpha/\beta]_\Omega$")
    ax.set_title("one market, three estimates (0.5, 2, 20): "
                 "the price depends on $p$", fontsize=11)
    style(ax)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "family_price.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    fig_family()
    fig_price_vs_p()
    # a small curiosity table: the price of the same market according to p
    parts = [(0.5, 1.0), (2.0, 0.5), (20.0, 0.25)]
    print("toy market: estimates (0.5, 2, 20), weights (1, 0.5, 0.25)")
    print(f"{'p':>6} {'price V':>10} {'slope 2p-1':>11}")
    for p in (1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 100.0):
        print(f"{p:>6g} {family_price(parts, p):>10.4f} {2*p-1:>11g}")
    print("figures: trader_family.png, family_price.png")
