# -*- coding: utf-8 -*-
"""Раздел 12 (v13): камень — обойма снаружи кулисы, кулиса — сплошная полоса b × h.
Опасные положения → эпюры на истинном положении звена → σ = |N|/A + |M|/W ≤ [σ] (лист: b известна, h из уравнения) →
шток — прочность и устойчивость (критическая сила по Эйлеру / Ясинскому, перебор по ГОСТ 2590-2006) → материал → массы.
Результаты → strength_v13.json."""
import json, os
import numpy as np
from math import pi, tan, atan, sin, cos, radians as rad, degrees as deg, log, sqrt

OUT = os.path.dirname(os.path.abspath(__file__))
R = {}
e, psi, S, Sob, L = 12.53, 36.75, 16.0, 6.0, 500.0
sig_cap, kk, Dk, Dobzh, s_j, n_f, E_cap = 415.0, 1.05, 32.10, 28.6, 0.22, 2.0, 2.1e5

def bisect(g, a, b, it=200):
    ga = g(a)
    for _ in range(it):
        m = 0.5 * (a + b); gm = g(m)
        if ga * gm <= 0: b = m
        else: a, ga = m, gm
    return 0.5 * (a + b)

phi_k = bisect(lambda pk: S / (tan(rad(pk + psi)) - tan(rad(pk))) - e, 0.0, 60.0 - psi)
phi_n = phi_k + psi
A_pr = n_f * pi * (Dobzh - s_j) * s_j * log(Dk / Dobzh)
F_t, F_max = sig_cap * A_pr, kk * sig_cap * A_pr
d_y = (sig_cap / E_cap) * Dk / 2 / (((Dk - Dobzh) / 2) / Sob)
phi_ob = deg(atan(tan(rad(phi_k)) + Sob / e))
phi_y = deg(atan(tan(rad(phi_k)) + (Sob - d_y) / e))
C_el, k_h = F_t / d_y, (F_max - F_t) / (Sob - d_y)

def Fphi(phi):
    if phi > phi_ob: return 0.0
    dl = e * (tan(rad(phi_ob)) - tan(rad(phi)))
    return C_el * dl if dl <= d_y else F_t + k_h * (dl - d_y)

def loads(phi):
    F = Fphi(phi); p = rad(phi); c, s = cos(p), sin(p)
    P = F * e / (L * c ** 3) if F > 0 else 0.0
    d = dict(phi=phi, F=F, P=P, R10x=F * tan(p), R10y=P - F, R12N=F / c, R30N=-F * tan(p), lOD=e / c)
    d["R10"] = float(np.hypot(d["R10x"], d["R10y"]))
    d["N"] = -P * s; d["Q_OD"] = P * c - F / c; d["Q_DK"] = P * c; d["M_D"] = d["Q_OD"] * d["lOD"]
    return d

lmin, lmax = e / cos(rad(phi_k)), e / cos(rad(phi_n))
R["mech"] = dict(phi_n=phi_n, phi_k=phi_k, phi_y=phi_y, lOD_min=lmin, lOD_max=lmax)
phs = np.linspace(phi_k, phi_ob, 40001)
LD = [loads(p) for p in phs]
crit = {"M_D": lambda d: abs(d["M_D"]) / 1000, "R12N": lambda d: d["R12N"], "F": lambda d: d["F"], "P": lambda d: d["P"]}
R["crit"] = {}
for k, fn in crit.items():
    v = np.array([fn(d) for d in LD]); i = int(np.argmax(v))
    R["crit"][k] = dict(phi=float(phs[i]), max=float(v[i]))
A_pos, B_pos = loads(phi_y), loads(phi_k)
R["A"], R["B"] = A_pos, B_pos

# ------------------------------------------------------------------ материалы, каталоги
MATS = [("Ст3сп", 245.0), ("35", 315.0), ("45", 355.0), ("40Х", 785.0)]
n_T = 2.5
mats = {m: dict(sig_T=sT, sig_a=sT / n_T) for m, sT in MATS}
R["mats"], R["n_T"] = mats, n_T
SHEET = [6.0, 8.0, 10.0]
BAR = [5, 5.5, 6, 6.3, 6.5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
RA20 = [10, 11, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40]
up = lambda x, ser: min(v for v in ser if v >= x - 1e-9)
rho, E = 7850e-9, 2.1e5

# ------------------------------------------------------------------ кулиса: сплошная полоса, опасное сечение под камнем
def kulisa(b, sa):
    Nh, Mh = abs(A_pos["N"]), abs(A_pos["M_D"])
    h_req = (Nh + sqrt(Nh ** 2 + 24 * sa * b * Mh)) / (2 * sa * b); h = up(h_req, RA20)
    sig = Nh / (b * h) + 6 * Mh / (b * h ** 2)
    sigB = abs(B_pos["N"]) / (b * h) + 6 * abs(B_pos["M_D"]) / (b * h ** 2)
    tau = 1.5 * abs(A_pos["Q_OD"]) / (b * h)
    I = b * h ** 3 / 12
    # прогиб конца K: опоры O и D, v'' = M/(EI), сечение постоянное
    zg = np.linspace(0, L, 50001)
    Mz = np.where(zg <= A_pos["lOD"], A_pos["Q_OD"] * zg, A_pos["Q_DK"] * (zg - L))
    th = np.concatenate([[0], np.cumsum((Mz[1:] + Mz[:-1]) / 2 * np.diff(zg))]) / (E * I)
    v0 = np.concatenate([[0], np.cumsum((th[1:] + th[:-1]) / 2 * np.diff(zg))])
    v = v0 - np.interp(A_pos["lOD"], zg, v0) * zg / A_pos["lOD"]
    m = rho * b * (h * L + pi * (h / 2) ** 2 / 2)           # полоса со скруглённым концом у оси O
    JO = rho * b * (h * L ** 3 / 3 + h ** 3 * L / 12)        # относительно оси O (кг·мм²)
    zc = (rho * b * h * L * L / 2) / m
    return dict(b=b, h_req=h_req, h=h, sig=sig, sigB=sigB, tau=tau, fK=float(abs(v[-1])),
                fK_vert=float(abs(v[-1]) * cos(rad(A_pos["phi"]))), m=m, JO=JO * 1e-6, JS=(JO - m * zc ** 2) * 1e-6, zc=zc)

R["kul_mat"] = {mn: kulisa(8.0, mats[mn]["sig_a"]) for mn in mats}
R["kul_b"] = {f"{b:g}": kulisa(b, mats["Ст3сп"]["sig_a"]) for b in SHEET}
KUL = R["kul_b"]["8"]
R["kul"] = KUL

# камень-обойма: давление на рёбра полосы
lk = 20.0
R["stone"] = dict(lk=lk, p=A_pos["R12N"] / (KUL["b"] * lk), a1=lmin - lk / 2, gap_O=lmin - lk / 2)

# ------------------------------------------------------------------ шток: прочность и устойчивость (Ст3сп)
sT, sa = 245.0, 245.0 / n_T
mu, l_rod, ny_a = 2.0, 60.0, 3.0
a_J, b_J, lam_pr = 310.0, 1.14, 100.0                        # Ясинский для Ст3; предел применимости формулы Эйлера

def rod(d):
    A = pi * d ** 2 / 4; I = pi * d ** 4 / 64; i = d / 4; lam = mu * l_rod / i
    if lam >= lam_pr:
        sk, form = pi ** 2 * E / lam ** 2, "Эйлер"
    else:
        sk, form = min(a_J - b_J * lam, sT), ("Ясинский" if a_J - b_J * lam < sT else "σт")
    Fk = sk * A
    FE = pi ** 2 * E * I / (mu * l_rod) ** 2
    return dict(d=d, A=A, lam=lam, sig=B_pos["F"] / A, sk=sk, form=form, Fk=Fk, FE=FE, ny=Fk / B_pos["F"])

R["rod_iter"] = [rod(d) for d in BAR]
ROD_W = next(r for r in R["rod_iter"] if r["sig"] <= sa and r["ny"] >= ny_a)          # по рабочей нагрузке
F_ovl = 120.0 * L * cos(rad(phi_k)) ** 3 / e
ROD = next(r for r in R["rod_iter"] if r["sig"] <= sa and r["Fk"] / F_ovl >= ny_a)   # и при перегрузке
R["rod_w"] = ROD_W
R["rod"] = ROD
R["rod_par"] = dict(mu=mu, l=l_rod, ny_a=ny_a, a=a_J, b=b_J, lam_pr=lam_pr, sig_a=sa, sT=sT, F=B_pos["F"])

# перегрузка в конце хода
Pd = 120.0; pk = rad(phi_k)
F_ov = Pd * L * cos(pk) ** 3 / e
R["overload"] = dict(F=F_ov, k=F_ov / B_pos["F"], sig_kul=KUL["sigB"] * F_ov / B_pos["F"], ny=ROD["Fk"] / F_ov)

# масса ползуна (ориентировочно)
parts3 = {"направляемая часть 24 × 40 × 16": rho * 24 * 40 * 16, f"шток Ø{ROD['d']:g} × 60": rho * pi / 4 * ROD["d"] ** 2 * 60,
          "головка Ø40 × 24": rho * pi / 4 * (40 ** 2 * 24 - 30 ** 2 * 20)}
R["m3"] = sum(parts3.values()); R["parts3"] = parts3

json.dump(R, open(os.path.join(OUT, "strength_v13.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
print({k: round(v, 2) for k, v in KUL.items()})
for mn, r in R["kul_mat"].items(): print(mn, round(r["h_req"], 2), r["h"], round(r["sig"], 1), round(r["fK"], 2), round(r["m"], 3))
for b, r in R["kul_b"].items(): print("b", b, round(r["h_req"], 2), r["h"], round(r["sig"], 1), round(r["fK"], 2), round(r["m"], 3))
for r in R["rod_iter"][:9]: print(f"d {r['d']:>4} λ {r['lam']:.0f} {r['form']:8} σкр {r['sk']:.0f} Fкр {r['Fk']:.0f} FЭ {r['FE']:.0f} n {r['ny']:.2f} σ {r['sig']:.0f}")
print("шток:", ROD["d"], "| обойма:", R["stone"], "| перегрузка:", {k: round(v, 2) for k, v in R["overload"].items()}, "| m3", round(R["m3"], 3))
