# stokexproof — formal verification of the $tôkEx

Proof in **Lean 4 + mathlib** of the central claims of the defensive publication
`../stokex_defensive_publication.tex`. What is proven here is proven: a machine has
verified it, line by line.

The theorems, and the annex of the document they cover:

| Theorem | What it establishes | Annex |
|---|---|---|
| `traderF_slope_at_one` | the slope of `f` at `x = 1` equals 3 — the basis of the angular interpretation `w = tan(θ)/3` | 7.4 |
| `exchange_at_market_price` | every exchange happens at the market price: `−Ẋᵅ/Ẋᵝ = [α/β]_Ω` | 7.5 |
| `market_clears` | the closed-form price zeroes the net flow of asset A | 7.6 |
| `market_price_unique` | the equilibrium price is unique | 7.7 |
| `market_is_single_participant` | the whole market behaves as a single participant of weight `W_Ω` | 7.8 |
| `traderF_strictMonoOn` | the trader function is strictly increasing on `(0, ∞)` — principle 7 | — |

The annex numbers are those of the August 2026 version; the stable `\label` keys
(`secProofDegree`, `secProofUniqueness`, …) are given at the top of the Lean file,
together with the article ↔ Lean notation dictionary.

**The exact scope, without rounding.** Two clarifications the table cannot carry,
and that matter to whoever verifies:

- `market_clears` proves the **converse** of annex 7.6. The annex starts from
  equilibrium and derives the closed-form price (necessity); the theorem starts from
  the closed-form price and derives equilibrium (sufficiency). The article leaves this
  direction implicit; the machine covers it.
- `market_price_unique` proves **uniqueness only**. The existence of an equilibrium
  price, which annex 7.7 obtains through the intermediate value theorem, is not
  formalized here.

## Toolchain and dependencies

The Lean setup is **self-contained in this repository** (see `docs/Cablage.md`,
organ E — the workbench, and AGENTS.md, "Lean"):

- the toolchain is pinned by the **repo-root `lean-toolchain`**
  (`leanprover/lean4:v4.32.0`), so any `lake`/`lean` run inside the repo uses that
  version, independent of the machine's global Lean. **elan** — the toolchain
  manager (https://leanprover-community.github.io/get_started.html) — installs it on
  its own on the first invocation of `lake`.
- **mathlib**, version `v4.32.0`, pinned in `lakefile.toml` and `lake-manifest.json`,
  is prebuilt once in the shared `.lake-shared/` cache at the repo root; this
  project's `.lake` symlinks to it, so there is no per-project download or rebuild.
- the shared foundation `lean_common/` (library `TokCommon`) is required by relative
  path; `lake` builds it alongside the proofs.

If something is genuinely missing, we say so and do not improvise: a half-verified
proof proves nothing.

## Verifying the proof

```sh
cd publications/stokex/lean_proofs && lake build
```

Run `lake` from this directory, never from the bare repo root. Because mathlib is
already built in `.lake-shared/`, **no `lake exe cache get` is needed** — the oleans
are local. An error-free output **is** the result: all the theorems of the file are
verified. The build artifacts (under `.lake/` → `.lake-shared/`) are gitignored.

## Notes

This folder is the mirror of a standalone Lean repository; its `.github/workflows/`
do not run here (GitHub reads only the `.github/` at the repository root). They are
kept as is so the folder stays detachable.

Like all of `publications/`, this content is in the **signed zone**: CC BY 4.0 (see
`../LICENSE`), not CC0 like the rest of the repo.
