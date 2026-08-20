#!/usr/bin/env python3
"""A small toy simulation of the $tôkEx, and its plots.

Companion to `stokex_toy.py`, which carries the mechanism and depends on
nothing. This script adds matplotlib, runs a four-participant market for 120
units of time, and plots what happens.

Three kinds of event are staged, all of them foreseen by the document (the
simulation produces five occurrences):
  1. a participant runs dry and leaves the market (Sec. 4.1, the exclusion);
  2. a participant revises their declaration (Sec. 4, action 4), which moves
     the price at once;
  3. the emptied participant is reintegrated as soon as they hold the asset
     they wish to sell (Sec. 4.1, the sorted reintegration).

Colors: the Smoothop palette, `docs/Style.md`. The −1 shades of blue and
orange are validated for contrast and color-vision deficiency; the green and
magenta added here to carry four series are not yet --- an open item in
`TODO.md`.

Output: `stokex_toy_sim.png`, **not versioned** --- an illustration is
regenerated, not archived.

Run with:
  ./.venv/bin/python publications/stokex/python_toy/stokex_toy_sim.py         # writes the PNG
  ./.venv/bin/python publications/stokex/python_toy/stokex_toy_sim.py --show  # + a window
"""
import os
import sys

import matplotlib

# By default the script is headless: it writes a PNG and returns, which makes
# it runnable anywhere, screen or no screen. With --show it keeps the machine's
# native backend and opens a real, zoomable window.
SHOW = "--show" in sys.argv
if not SHOW:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt

from stokex_toy import Market, Participant, weight_of_degree

OUT = os.path.dirname(os.path.abspath(__file__))

# Smoothop palette (docs/Style.md) — brand hues, shade 3
BLUE = "#0B85A6"     # S3, the Smoothop blue
ORANGE = "#CC6318"   # O3
GREEN = "#1A7A27"    # G3
MAGENTA = "#9A23A3"  # M3
INK = "#404040"      # K5
GRID = "#CACACA"     # W5

SERIES = [BLUE, ORANGE, GREEN, MAGENTA]

plt.rcParams.update({
    "font.size": 9,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def simulate(market, duration, step, revision=None):
    """Sample the market's trajectory without ever spoiling the exact stepping.

    We advance in small chunks; `Market.advance` handles internally any event
    falling inside a chunk, so the state stays exact. `revision` is a pair
    (instant, function) applied along the way.
    """
    hist = {"t": [], "price": [], "weight": [], "n_participants": [],
            "alpha": [[] for _ in market.participants],
            "beta": [[] for _ in market.participants],
            "estimate": [[] for _ in market.participants]}
    events = []

    t = 0.0
    market.inner()
    trading_before = {p.name for p in market.participants if p.trading}
    done_revision = revision is None

    while t <= duration + 1e-12:
        for key, val in (("t", t), ("price", market.price),
                         ("weight", market.total_weight)):
            hist[key].append(val)
        hist["n_participants"].append(sum(1 for p in market.participants if p.trading))
        for i, p in enumerate(market.participants):
            hist["alpha"][i].append(p.n_alpha)
            hist["beta"][i].append(p.n_beta)
            hist["estimate"][i].append(p.estimate)   # it may change along the way

        trading_now = {p.name for p in market.participants if p.trading}
        if trading_now != trading_before:
            for name in trading_before - trading_now:
                events.append((t, f"{name} leaves", ORANGE))
            for name in trading_now - trading_before:
                events.append((t, f"{name} returns", GREEN))
            trading_before = trading_now

        if not done_revision and t >= revision[0]:
            revision[1](market)
            market.inner()
            events.append((t, "revision", MAGENTA))
            done_revision = True

        market.advance(step)
        t += step

    return hist, events


def _revise(market):
    """Bob changes his mind: he thinks β is worth far more, and firmly so.

    Firmly enough to pull the market price **above** Carol's estimate --- and
    Carol, out of α for a long while, becomes a seller of β again, the asset
    she has left. That is the reintegration of Sec. 4.1.
    """
    bob = next(p for p in market.participants if p.name == "Bob")
    bob.estimate = 6.0
    bob.degree = 92.0
    bob.weight = weight_of_degree(92.0)


def main():
    market = Market([
        Participant("Alice", estimate=2.00, degree=75.0, n_alpha=100.0, n_beta=50.0),
        Participant("Bob",   estimate=1.00, degree=50.0, n_alpha=80.0,  n_beta=80.0),
        Participant("Carol", estimate=3.50, degree=90.0, n_alpha=10.0,  n_beta=200.0),
        Participant("Dan",   estimate=1.50, degree=30.0, n_alpha=60.0,  n_beta=60.0),
    ], reference_velocity=1.0)

    a0, b0 = market.totals()
    hist, events = simulate(market, duration=120.0, step=0.05, revision=(50.0, _revise))
    a1, b1 = market.totals()

    fig, axes = plt.subplots(4, 1, figsize=(7.2, 9.0), sharex=True)
    t = hist["t"]

    # 1 — the market price, and the estimates it aggregates
    ax = axes[0]
    for i, p in enumerate(market.participants):
        # the declared estimate over time: Bob changes his along the way
        ax.plot(t, hist["estimate"][i], color=SERIES[i], lw=0.9,
                ls=(0, (4, 3)), alpha=0.8)
    ax.plot(t, hist["price"], color=INK, lw=2.0)
    ax.set_ylabel(r"$[\alpha/\beta]_\Omega$")
    ax.set_title("The market price, bracketed by the participants' estimates",
                 fontsize=10, loc="left")
    style(ax)

    # 2 — the asset A balances
    ax = axes[1]
    for i, p in enumerate(market.participants):
        ax.plot(t, hist["alpha"][i], color=SERIES[i], lw=1.6, label=p.name)
    ax.set_ylabel(r"$n_i^\alpha$")
    ax.legend(ncol=4, frameon=False, fontsize=8, loc="upper left")
    ax.set_ylim(top=ax.get_ylim()[1] * 1.18)
    style(ax)

    # 3 — the asset B balances
    ax = axes[2]
    for i, p in enumerate(market.participants):
        ax.plot(t, hist["beta"][i], color=SERIES[i], lw=1.6)
    ax.set_ylabel(r"$n_i^\beta$")
    style(ax)

    # 4 — the stiffness of the market
    ax = axes[3]
    ax.plot(t, hist["weight"], color=BLUE, lw=1.8)
    ax.set_ylabel(r"$W_\Omega$")
    # Ṙ is a velocity, not a duration: the axis is in the market's own time
    # unit, and Ṙ = 1 is what fixes the pace measured against it.
    ax.set_xlabel(r"time (arbitrary unit, with $\dot{R} = 1\,\alpha$ per unit)")
    style(ax)

    # the events, on all four panels
    for ax in axes:
        for t_e, label, color in events:
            ax.axvline(t_e, color=color, lw=1.0, ls=(0, (2, 2)), alpha=0.8)
    # labels staggered in alternation: two events can follow one another very
    # closely (the revision, and the reintegration it triggers)
    for rank, (t_e, label, color) in enumerate(events):
        axes[0].annotate(label, (t_e, axes[0].get_ylim()[1]), fontsize=7.5,
                         color=color, rotation=90, va="top", ha="right",
                         xytext=(-2, -4 - 26 * (rank % 2)), textcoords="offset points")

    fig.tight_layout()
    path = os.path.join(OUT, "stokex_toy_sim.png")
    fig.savefig(path, dpi=170)

    print(f"figure written : {path}")
    print(f"final price    : {market.price:.6f} α per β")
    print(f"events         : " + ", ".join(f"{lab} at t={te:.2f}" for te, lab, _ in events))
    print(f"conservation   : Δ(Σn^α) = {a1 - a0:.3e}, Δ(Σn^β) = {b1 - b0:.3e}")
    assert abs(a1 - a0) < 1e-6 and abs(b1 - b0) < 1e-6, "the mechanism no longer conserves"
    print("conservation verified over the whole simulation.")

    if SHOW:
        print("window open — close it to return.")
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
