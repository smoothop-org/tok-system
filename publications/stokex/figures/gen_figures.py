#!/usr/bin/env python3
"""Generates the PDF figures of stokex_defensive_publication.tex (Smoothop palette).

Usage: python gen_figures.py  (matplotlib required; tested with 3.7)
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (Arc, Circle, FancyArrowPatch, FancyBboxPatch,
                                Polygon)
from matplotlib.ticker import NullFormatter, ScalarFormatter

OUT = os.path.dirname(os.path.abspath(__file__))

# Smoothop palette, shades -1 (validated for CVD/contrast on white background)
BLUE = "#0F8EB1"
ORANGE = "#CC6018"
MAGENTA = "#9A23A3"
INK = "#333333"
MUTED = "#6E6E6E"
GRID = "#E4E4E4"

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


# ------------------------------------------------- stokex_symmetry.pdf
def fig_symmetry():
    """Exchange velocities of the i-th participant: B is converted to α-equivalent
    via the participant's own estimate priceAB_i (their "fair" conversion rate), for
    a single common axis in units of Rdot (no dual scale); mirror."""
    v_i, theta = 10.0, 75.0
    w_i = math.tan(math.pi * theta / 200.0) / 3.0

    def f(p):
        return p * p - 1.0 / p

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    p = [10 ** (j / 300.0) for j in range(601)]  # 1 .. 100
    ax.plot(p, [w_i * f(q / v_i) for q in p], color=BLUE, lw=1.8,
            label=r"asset A: $\dot{X}_i^\alpha$ (in units of $\dot{R}$)",
            clip_on=True)
    ax.plot(p, [w_i * f(v_i / q) for q in p], color=ORANGE, lw=1.8,
            label=r"asset B: $\dot{X}_i^\beta\,[\alpha/\beta]_i$"
                  r" (in units of $\dot{R}$)",
            clip_on=True)
    ax.axvline(v_i, color=MUTED, lw=0.8, ls=(0, (2, 3)))
    ax.plot([v_i], [0.0], "o", ms=6, color=INK, zorder=5)

    ax.set_xscale("log")
    ax.set_xlim(1, 100)
    ax.set_ylim(-12, 40)
    ax.set_yticks([0, 20, 40])
    ax.set_xlabel(r"market price $[\alpha/\beta]_\Omega$"
                  r" (in $\alpha$ per unit of $\beta$, log scale)")
    ax.set_ylabel("exchange velocity, in units of $\\dot{R}$\n"
                  "(asset B converted at $i$'s own estimate)")
    style(ax, grid_axis="y")

    ax.text(v_i, -9, "equilibrium at the estimate", ha="center", color=INK,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8})
    ax.legend(loc="upper center", ncol=1, frameon=True, facecolor='white', edgecolor='none', framealpha=0.8)

    fig.savefig(os.path.join(OUT, "stokex_symmetry.pdf"),
                bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------ trader_function.pdf
def fig_trader_function():
    """The trader function f(x) = x^2 - 1/x, bare and alone: the zero at the
    estimate, buying below the estimate, selling above it, the unbounded
    urgency on both sides."""
    fig, ax = plt.subplots(figsize=(6.5, 4.2))

    # log scale in x: the ratio reads multiplicatively, and the window
    # [1/10, 10] is symmetric around the estimate
    xs = [10 ** (-1.0 + j / 1000.0) for j in range(2001)]  # 0.1 .. 10
    ax.plot(xs, [x * x - 1.0 / x for x in xs], color=BLUE, lw=1.8)

    ax.axhline(0.0, color=MUTED, lw=0.8)
    ax.axvline(1.0, color=MUTED, lw=0.8, ls=(0, (2, 3)))
    ax.plot([1.0], [0.0], "o", ms=6, color=INK, zorder=5)

    ax.set_xscale("log")
    ax.set_xlim(0.1, 10)
    ax.set_ylim(-10, 10)
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 5, 10],
                  ["0.1", "0.2", "0.5", "1", "2", "5", "10"])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_yticks([-10, -5, 0, 5, 10])
    ax.set_xlabel(r"price ratio $x$ (log scale)", fontsize=13)
    # rotation=0 leaves matplotlib's default va="bottom": without
    # va="center", the label floats above the middle of the axis
    ax.set_ylabel("$f(x)$", rotation=0, labelpad=16, fontsize=12,
                  va="center", ha="right")
    style(ax, grid_axis="y")

    ax.annotate("no trade at one's own estimate", (1.0, 0.0),
                xytext=(1.3, -6.0), ha="left", va="center", color=INK,
                fontsize=9.5,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9,
                                shrinkA=2, shrinkB=4))

    fig.savefig(os.path.join(OUT, "trader_function.pdf"), bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------- stokex_steps.pdf
def fig_steps():
    """The market price, piecewise constant between events."""
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    events = [0.0, 1.0, 1.5, 1.8]
    steps_t = [0.0, 1.0, 1.0, 1.5, 1.5, 1.8, 1.8, 3.0]
    steps_v = [1.0, 1.0, 1.2, 1.2, 0.6, 0.6, 0.5, 0.5]
    ax.plot(steps_t, steps_v, color=MAGENTA, lw=1.8)
    ax.plot([3.0, 5.0], [0.5, 0.5], color=MAGENTA, lw=1.8,
            ls=(0, (4, 3)), alpha=0.6)
    ax.plot(events, [0.0] * len(events), "o", ms=6, color=ORANGE,
            markeredgecolor="white", markeredgewidth=1.2,
            clip_on=False, zorder=5,
            label="execution of the inner algorithm")

    ax.set_xlim(0, 5)
    ax.set_ylim(0, 2)
    ax.set_xticks([0.0, 3.0], [r"$t_0$", r"$t_1$"])
    ax.set_yticks([])
    ax.set_xlabel("time")
    ax.set_ylabel(r"market price $[\alpha/\beta]_\Omega$")
    style(ax, grid_axis=None)
    ax.spines["left"].set_visible(False)

    ax.text(3.1, 0.62, "beyond $t_1$ (not yet computed)", color=MUTED,
            fontsize=10)
    ax.legend(loc="upper right")

    fig.savefig(os.path.join(OUT, "stokex_steps.pdf"), bbox_inches="tight")
    plt.close(fig)


# ------------------------- degree_of_certainty.pdf / degree_of_certainty_log.pdf
def fig_degree(log=False):
    """Geometric interpretation of θ. aspect='equal' so that the drawn angle
    is exactly arctan(3 w). The annex reasons about an arbitrary
    participant: θ and w appear there without an index."""
    RATIO = r"\frac{\,[\alpha/\beta]_\Omega}{[\alpha/\beta]_i}"

    w = 0.16  # schematic: angle readable at the scale of the graph
    slope = 3.0 * w
    theta_deg = math.degrees(math.atan(slope))

    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    if log:
        xs = [-2.0 + j / 200.0 for j in range(801)]
        ax.plot(xs, [w * (math.exp(2 * x) - math.exp(-x)) for x in xs],
                color=BLUE, lw=1.8)
        ax.set_xlim(-2, 2)
        x0 = 0.0
        ax.set_xlabel(r"$\ln\left(%s\right)$" % RATIO, fontsize=13)
    else:
        xs = [0.02 + j / 400.0 for j in range(1601)]
        ax.plot(xs, [w * (x * x - 1.0 / x) for x in xs], color=BLUE, lw=1.8)
        ax.set_xlim(0, 4)
        x0 = 1.0
        ax.set_xlabel("$%s$" % RATIO, fontsize=15)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")  # the on-screen angle = the geometric angle
    ax.set_ylabel(r"$\dot{X}_i^\alpha / \dot{R}$", rotation=0, labelpad=24,
                  fontsize=12)
    style(ax)

    # construction: horizontal, tangent, arc of the angle θ
    reach = 1.6
    dash = dict(color=INK, lw=1.1, ls=(0, (4, 3)))
    ax.plot([x0, x0 + reach], [0.0, 0.0], **dash)
    ax.plot([x0, x0 + reach], [0.0, slope * reach], **dash)
    ax.add_patch(Arc((x0, 0.0), 1.8, 1.8, angle=0.0,
                     theta1=0.0, theta2=theta_deg, color=INK, lw=1.1))
    mid = math.radians(theta_deg / 2.0)
    ax.annotate(r"$\theta_i$", (x0 + 1.12 * math.cos(mid), 1.12 * math.sin(mid)),
                ha="left", va="center", fontsize=13, color=INK)
    ax.plot([x0], [0.0], "o", ms=6, color=INK, zorder=5)

    name = "degree_of_certainty_log.pdf" if log else "degree_of_certainty.pdf"
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------- personal_trading_robot.pdf
def fig_robot_schema():
    """Schematic of the personal trading robot in the context of the market.

    An honest human participant declares two inputs, once; their personal
    robot then trades continuously in their place. Since this is a market,
    we show three participants: participant i (highlighted, honest) and two
    peers (greyed out, "one among others"). The aggregate of every robot
    sets the single market price, which feeds back into each robot
    continuously. A diagram, not a data graph."""
    # ---- Palette and drawing constants ---------------------------------
    FADE = "#AAAAAA"           # muted peers: "one participant among others"
    WHITE_PAD = 3.0            # pt, white box behind a label (masks the arrow)
    PAD = 0.12                 # data units, FancyBboxPatch corner pad
    TAIL, HEAD = 0.02, 0.04    # gap left outside a box by an arrow tail / head
    ROUND = "round,pad=%g,rounding_size=%g" % (PAD, PAD)
    SQUARE = "square,pad=%g" % PAD

    # ---- Layout: columns, human rows, and the boxes (cx, cy, w, h) ------
    COL_I, COL_J, COL_K = 5.0, 1.05, 8.95
    Y_PERSON, Y_NAME, Y_NOTE, Y_INPUT = 10.75, 10.15, 9.68, 8.85
    ROBOT_I = (COL_I, 6.825, 5.6, 2.55)
    ROBOT_J = (COL_J, 6.225, 1.4, 1.35)
    ROBOT_K = (COL_K, 6.225, 1.4, 1.35)
    MARKET = (COL_I, 2.75, 9.4, 1.6)
    BASE = ROBOT_I[1] - ROBOT_I[3] / 2      # shared bottom edge of every robot
    ROB_OUT = BASE - PAD - TAIL             # y where flows leave/enter a robot
    BUS_Y = 4.55                            # the single price bus

    fig, ax = plt.subplots(figsize=(7.6, 7.3))
    ax.set_xlim(0, 10)
    ax.set_ylim(1.55, 11.15)   # hug content: axis is off, so tight-bbox = limits
    ax.axis("off")

    # ---- Drawing helpers -----------------------------------------------
    def box(cx, cy, w, h, text, edgecolor, textcolor=INK, fontsize=10.5,
            lw=1.5, boxstyle=ROUND):
        ax.add_patch(FancyBboxPatch(
            (cx - w / 2, cy - h / 2), w, h, boxstyle=boxstyle, linewidth=lw,
            edgecolor=edgecolor, facecolor="white", zorder=3))
        if text:
            ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize,
                    color=textcolor, zorder=4)

    def arrow(xy_from, xy_to, color=INK, lw=1.3, ls="solid"):
        ax.add_patch(FancyArrowPatch(
            xy_from, xy_to, arrowstyle="-|>", mutation_scale=12,
            color=color, lw=lw, linestyle=ls, shrinkA=0, shrinkB=0, zorder=2))

    def label(x, y, text, color=MUTED, fontsize=9.5, ha="center",
              style="normal"):
        ax.text(x, y, text, ha=ha, va="center", fontsize=fontsize, color=color,
                zorder=5, style=style,
                bbox=dict(facecolor="white", edgecolor="none", pad=WHITE_PAD))

    def person(cx, cy, s, color):
        ax.add_patch(Circle((cx, cy + 0.17 * s), 0.13 * s, facecolor="white",
                            edgecolor=color, lw=1.4, zorder=4))
        ax.add_patch(Polygon(
            [(cx - 0.24 * s, cy - 0.30 * s), (cx + 0.24 * s, cy - 0.30 * s),
             (cx + 0.15 * s, cy + 0.02 * s), (cx - 0.15 * s, cy + 0.02 * s)],
            closed=True, facecolor="white", edgecolor=color, lw=1.4,
            joinstyle="round", zorder=4))

    def top_in(b):
        """y just above box b's top edge, where an arrow head should land."""
        return b[1] + b[3] / 2 + PAD + HEAD

    MKT_IN = top_in(MARKET)    # y where the exchange velocities reach the market

    # ---- Peers j and k: a participant, their robot, their trades (muted) -
    # Each peer trades out on its outer edge and reads the price on its inner
    # edge; `side` (-1 for j, +1 for k) mirrors the two columns.
    for b, tag, side in ((ROBOT_J, "j", -1), (ROBOT_K, "k", +1)):
        cx = b[0]
        person(cx, Y_PERSON, 0.85, FADE)
        label(cx, Y_NAME, "Participant $%s$" % tag, color=FADE, fontsize=9.5)
        arrow((cx, Y_NAME - 0.40), (cx, top_in(b)), color=FADE, lw=1.1)
        label(cx, Y_INPUT, r"$[\alpha/\beta]_%s,\ \theta_%s$" % (tag, tag),
              color=FADE, fontsize=8.5)
        box(*b, r"\texttt{robot %s}" % tag, FADE, textcolor=FADE, fontsize=9.5,
            lw=1.2, boxstyle=SQUARE)
        arrow((cx + side * 0.45, ROB_OUT), (cx + side * 0.25, MKT_IN),
              color=FADE, lw=1.1)                                  # trade out
        arrow((cx - side * 0.45, BUS_Y), (cx - side * 0.45, ROB_OUT),
              color=FADE, lw=1.0)                         # price in

    # ---- Participant i: the human, in full detail ----------------------
    person(COL_I, Y_PERSON, 1.0, INK)
    label(COL_I, Y_NAME, "Participant $i$", color=INK, fontsize=11)
    label(COL_I, Y_NOTE, "declares estimate and confidence once at $t_0$",
          color=MUTED, fontsize=8.7, style="italic")
    arrow((COL_I, Y_NOTE - 0.30), (COL_I, top_in(ROBOT_I)), color=INK)
    label(COL_I, Y_INPUT, r"$[\alpha/\beta]_i,\ \theta_i$", color=INK,
          fontsize=10)

    # Square, monospace = the machine. Title / equations / standing order are
    # placed separately (linespacing is ignored under usetex) so each breathes.
    box(*ROBOT_I, "", BLUE, boxstyle=SQUARE)
    ax.text(COL_I, 7.72, r"\texttt{personal trading robot i}", ha="center",
            va="center", color=INK, fontsize=9, zorder=4)
    ax.text(COL_I, 6.78,
            r"$\begin{aligned}"
            r"\dot{X}_i^\alpha &= w(\theta_i)\, f\!\left("
            r"\dfrac{[\alpha/\beta]_\Omega}{[\alpha/\beta]_i}\right)\dot{R}"
            r"\\[6pt]"
            r"\dot{X}_i^\beta &= w(\theta_i)\, f\!\left("
            r"\dfrac{[\beta/\alpha]_\Omega}{[\beta/\alpha]_i}\right)"
            r"\dot{R}\,[\beta/\alpha]_i"
            r"\end{aligned}$",
            ha="center", va="center", color=INK, fontsize=9.5, zorder=4)
    ax.text(COL_I, 5.88, r"\texttt{buy low, sell high, every instant}",
            ha="center", va="center", color=INK, fontsize=9, zorder=4)

    # Two exchange velocities flow down into the market; labels ride the arrows.
    arrow((3.8, ROB_OUT), (4.0, MKT_IN), color=INK)
    arrow((6.2, ROB_OUT), (6.0, MKT_IN), color=INK)
    label(3.86, 4.90, r"$\dot{X}_i^\alpha$", color=INK, fontsize=10)
    label(6.14, 4.90, r"$\dot{X}_i^\beta$", color=INK, fontsize=10)

    # ---- The market: the aggregate of every robot ----------------------
    box(*MARKET, "", MAGENTA)
    ax.text(COL_I, 3.04, r"\textbf{Market: every participant's robot at once}",
            ha="center", va="center", color=INK, fontsize=10.5, zorder=4)
    ax.text(COL_I, 2.40,
            r"$\sum_i \dot{X}_i^\alpha = \sum_i \dot{X}_i^\beta = 0"
            r"\ \Longrightarrow\ [\alpha/\beta]_\Omega$",
            ha="center", va="center", color=INK, fontsize=10.5, zorder=4)

    # ---- Price bus: one market price, fed up the middle to every robot --
    ax.plot([0.9, 9.1], [BUS_Y, BUS_Y], color=MUTED, lw=1.1, zorder=1)
    arrow((COL_I, MKT_IN), (COL_I, BUS_Y), color=MUTED, lw=1.1)  # market feeds it
    arrow((COL_I, BUS_Y), (COL_I, ROB_OUT), color=MUTED, lw=1.1)
    label(COL_I, 4.12, r"$[\alpha/\beta]_\Omega$", color=MUTED, fontsize=9.5)

    fig.savefig(os.path.join(OUT, "personal_trading_robot.pdf"),
                bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------- cadeur_example.pdf
def fig_cadeur_example():
    """Numerical illustration relevant to the tok system (exchange
    against a foreign currency): CAD/EUR (CAD per EUR = DEXCAUS x
    DEXUSEU, FRED)."""
    import pandas as pd

    # alpha = CAD, beta = EUR
    RCAD = 1.0  # CAD / day, arbitrary reference
    theta = 70.0 # %

    df = pd.read_csv(os.path.join(OUT, "cadeur_daily.csv"))
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df["DEXCAUS"] = pd.to_numeric(df["DEXCAUS"], errors="coerce")
    df["DEXUSEU"] = pd.to_numeric(df["DEXUSEU"], errors="coerce")
    df["CADEUR"] = df["DEXCAUS"] * df["DEXUSEU"]  # CAD per 1 EUR
    df = df.dropna(subset=["CADEUR"]).reset_index(drop=True)

    # 5 years of observation before 5 years of trading with fixed parameters
    test_end = df["observation_date"].max()  # July 1st 2026
    test_start = test_end - pd.DateOffset(years=5)
    fit_start = test_start - pd.DateOffset(years=5)
    fit = df[(df["observation_date"] >= fit_start)
             & (df["observation_date"] < test_start)].reset_index(drop=True)
    full = df[df["observation_date"] >= fit_start].reset_index(drop=True)
    df = df[df["observation_date"] >= test_start].reset_index(drop=True)
    market_price = df["CADEUR"] # CAD/EUR

    # participant variables
    estimate = fit["CADEUR"].mean() # CAD/EUR, plain 5-year average, no trend fit
    w = (1.0 / 3.0) * math.tan(math.pi * theta / 200.0)
    x = market_price / estimate
    f = lambda z: z ** 2 - 1.0 / z
    XCAD = w * f(x) * RCAD                   # CAD/day
    XEUR = w * f(1.0 / x) * RCAD / estimate  # EUR/day

    # balances
    n0 = 100.0  # 100 CAD and 100 EUR to start -- both native, round units
    cumsumCAD = XCAD.cumsum() # accumulated CAD, from t0
    cumsumEUR = XEUR.cumsum() # accumulated EUR, from t0
    nCAD = n0 + cumsumCAD # amount CAD
    nEUR = n0 + cumsumEUR # amount EUR
    dnCAD = nCAD - nCAD.iloc[0] # amount change CAD, since t0
    dnEUR = nEUR - nEUR.iloc[0] # amount change EUR, since t0
    PCAD = dnCAD + dnEUR * market_price # total profit CAD, since t0
    PEUR = dnEUR + dnCAD / market_price # total profit EUR, since t0

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(
        4, 1, figsize=(6.8, 10.6), sharex=True, height_ratios=[1, 1, 1, 1])

    SHADE = "#EDEDED"
    colorCADEUR = "#501650"
    for ax in (ax1, ax2, ax3, ax4):
        ax.axvspan(fit_start, test_start, color=SHADE, zorder=0)
        ax.axvline(test_start, color=MUTED, lw=0.9, ls=(0, (1, 2)), zorder=1)

    ax1.plot(full["observation_date"], full["CADEUR"], color=colorCADEUR, lw=1.2, zorder=2)
    ax1.plot([fit_start, test_start], [estimate, estimate],
              color=INK, lw=1.3, zorder=3)
    ax1.axhline(estimate, color=INK, lw=1.1, ls=(0, (4, 3)), zorder=1)
    ax1.annotate(
        r"Estimate $[\mathrm{CAD/EUR}]_i$ at $t_0$ "
        r"$=$ 5-year average over observation window"
        r" $\approx %.3f$ CAD/EUR" % estimate,
        xy=(fit_start + 0.30 * (test_start - fit_start), estimate),
        xytext=(fit_start + (test_end - fit_start) / 2, 1.77),
        color=INK, fontsize=9, ha="center", va="top",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                  edgecolor=GRID, linewidth=0.8))
    ax1.text((fit_start + (test_start - fit_start) / 2), 1.15,
              "observation window", color=MUTED, fontsize=9.5,
              ha="center", va="bottom", style="italic")
    ax1.text((test_start + (test_end - test_start) / 2), 1.15,
              "exchange window", color=MUTED, fontsize=9.5,
              ha="center", va="bottom", style="italic")
    ax1.text(test_start, 1.15, r"$t_0$", color=INK, fontsize=10,
              ha="center", va="bottom",
              bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    ax1.set_xlim(fit_start, test_end)   # snug to the data (shared x-axis)
    ax1.set_yscale("log")
    ax1.set_ylim(1.2, 1.8)
    ax1.set_yticks([1.2, 1.4, 1.6, 1.8])
    ax1.yaxis.set_major_formatter(ScalarFormatter())
    ax1.yaxis.set_minor_formatter(NullFormatter())
    ax1.set_ylabel("CAD/EUR rate\n(CAD per 1 EUR, log scale)", color=colorCADEUR)
    style(ax1, grid_axis="y")

    # Panel 2: CAD (red) and EUR (blue), each a native currency unit --
    # no numeraire imposed between them, as in the ETF example.
    colorCAD = "#990000"
    dates = df["observation_date"]
    ax2.plot(dates, nCAD, color=colorCAD, lw=1.4, zorder=3)
    ax2.set_ylim(0, 200)
    ax2.set_ylabel("Amount\n(CAD)", color=colorCAD)
    ax2.tick_params(axis="y", colors=colorCAD)
    style(ax2, grid_axis="y")

    colorEUR =  "#003399"
    ax2b = ax2.twinx()
    ax2b.plot(dates, nEUR, color=colorEUR, lw=1.4, zorder=3)
    ax2b.axhline(n0, color=MUTED, lw=0.7, ls=(0, (2, 3)), alpha=0.6, zorder=1)
    ax2b.set_ylim(0, 200)
    ax2b.set_ylabel("Amount\n(EUR)", color=colorEUR)
    ax2b.tick_params(axis="y", colors=colorEUR)
    ax2b.grid(False)
    ax2b.spines[["top"]].set_visible(False)

    # Panel 3: total profit accounted in CAD.
    ax3.plot(dates, PCAD, color=colorCAD, lw=1.4)
    ax3.axhline(0.0, color=MUTED, lw=0.8, ls=(0, (2, 3)))
    ax3.set_ylabel("Total profit\n(CAD)", color=colorCAD)
    ax3.tick_params(axis="y", colors=colorCAD)
    style(ax3, grid_axis="y")

    # Panel 4: the same portfolio, the same trades, accounted in EUR instead.
    ax4.plot(dates, PEUR, color=colorEUR, lw=1.4)
    ax4.axhline(0.0, color=MUTED, lw=0.8, ls=(0, (2, 3)))
    ax4.set_ylabel("Total profit\n(EUR)", color=colorEUR)
    ax4.tick_params(axis="y", colors=colorEUR)
    ax4.set_xlabel("date")
    style(ax4, grid_axis="y")

    fig.align_ylabels([ax1, ax2, ax3, ax4])
    fig.savefig(os.path.join(OUT, "cadeur_example.pdf"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_symmetry()
    fig_trader_function()
    fig_steps()
    fig_degree(log=False)
    fig_degree(log=True)
    fig_robot_schema()
    fig_cadeur_example()
    print("OK:", sorted(f for f in os.listdir(OUT) if f.endswith(".pdf")))
