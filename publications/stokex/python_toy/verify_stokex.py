#!/usr/bin/env python3
"""Numerical verification of the claims of stokex_defensive_publication.tex.

Each test validates one equation or theorem of the paper. No dependencies.
Run with: python3 verify_stokex.py
"""
import math
import random

random.seed(20260718)  # reproducible
TOL = 1e-9


def w_of_theta(theta):          # eqFunctionW of the paper
    return math.tan(math.pi * theta / 200.0) / 3.0


def theta_of_w(w):              # inverse
    return 200.0 / math.pi * math.atan(3.0 * w)


def f(x):                       # trader function, stable form
    return (x ** 3 - 1.0) / x


def market_price(parts):        # eqMarketPrice: V = (Σ w v / Σ w v^-2)^(1/3)
    num = sum(w * v for v, w in parts)
    den = sum(w / v ** 2 for v, w in parts)
    return (num / den) ** (1.0 / 3.0)


def velocities(parts, V, R=1.0):
    """eqExchangeSymmetry / eqExchangeVelocities: the two forms (α direct, β symmetric)."""
    Xa = [w * f(V / v) * R for v, w in parts]
    Xb = [w * f((1.0 / V) / (1.0 / v)) * R * (1.0 / v) for v, w in parts]
    return Xa, Xb


def random_market(n):
    return [(10 ** random.uniform(-3, 3), w_of_theta(random.uniform(1, 99)))
            for _ in range(n)]


results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))


# --- T1: the price clears the market on both sides (eqEquilibrium, eqMarketPrice) -------------
for n in (2, 5, 50, 500):
    parts = random_market(n)
    V = market_price(parts)
    Xa, Xb = velocities(parts, V)
    check(f"T1 equilibrium of both assets (N={n})",
          abs(sum(Xa)) < TOL * sum(abs(x) for x in Xa) + TOL
          and abs(sum(Xb)) < TOL * sum(abs(x) for x in Xb) + TOL,
          f"ΣẊα={sum(Xa):.2e} ΣẊβ={sum(Xb):.2e}")

# --- T2: exchange at the market price (eqExchangeAtMarketPrice) -----------------------------
parts = random_market(30)
V = market_price(parts)
Xa, Xb = velocities(parts, V)
ok = all(abs(-xa / xb - V) < 1e-9 * V for xa, xb in zip(Xa, Xb) if abs(xb) > 1e-15)
check("T2 −Ẋα/Ẋβ = [α/β]Ω for each participant", ok)

# --- T3: uniqueness (net flow strictly increasing in V) -------------------
g = lambda z: sum(w * f(z / v) for v, w in parts)
zs = [V * 10 ** e for e in (-2, -1, -0.01, 0.01, 1, 2)]
vals = [g(z) for z in zs]
check("T3 uniqueness: net flow increasing, sign around V",
      all(a < b for a, b in zip(vals, vals[1:])) and vals[2] < 0 < vals[3])

# --- T4: the market is a participant (eqMarketBehavior, eqTotalMarketWeight) ------------------------
W1 = (1.0 / V) * sum(w * v for v, w in parts)          # eqTotalMarketWeight
W2 = V ** 2 * sum(w / v ** 2 for v, w in parts)        # eqTotalMarketWeight2
ok4 = abs(W1 - W2) < 1e-9 * W1
for _ in range(20):
    z = 10 ** random.uniform(-3, 3)
    lhs = sum(w * f(z / v) for v, w in parts)
    rhs = W1 * f(z / V)
    ok4 = ok4 and abs(lhs - rhs) < 1e-9 * (abs(lhs) + abs(rhs) + 1)
check("T4 single participant: Σwᵢf(z/vᵢ) = W_Ω f(z/V), and W₁=W₂", ok4,
      f"W_Ω={W1:.6g}, Θ_Ω={theta_of_w(W1):.4f}%")

# --- T5: the degree of confidence is an angle (Annex A) -------------------
ok5 = True
for theta in (10, 50, 75, 99):
    w = w_of_theta(theta)
    h = 1e-6
    slope = (w * f(1 + h) - w * f(1 - h)) / (2 * h)     # dy/dx at x=1
    ok5 = ok5 and abs(slope - 3 * w) < 1e-6 * (1 + 3 * w)
    ok5 = ok5 and abs(math.degrees(math.atan(3 * w)) / 90 * 100 - theta) < 1e-9
check("T5 slope at x=1 equals 3w = tan(θ); exact inverse", ok5)

# --- T6: round trip w(θ) / θ(w), bounds -----------------------------------
ok6 = all(abs(theta_of_w(w_of_theta(t)) - t) < 1e-9 for t in
          (0.0001, 1, 42, 50, 99, 99.9999)) and w_of_theta(0) == 0.0
check("T6 w↔θ inverse; w(0)=0; w(99.9999%)≈2.1e5", ok6,
      f"w_max={w_of_theta(99.9999):.4g}")

# --- T7: incremental update (Market update section) -----------------------
j = 7
v1, w1 = parts[j]
v2, w2 = 10 ** random.uniform(-3, 3), w_of_theta(random.uniform(1, 99))
num = W1 * V - w1 * v1 + w2 * v2
den = W1 * (1 / V) ** 2 - w1 * (1 / v1) ** 2 + w2 * (1 / v2) ** 2
V_inc = (num / den) ** (1.0 / 3.0)
parts2 = parts.copy(); parts2[j] = (v2, w2)
V_full = market_price(parts2)
check("T7 incremental update formula = full recomputation",
      abs(V_inc - V_full) < 1e-9 * V_full, f"V₂={V_full:.6g}")

# --- T8: analogous variance (consistent definition, ≥ 0) ------------------
sig2 = sum(w * v ** 2 for v, w in parts) / W1 - V ** 2
mean_check = abs(sum((w / W1) * v for v, w in parts) - V) < 1e-9 * V
check("T8 V = weighted mean (wᵢ/W_Ω); analogous variance ≥ 0",
      mean_check and sig2 >= 0, f"σ={math.sqrt(sig2):.4g}")

# --- T9: outer (event-driven) algorithm vs brute force --------------------
def inner(parts, na, nb):
    """Inner algorithm of the paper (ordered exclusion-reintegration)."""
    trading = [na[i] > 0 and nb[i] > 0 for i in range(len(parts))]
    checklist = [i for i in range(len(parts)) if not trading[i]]
    act = [p for i, p in enumerate(parts) if trading[i]]
    V = market_price(act) if act else 1.0
    while checklist:
        fs = {i: f(V / parts[i][0]) for i in checklist}
        imax = max(checklist, key=lambda i: abs(fs[i]))
        if (fs[imax] >= 0 and nb[imax] > 0) or (fs[imax] <= 0 and na[imax] > 0):
            trading[imax] = True
            act = [p for i, p in enumerate(parts) if trading[i]]
            V = market_price(act)
        checklist.remove(imax)
    Xa = [parts[i][1] * f(V / parts[i][0]) if trading[i] else 0.0
          for i in range(len(parts))]
    Xb = [-Xa[i] / V for i in range(len(parts))]
    return V, Xa, Xb, trading

def outer(parts, na, nb, t1):
    """Outer algorithm: jumps from event to event."""
    t = 0.0
    na, nb = na[:], nb[:]
    while True:
        V, Xa, Xb, _ = inner(parts, na, nb)
        dts = [(-na[i] / Xa[i] if Xa[i] < 0 else (-nb[i] / Xb[i] if Xb[i] < 0 else math.inf))
               for i in range(len(parts))]
        dt = min(dts)
        if t + dt > t1:
            break
        for i in range(len(parts)):
            na[i] = max(0.0, na[i] + Xa[i] * dt)
            nb[i] = max(0.0, nb[i] + Xb[i] * dt)
        t += dt
    dt = t1 - t
    for i in range(len(parts)):
        na[i] += Xa[i] * dt
        nb[i] += Xb[i] * dt
    return V, na, nb

def brute(parts, na, nb, t1, dt=2e-5):
    na, nb = na[:], nb[:]
    steps = int(t1 / dt)
    for _ in range(steps):
        V, Xa, Xb, _ = inner(parts, na, nb)
        for i in range(len(parts)):
            na[i] = max(0.0, na[i] + Xa[i] * dt)
            nb[i] = max(0.0, nb[i] + Xb[i] * dt)
    return na, nb

parts9 = [(0.5, w_of_theta(60)), (1.0, w_of_theta(50)),
          (2.0, w_of_theta(70)), (4.0, w_of_theta(30))]
na0 = [0.02, 5.0, 3.0, 0.4]      # asset A — the 1st will run dry fast
nb0 = [4.0, 0.015, 2.0, 3.0]     # asset B — the 2nd too
V_ev, na_ev, nb_ev = outer(parts9, na0, nb0, t1=1.0)
na_bf, nb_bf = brute(parts9, na0, nb0, t1=1.0)
err = max(max(abs(a - b) for a, b in zip(na_ev, na_bf)),
          max(abs(a - b) for a, b in zip(nb_ev, nb_bf)))
cons_a = abs(sum(na_ev) - sum(na0))
cons_b = abs(sum(nb_ev) - sum(nb0))
check("T9 event-driven = brute force (dt→0); conservation A and B",
      err < 5e-4 and cons_a < 1e-12 and cons_b < 1e-12,
      f"max gap={err:.1e}, ΔΣA={cons_a:.1e}, ΔΣB={cons_b:.1e}")

# --- T10: shifted form of the trader function (precision) -----------------
# Domain of the ratio x = V/vᵢ: both prices live in [1e-6, 1e6] (see T11),
# so x spans [1e-12, 1e+12] — twelve decades on each side.
from fractions import Fraction

def f_exact(x):
    q = Fraction(x)
    return q * q - 1 / q

def f_std(x):
    return x * x - 1.0 / x

def f_shifted(x):           # y = x−1; denominator x, NOT y+1
    y = x - 1.0
    return y * (y * y + 3.0 * y + 3.0) / x

def f_shifted_bad(x):       # recomposed denominator y+1: ~1e-5 error at 1e-12
    y = x - 1.0
    return y * (y * y + 3.0 * y + 3.0) / (y + 1.0)

def rel(approx, x):
    ex = f_exact(x)
    return float(abs((Fraction(approx) - ex) / ex)) if ex else abs(approx)

pts = [1.0 + s * 10.0 ** (-k) for k in range(1, 16) for s in (1, -1)]
pts += [10.0 ** k for k in range(-12, 13)]
pts += [10.0 ** random.uniform(-12, 12) for _ in range(5000)]
worst_shift = max(rel(f_shifted(x), x) for x in pts)
worst_std_near1 = max(rel(f_std(x), x) for x in pts[:30])
bad_small = rel(f_shifted_bad(1e-12), 1e-12)
check("T10 shifted form y(y²+3y+3)/x: machine precision on [1e-12, 1e12]",
      worst_shift < 5e-15 and worst_std_near1 > 1e-6 and bad_small > 1e-6,
      f"shifted max={worst_shift:.1e}; standard near 1={worst_std_near1:.1e}; "
      f"denom y+1 at x=1e-12={bad_small:.1e}")

# --- T11: the equilibrium price is bounded by the estimates ---------------
# g(z) = Σ wᵢ f(z/vᵢ) is strictly increasing, ≤ 0 at min vᵢ and ≥ 0 at
# max vᵢ: the price is therefore in [min vᵢ, max vᵢ]. With estimates bounded
# to [1e-6, 1e6], the ratio x = V/vᵢ stays within [1e-12, 1e+12].
ok11 = True
for _ in range(200):
    parts11 = [(10 ** random.uniform(-6, 6), w_of_theta(random.uniform(1, 99.9999)))
               for _ in range(random.randint(1, 40))]
    V11 = market_price(parts11)
    vs = [v for v, _ in parts11]
    ok11 = ok11 and min(vs) * (1 - 1e-9) <= V11 <= max(vs) * (1 + 1e-9)
check("T11 price ∈ [min vᵢ, max vᵢ] ⇒ ratio x ∈ [10⁻¹², 10⁺¹²]", ok11)

# --- T12: the family of admissible trader functions (annex) ---------------
# fₚ(x) = xᵖ − x^(1−p), p ≥ 1: functional equation f(1/x) = −f(x)/x
# (forced by principles 2 and 4), closed-form price with exponent 1/(2p−1),
# slope 2p−1 at x = 1. The $tôkEx is the p = 2 member.
ok12 = True
for p_exp in (1.0, 1.5, 2.0, 3.0):
    fp = lambda x, p=p_exp: x ** p - x ** (1.0 - p)
    for _ in range(50):                       # functional equation
        x = 10 ** random.uniform(-3, 3)
        ok12 = ok12 and abs(fp(1.0 / x) + fp(x) / x) < 1e-9 * (1 + abs(fp(x) / x))
    parts12 = random_market(20)               # closed-form price
    num = sum(w * v ** (p_exp - 1.0) for v, w in parts12)
    den = sum(w * v ** (-p_exp) for v, w in parts12)
    Vp = (num / den) ** (1.0 / (2.0 * p_exp - 1.0))
    flow = sum(w * fp(Vp / v) for v, w in parts12)
    scale = sum(abs(w * fp(Vp / v)) for v, w in parts12)
    ok12 = ok12 and abs(flow) < 1e-9 * (scale + 1)
    h = 1e-6                                  # slope at equilibrium
    slope = (fp(1 + h) - fp(1 - h)) / (2 * h)
    ok12 = ok12 and abs(slope - (2 * p_exp - 1)) < 1e-5 * (2 * p_exp - 1)
ok12 = ok12 and fp(1.0) == 0.0                # f(1) = 0, forced
check("T12 family fₚ(x)=xᵖ−x^(1−p): functional eq., closed-form price, slope 2p−1",
      ok12)

# --- T13: emptying time with demurrage (reference implementation) ---------
# dn/dt = Ẋ − k·n (Ẋ < 0): Δt = ln(1 − k·n₀/Ẋ)/k — the exact solution
# vanishes there, Δt is shorter than the regular case −n₀/Ẋ, and tends to it as k→0.
ok13 = True
for _ in range(100):
    k = 10 ** random.uniform(-4, 1)
    n0 = 10 ** random.uniform(-2, 2)
    Xd = -(10 ** random.uniform(-2, 2))
    dt = math.log(1.0 - k * n0 / Xd) / k
    n_dt = (n0 - Xd / k) * math.exp(-k * dt) + Xd / k     # exact solution
    ok13 = ok13 and abs(n_dt) < 1e-9 * n0 and 0 < dt <= -n0 / Xd
tiny = math.log(1.0 - 1e-12 * 5.0 / -2.0) / 1e-12
ok13 = ok13 and abs(tiny - 2.5) < 1e-3
# commutation with the min (tokRepo implementation: a single log, on the min):
# min of the logs = log of the min, since u ↦ ln(1+k·u)/k is strictly increasing
k = 0.7
us = [10 ** random.uniform(-2, 2) for _ in range(50)]     # the linear −n₀/Ẋ
ok13 = ok13 and (min(math.log1p(k * u) / k for u in us)
                 == math.log1p(k * min(us)) / k)
check("T13 Δt with demurrage: n(Δt)=0, shorter, k→0; log∘min = min∘log", ok13)

# --- report ---------------------------------------------------------------
print(f"{'TEST':<58}{'RESULT':<10}DETAIL")
for name, ok, detail in results:
    print(f"{name:<58}{'PASS' if ok else 'FAIL':<10}{detail}")
fails = [n for n, ok, _ in results if not ok]
print("\n→", "ALL PASS — the paper tells the truth." if not fails else f"FAILURES: {fails}")
