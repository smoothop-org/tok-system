#!/usr/bin/env python3
"""A toy implementation of the $tôkEx, with asset A and asset B accounts.

A complete, runnable market, written **from the defensive publication**
(`stokex_defensive_publication.tex`) and from nothing else: every function
points at the equation or the section it realizes. It is not a copy of the tôk
system backend --- it is what the disclosure lets anyone rewrite from the
document alone, which is also the best evidence that the disclosure is
*enabling* in the prior-art sense.

What the toy does:
  - the trader function (2), evaluated in the shifted form (4);
  - the weight function (5);
  - the closed-form market price (14);
  - the exchange velocities (6) and the emptying times (8);
  - the inner algorithm (Sec. 4.1): exclusion, price, sorted reintegration;
  - the outer algorithm (Sec. 4.2): exact stepping, event by event.

What the toy does not do, deliberately:
  - no compensated (Kahan) summation, no extended precision;
  - no disintegration: both assets are assumed to have no dynamics of their
    own, the document's default assumption (Sec. 2);
  - no bounds on estimates, no discretization of the degree of confidence.
  Sec. 4.3 describes those refinements; they add nothing to an understanding
  of the mechanism, which is the point here.

No dependencies. Run with: python3 stokex_toy.py
"""
import math

TOL = 1e-12          # solvency threshold: below it, an account counts as empty
DEFAULT_PRICE = 1.0  # price of an empty market (Sec. 4.3)


# ----------------------------------------------------------------------
# The two functions of the mechanism
# ----------------------------------------------------------------------

def weight_of_degree(theta):
    """(5) — w(θ) = tan(π θ / 200 %) / 3, with θ in percent, in [0, 100)."""
    if theta <= 0.0:
        return 0.0
    if theta >= 100.0:
        raise ValueError("the degree of confidence is bounded to [0, 100) % — see Annex 7.9")
    return math.tan(math.pi * theta / 200.0) / 3.0


def degree_of_weight(w):
    """Inverse of (5), which also gives the market's aggregate degree (19)."""
    return 200.0 / math.pi * math.atan(3.0 * w)


def trader_f(x):
    """(2) — f(x) = x² − 1/x, evaluated in the shifted form (4).

    The typical operating point is x ≈ 1, exactly where x² − 1/x loses half its
    significand to catastrophic cancellation. Setting y = x − 1 (exact on
    [1/2, 2] by Sterbenz's lemma) gives x³ − 1 = y³ + 3y² + 3y, so the
    numerator tracks the small deviation y without cancellation. The
    denominator must be **x itself**, not y + 1.
    """
    y = x - 1.0
    return y * (y * y + 3.0 * y + 3.0) / x


# ----------------------------------------------------------------------
# The participants
# ----------------------------------------------------------------------

class Participant:
    """A participant: two declarations, two accounts.

    The participant declares an estimate [α/β]_i and a degree of confidence
    θ_i; it is their trading robot that executes, by producing the two
    exchange velocities.
    """

    def __init__(self, name, estimate, degree, n_alpha, n_beta):
        if estimate <= 0.0:
            raise ValueError("an estimate is strictly positive")
        self.name = name
        self.estimate = float(estimate)   # [α/β]_i
        self.degree = float(degree)       # θ_i, in %
        self.weight = weight_of_degree(degree)   # w_i, computed once
        self.n_alpha = float(n_alpha)
        self.n_beta = float(n_beta)
        # filled in by the inner algorithm
        self.trading = False
        self.vel_alpha = 0.0              # Ẋ_i^α
        self.vel_beta = 0.0               # Ẋ_i^β
        self.dt_empty = math.inf          # Δt_i

    def __repr__(self):
        return (f"{self.name}: [α/β]={self.estimate:.4f} θ={self.degree:g}% "
                f"α={self.n_alpha:.4f} β={self.n_beta:.4f}")


# ----------------------------------------------------------------------
# The market
# ----------------------------------------------------------------------

class Market:
    """The $tôkEx for one pair of assets A/B, with its reference velocity Ṙ."""

    def __init__(self, participants, reference_velocity=1.0):
        self.participants = list(participants)
        self.R = float(reference_velocity)      # Ṙ, in α per unit of time
        self.price = DEFAULT_PRICE               # [α/β]_Ω
        self._sum_wv = 0.0                       # Σ w_i [α/β]_i
        self._sum_w_inv_v2 = 0.0                 # Σ w_i [β/α]_i²

    # -- price ----------------------------------------------------------

    def _reset_sums(self):
        self._sum_wv = 0.0
        self._sum_w_inv_v2 = 0.0

    def _accumulate(self, p):
        """Add one participant to the two sums of (14). Costs O(1)."""
        self._sum_wv += p.weight * p.estimate
        self._sum_w_inv_v2 += p.weight / (p.estimate * p.estimate)

    def _price_from_sums(self):
        """(14) — [α/β]_Ω = (Σ w [α/β] / Σ w [β/α]²)^(1/3)."""
        if self._sum_w_inv_v2 <= 0.0:      # empty market: nobody can trade
            return DEFAULT_PRICE
        return (self._sum_wv / self._sum_w_inv_v2) ** (1.0 / 3.0)

    @property
    def total_weight(self):
        """(17) — W_Ω = [β/α]_Ω Σ w_i [α/β]_i, the stiffness of the market."""
        return self._sum_wv / self.price

    @property
    def total_degree(self):
        """(19) — Θ_Ω, the market's aggregate degree of confidence."""
        return degree_of_weight(self.total_weight)

    # -- inner algorithm (Sec. 4.1) -------------------------------------

    def inner(self):
        """Compute price, velocities and emptying times at the current instant.

        A participant with an empty account is excluded, then possibly
        reintegrated if they hold the asset they wish to sell. The order of
        reintegration is not free: always handle the one **farthest** from the
        price, in the sense of |f_i^α|. Since f is monotone in the estimate,
        that farthest one always sits at one of the two ends of the sorted
        checklist --- hence two examinations per round, and a total cost of
        O(N log N) dominated by the sort.
        """
        checklist = []
        self._reset_sums()

        for p in self.participants:
            p.trading = True
            if p.weight == 0.0:                      # no conviction, no trade
                p.trading = False
                continue
            if p.n_alpha <= TOL or p.n_beta <= TOL:
                p.trading = False
                checklist.append(p)
            else:
                self._accumulate(p)
        self.price = self._price_from_sums()

        # reintegrations, from the farthest from the price to the nearest
        checklist.sort(key=lambda q: q.estimate)
        while checklist:
            f_low = trader_f(self.price / checklist[0].estimate)
            f_high = trader_f(self.price / checklist[-1].estimate)
            far = checklist.pop(0 if abs(f_low) >= abs(f_high) else -1)
            f_far = f_low if abs(f_low) >= abs(f_high) else f_high
            # f ≥ 0: the market is above the estimate, the participant sells β
            # f ≤ 0: the market is below it, the participant sells α
            if (f_far >= 0.0 and far.n_beta > TOL) or (f_far <= 0.0 and far.n_alpha > TOL):
                far.trading = True
                self._accumulate(far)                # incremental update, O(1)
                self.price = self._price_from_sums()

        # velocities (6) and emptying times (8)
        for p in self.participants:
            if p.trading:
                x = self.price / p.estimate
                p.vel_alpha = p.weight * trader_f(x) * self.R
                # symmetric form: f([β/α]_Ω / [β/α]_i) Ṙ [β/α]_i
                p.vel_beta = p.weight * trader_f(1.0 / x) * self.R / p.estimate
            else:
                p.vel_alpha = 0.0
                p.vel_beta = 0.0
            p.dt_empty = self._emptying_time(p)

        return self.price

    @staticmethod
    def _emptying_time(p):
        """(8)–(9) — Δt_i = min(Δt_i^α, Δt_i^β), with the +∞ convention.

        Only the account of a sold asset ever empties. The +∞ is what lets the
        minimum select the right account: without it, the negative raw ratio of
        the bought account would spuriously win.
        """
        dt_a = -p.n_alpha / p.vel_alpha if p.vel_alpha < 0.0 else math.inf
        dt_b = -p.n_beta / p.vel_beta if p.vel_beta < 0.0 else math.inf
        return min(dt_a, dt_b)

    # -- outer algorithm (Sec. 4.2) -------------------------------------

    def advance(self, duration, trace=None):
        """Advance the market by `duration`, exactly, event by event.

        The state is constant between two events, so each balance evolves
        linearly: no arbitrary time step, no accumulated error.
        """
        t = 0.0
        self.inner()
        while True:
            dt = min((p.dt_empty for p in self.participants), default=math.inf)
            if duration - t < dt:
                break
            self._step(dt)
            t += dt
            before = self.price
            self.inner()             # the price moves: someone just dropped out
            if trace is not None:
                trace.append((t, before, self.price))
        self._step(duration - t)
        return self.price

    def _step(self, dt):
        if dt == 0.0:
            return
        for p in self.participants:
            p.n_alpha += p.vel_alpha * dt
            p.n_beta += p.vel_beta * dt
            if p.n_alpha < 0.0:      # catch the rounding of the exact step
                p.n_alpha = 0.0
            if p.n_beta < 0.0:
                p.n_beta = 0.0

    # -- reading --------------------------------------------------------

    def totals(self):
        """The two sums the mechanism conserves (principle 1)."""
        return (sum(p.n_alpha for p in self.participants),
                sum(p.n_beta for p in self.participants))


# ----------------------------------------------------------------------
# Demonstration and checks
# ----------------------------------------------------------------------

def _demo():
    market = Market([
        Participant("Alice",  estimate=2.00, degree=75.0, n_alpha=100.0, n_beta=50.0),
        Participant("Bob",    estimate=1.00, degree=50.0, n_alpha=80.0,  n_beta=80.0),
        Participant("Carol",  estimate=3.50, degree=90.0, n_alpha=10.0,  n_beta=200.0),
        Participant("Dan",    estimate=1.50, degree=0.0,  n_alpha=40.0,  n_beta=40.0),
    ], reference_velocity=1.0)

    a0, b0 = market.totals()
    market.inner()

    print("=== initial state ===")
    print(f"market price [α/β]_Ω = {market.price:.6f} α per β")
    print(f"total weight W_Ω = {market.total_weight:.6f}  (aggregate degree Θ_Ω = {market.total_degree:.3f} %)")
    print()
    print(f"{'participant':<8} {'estimate':>10} {'θ':>7} {'Ẋ^α':>12} {'Ẋ^β':>12} {'Δt':>10}")
    for p in market.participants:
        dt = "∞" if p.dt_empty == math.inf else f"{p.dt_empty:.3f}"
        print(f"{p.name:<8} {p.estimate:>10.4f} {p.degree:>6g}% "
              f"{p.vel_alpha:>12.6f} {p.vel_beta:>12.6f} {dt:>10}")

    # -- the paper's invariants, checked on this state ------------------
    print("\n=== checks ===")

    net_a = sum(p.vel_alpha for p in market.participants)
    net_b = sum(p.vel_beta for p in market.participants)
    print(f"(13) equilibrium    : ΣẊ^α = {net_a:.3e}, ΣẊ^β = {net_b:.3e}")
    assert abs(net_a) < 1e-9 and abs(net_b) < 1e-9

    worst = max((abs(-p.vel_alpha / p.vel_beta - market.price)
                 for p in market.participants if p.trading and p.vel_beta != 0.0),
                default=0.0)
    print(f"(7)  at the price   : max |−Ẋ^α/Ẋ^β − [α/β]_Ω| = {worst:.3e}")
    assert worst < 1e-9

    # (16) the whole market behaves as a single participant
    probe = 1.234 * market.price
    crowd = sum(p.weight * trader_f(probe / p.estimate) * market.R
                for p in market.participants if p.trading)
    single = market.total_weight * trader_f(probe / market.price) * market.R
    print(f"(16) aggregation    : |crowd − single| = {abs(crowd - single):.3e}")
    assert abs(crowd - single) < 1e-9

    # bound from Annex 7.7: the price lies between the smallest and largest estimate
    trading = [p.estimate for p in market.participants if p.trading]
    print(f"(7.7) bracketing    : {min(trading):.4f} ≤ {market.price:.4f} ≤ {max(trading):.4f}")
    assert min(trading) <= market.price <= max(trading)

    # -- let the market run ---------------------------------------------
    print("\n=== 60 units of time later ===")
    trace = []
    market.advance(60.0, trace)
    for t, before, after in trace:
        print(f"  t = {t:9.4f}   an account empties: "
              f"[α/β]_Ω moves from {before:.6f} to {after:.6f}")
    print(f"  t = {60.0:9.4f}   end, [α/β]_Ω = {market.price:.6f}")

    print()
    for p in market.participants:
        print(f"  {p}")

    a1, b1 = market.totals()
    print(f"\n(13) conservation   : Δ(Σn^α) = {a1 - a0:.3e}, Δ(Σn^β) = {b1 - b0:.3e}")
    assert abs(a1 - a0) < 1e-9 and abs(b1 - b0) < 1e-9

    print("\nAll checks pass.")


if __name__ == "__main__":
    _demo()
