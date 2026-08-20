# python_toy — a working $tôkEx you can run

You have read (or are reading) **`stokex_defensive_publication.pdf`**. This folder
is the same algorithm, made runnable — a small gallery of three exhibits you can
run in seconds and read line by line.

The $tôkEx is an **order-book-free, continuous exchange between two fungible
assets**: no bids, no asks, no matching. Each participant declares only *where
they think the price is* and *how sure they are*; a closed-form market price
emerges, and everyone trades toward it at once. These scripts let you watch that
happen.

Everything here was written **from the document alone** — not copied from the tôk
backend. That is deliberate: a defensive publication must be *enabling*, and the
best proof that it is, is that anyone can rebuild the mechanism from the text.
Every function points back at the equation or the section it realizes.

---

## Run the tour

No installation for two of the three exhibits — they use the standard library
only. From the repository root:

```sh
# 1. The mechanism, in full          (no dependencies)
python3 publications/stokex/python_toy/stokex_toy.py

# 2. The claims of the paper, checked (no dependencies)
python3 publications/stokex/python_toy/verify_stokex.py

# 3. The story, in pictures          (needs matplotlib → use the venv)
./.venv/bin/python publications/stokex/python_toy/stokex_toy_sim.py         # writes a PNG
./.venv/bin/python publications/stokex/python_toy/stokex_toy_sim.py --show  # + a live window
```

New here? Start with **1**, then **3**, then **2**.

---

## The three exhibits

### 1 · `stokex_toy.py` — the mechanism

A complete market in ~300 lines and zero dependencies: the two functions of the
mechanism, the closed-form price, the inner algorithm (exclusion → price →
sorted reintegration), and the outer algorithm (exact, event-by-event stepping).

**What you'll see.** Four participants — Alice, Bob, Carol, Dan — each with an
estimate and a degree of confidence. The script prints the market price they
agree on, each robot's two exchange velocities, and the time until each account
runs dry; then it lets the market run for 60 units of time and reports where the
price settles.

**The capabilities it makes concrete:**

| You see… | …the article's claim |
|---|---|
| one price from four disagreeing estimates | closed-form market price, eq. (14) |
| the price sitting between the smallest and largest estimate | bracketing, Annex 7.7 |
| the four robots' flows summing to zero | equilibrium & conservation, principle 1, eq. (13) |
| a probe showing the crowd = one synthetic participant | aggregation, eq. (16)–(17) |
| accounts emptying at computed instants, price jumping | exact event stepping, Sec. 4.2 |

All invariants are re-checked with `assert` as the demo runs: if the mechanism
ever failed to conserve or to clear at the price, the script would stop.

### 2 · `verify_stokex.py` — the claims, checked

Thirteen independent numerical tests, one per headline result of the paper —
equilibrium, uniqueness, aggregation, the tangent-map weight, the stable shifted
form of the trader function on `[1e-12, 1e12]`, the incremental price update,
the demurrage-adjusted emptying time, and more. No dependencies; reproducible
seed.

**What you'll see.** A table ending in `→ TOUT PASSE — le papier dit vrai.`
Every row is a claim from the document confirmed to machine precision. This is
the numerical counterpart to the machine-checked Lean proofs in
[`../lean_proofs/`](../lean_proofs/): the proofs establish *that* the results
hold; this establishes *that the numbers behave*.

### 3 · `stokex_toy_sim.py` — the story, in pictures

The same engine as exhibit 1, run for 120 units of time with matplotlib, staging
every kind of event the document foresees. Output is `stokex_toy_sim.png`
(regenerated, not versioned).

**What you'll see**, across four stacked panels sharing a timeline:

- **the price**, a solid line threading between the participants' estimates —
  and never leaving the interval they span;
- **the balances** of each asset, draining and filling as the market trades;
- **a participant running dry and leaving** (Sec. 4.1, exclusion), then, after
  Bob revises his estimate upward and pulls the price past Carol, **Carol
  re-entering** as a seller of the asset she still holds (the sorted
  reintegration);
- **the market's stiffness** `W_Ω`, the single number the crowd aggregates to.

The picture is the mechanism's autobiography: disagreement, a price, events, and
conservation holding through all of them.

---

## What the toy leaves out, on purpose

The point here is the *mechanism*, so the refinements of Sec. 4.3 are omitted:
no compensated summation or extended precision, no tôk-style disintegration
(both assets are assumed inert, the document's default), no bounds on estimates
or discretized confidence. They change nothing about how the exchange works —
which is exactly why they are left out of the exhibit.

For the full workflow (figures, LaTeX, Lean, go-live) see the
[parent README](../README.md).
