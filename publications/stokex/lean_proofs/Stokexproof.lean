/-
Formal verification (Lean 4 + mathlib) of the central claims of
"The $tôkEx Algorithm" (Smoothop, defensive publication, 2026).

# Notation

The identifiers below follow the article as closely as Lean allows. In
particular the market price and a participant's estimate are the *same*
letter with different subscripts, exactly as in the article, rather than
two letters distinguished only by case.

| Article                          | Here    | Meaning                            |
|----------------------------------|---------|------------------------------------|
| `[α/β]_i`                        | `p i`   | participant `i`'s estimate         |
| `[α/β]_Ω`                        | `pΩ`    | the market price                   |
| `[α/β]_z`                        | `pz`    | a probe price (Sec. 5.1)           |
| `[β/α]_i = 1/[α/β]_i`            | `1/p i` | the reciprocal estimate            |
| `w_i`                            | `w i`   | participant `i`'s weight, Eq. (5)  |
| `Ṙ`                              | `R`     | the reference exchange velocity    |
| `W_Ω`                            | —       | written out as `(∑ w i * p i)/pΩ`  |
| `f`                              | `traderF` | the trader function, Eq. (2)     |

Two identifications used throughout, both from `[β/α] = 1/[α/β]`:
the denominator `∑ wᵢ [β/α]ᵢ²` of the market price Eq. (14) is written
`∑ w i / (p i)^2`, and the total market weight Eq. (17),
`W_Ω = [β/α]_Ω ∑ wᵢ [α/β]ᵢ`, is written `(∑ w i * p i) / pΩ`.

# What is proved, and where it lives in the article

Annex numbers are those of the 2026-07 version; the `\label` keys in
brackets are stable across renumbering.

  * `traderF_slope_at_one` : f'(1) = 3 — the basis of the angular
    interpretation of the degree of confidence, w = tan(θ)/3.
    Annex 7.4 [secProofDegree].
  * `exchange_at_market_price` : −Ẋᵅ/Ẋᵝ = [α/β]_Ω — every exchange occurs
    at the market price (principle 2, Eq. (7)).
    Annex 7.5 [secProofExchangeAtMarketPrice].
  * `market_clears` : the closed-form price Eq. (14) cancels the net flow
    of asset A. Note the direction: Annex 7.6 derives Eq. (14) *from* the
    equilibrium condition (necessity); this theorem proves the converse
    (sufficiency), which the article leaves implicit.
    Annex 7.6 [secProofMarketprice].
  * `market_is_single_participant` : the whole market behaves as a single
    participant of weight W_Ω, Eq. (16).
    Annex 7.8 [secProofTotalMarketWeight].
  * `traderF_strictMonoOn` : the trader function is strictly increasing on
    (0, ∞) — principle 7, and the engine of the uniqueness proof.
  * `market_price_unique` : the market-clearing price is unique.
    Annex 7.7 [secProofUniqueness]. Uniqueness only: the *existence* of
    an equilibrium price, which the article obtains from the intermediate
    value theorem, is not formalized here.
-/
import Mathlib

open Finset

noncomputable section

/-- The $tôkEx trader function, Eq. (2): `f(x) = x² − 1/x`, for a price
ratio `x > 0` (defined totally on ℝ here; the theorems carry the
nonvanishing hypotheses). -/
def traderF (x : ℝ) : ℝ := x ^ 2 - 1 / x

/-- **Exchange at the market price.** For any participant (estimate
`p ≠ 0`, weight `w`, reference exchange velocity `R`) and any market price
`pΩ ≠ 0`, the exchange velocity of asset A equals `−[α/β]_Ω` times the
(symmetric) velocity of asset B: `−Ẋᵅ/Ẋᵝ = [α/β]_Ω`, Eq. (7).

The two sides are Eq. (6) written out: `Ẋᵅ = w f([α/β]_Ω/[α/β]_i) Ṙ` and
`Ẋᵝ = w f([β/α]_Ω/[β/α]_i) Ṙ [β/α]_i`, the reciprocals kept explicit. -/
theorem exchange_at_market_price (w R pΩ p : ℝ) (hp : p ≠ 0) (hpΩ : pΩ ≠ 0) :
    w * traderF (pΩ / p) * R = -pΩ * (w * traderF ((1 / pΩ) / (1 / p)) * R * (1 / p)) := by
  unfold traderF
  field_simp
  ring

/-- **The price clears the market.** If `pΩ ≠ 0` satisfies the closed form
Eq. (14), `[α/β]_Ω³ · Σ wᵢ[β/α]ᵢ² = Σ wᵢ[α/β]ᵢ`, then the net flow of
asset A vanishes, Eq. (13). -/
theorem market_clears {ι : Type*} (s : Finset ι) (p w : ι → ℝ) (pΩ : ℝ)
    (hp : ∀ i ∈ s, p i ≠ 0) (hpΩ : pΩ ≠ 0)
    (hprice : pΩ ^ 3 * ∑ i ∈ s, w i / (p i) ^ 2 = ∑ i ∈ s, w i * p i) :
    ∑ i ∈ s, w i * traderF (pΩ / p i) = 0 := by
  have expand : ∀ i ∈ s, w i * traderF (pΩ / p i)
      = pΩ ^ 2 * (w i / (p i) ^ 2) - (w i * p i) / pΩ := by
    intro i hi
    have := hp i hi
    unfold traderF
    field_simp
  calc ∑ i ∈ s, w i * traderF (pΩ / p i)
      = ∑ i ∈ s, (pΩ ^ 2 * (w i / (p i) ^ 2) - (w i * p i) / pΩ) :=
        Finset.sum_congr rfl expand
    _ = pΩ ^ 2 * (∑ i ∈ s, w i / (p i) ^ 2) - (∑ i ∈ s, w i * p i) / pΩ := by
        rw [Finset.sum_sub_distrib, Finset.mul_sum, Finset.sum_div]
    _ = 0 := by
        field_simp
        linear_combination hprice

/-- **The market is a single participant.** Against any probe price
`pz ≠ 0`, the sum of the individual responses equals the response of a
single participant with estimate `[α/β]_Ω` and total market weight
`W_Ω = (Σ wᵢ[α/β]ᵢ)/[α/β]_Ω`, Eqs. (16)–(17). -/
theorem market_is_single_participant {ι : Type*} (s : Finset ι) (p w : ι → ℝ)
    (pΩ pz : ℝ) (hp : ∀ i ∈ s, p i ≠ 0) (hpΩ : pΩ ≠ 0) (hpz : pz ≠ 0)
    (hprice : pΩ ^ 3 * ∑ i ∈ s, w i / (p i) ^ 2 = ∑ i ∈ s, w i * p i) :
    ∑ i ∈ s, w i * traderF (pz / p i)
      = ((∑ i ∈ s, w i * p i) / pΩ) * traderF (pz / pΩ) := by
  have expand : ∀ i ∈ s, w i * traderF (pz / p i)
      = pz ^ 2 * (w i / (p i) ^ 2) - (w i * p i) / pz := by
    intro i hi
    have := hp i hi
    unfold traderF
    field_simp
  have lhs_eq : ∑ i ∈ s, w i * traderF (pz / p i)
      = pz ^ 2 * (∑ i ∈ s, w i / (p i) ^ 2) - (∑ i ∈ s, w i * p i) / pz := by
    rw [Finset.sum_congr rfl expand, Finset.sum_sub_distrib,
        Finset.mul_sum, Finset.sum_div]
  have hS : (∑ i ∈ s, w i / (p i) ^ 2) = (∑ i ∈ s, w i * p i) / pΩ ^ 3 := by
    field_simp; linear_combination hprice
  rw [lhs_eq, hS]
  unfold traderF
  field_simp

/-- **The slope at equilibrium is 3.** `f'(1) = 3` — the factor relating
the weight to the angle of the degree of confidence, `tan θ = 3w`,
Eq. (5). -/
theorem traderF_slope_at_one : HasDerivAt traderF 3 1 := by
  have h : HasDerivAt (fun x : ℝ => x ^ 2 - x⁻¹)
      (2 * (1 : ℝ) ^ 1 - -(((1 : ℝ) ^ 2)⁻¹)) 1 :=
    (hasDerivAt_pow 2 1).sub (hasDerivAt_inv one_ne_zero)
  have hfun : traderF = fun x : ℝ => x ^ 2 - x⁻¹ := by
    funext x; simp [traderF, one_div]
  norm_num at h
  rw [hfun]
  exact h


/-- **The trader function is strictly increasing on (0, ∞)** — principle 7
(*urgency grows with the gap*). -/
theorem traderF_strictMonoOn : StrictMonoOn traderF (Set.Ioi 0) := by
  intro x hx y hy hxy
  simp only [Set.mem_Ioi] at hx hy
  unfold traderF
  have h1 : x ^ 2 < y ^ 2 := by nlinarith
  have h2 : 1 / y < 1 / x := one_div_lt_one_div_of_lt hx hxy
  linarith

/-- **Uniqueness of the market price.** Conditions of Annex 7.7: strictly
positive estimates, nonnegative weights, at least one strictly positive
weight. Two strictly positive probe prices that both clear the market are
equal. -/
theorem market_price_unique {ι : Type*} (s : Finset ι) (p w : ι → ℝ)
    (hp : ∀ i ∈ s, 0 < p i) (hw : ∀ i ∈ s, 0 ≤ w i)
    (j : ι) (hj : j ∈ s) (hwj : 0 < w j)
    (pz₁ pz₂ : ℝ) (hpz₁ : 0 < pz₁) (hpz₂ : 0 < pz₂)
    (hclear₁ : ∑ i ∈ s, w i * traderF (pz₁ / p i) = 0)
    (hclear₂ : ∑ i ∈ s, w i * traderF (pz₂ / p i) = 0) : pz₁ = pz₂ := by
  have mono : StrictMonoOn (fun z => ∑ i ∈ s, w i * traderF (z / p i))
      (Set.Ioi 0) := by
    intro a ha b hb hab
    simp only [Set.mem_Ioi] at ha hb
    apply Finset.sum_lt_sum
    · intro i hi
      have hpi := hp i hi
      have hdiv : a / p i < b / p i := by gcongr
      have hmem₁ : a / p i ∈ Set.Ioi (0:ℝ) := Set.mem_Ioi.mpr (div_pos ha hpi)
      have hmem₂ : b / p i ∈ Set.Ioi (0:ℝ) := Set.mem_Ioi.mpr (div_pos hb hpi)
      exact mul_le_mul_of_nonneg_left
        (traderF_strictMonoOn hmem₁ hmem₂ hdiv).le (hw i hi)
    · refine ⟨j, hj, ?_⟩
      have hpj := hp j hj
      have hdiv : a / p j < b / p j := by gcongr
      have hmem₁ : a / p j ∈ Set.Ioi (0:ℝ) := Set.mem_Ioi.mpr (div_pos ha hpj)
      have hmem₂ : b / p j ∈ Set.Ioi (0:ℝ) := Set.mem_Ioi.mpr (div_pos hb hpj)
      exact mul_lt_mul_of_pos_left (traderF_strictMonoOn hmem₁ hmem₂ hdiv) hwj
  exact mono.injOn (Set.mem_Ioi.mpr hpz₁) (Set.mem_Ioi.mpr hpz₂)
    (hclear₁.trans hclear₂.symm)

end
