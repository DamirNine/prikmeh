# -*- coding: utf-8 -*-
"""Раздел 12, камень — ролик на пальце D: опасные положения → эпюры → σ = |N|/A + |M|/W ≤ [σ];
пруток — перебор диаметров по ГОСТ 2590-2006, лист — h из уравнения прочности; ролик — контактная прочность
по Герцу и ГОСТ 21354-87 → твёрдость рабочих поверхностей → материал; массы звеньев. Результаты → strength_r.json."""
import json, os
import numpy as np
from math import pi, tan, atan, sin, cos, radians as rad, degrees as deg, log, sqrt

OUT = os.path.dirname(os.path.abspath(__file__))
R = {}

# ------------------------------------------------------------------ механизм и нагрузки (разд. 7–11)
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
    d = dict(phi=phi, F=F, P=P, R10x=F * tan(p), R10y=P - F, R12N=F / c, R23x=-F * tan(p), R23y=F, R30N=-F * tan(p), lOD=e / c)
    d["R10"] = float(np.hypot(d["R10x"], d["R10y"])); d["R23"] = float(np.hypot(d["R23x"], d["R23y"]))
    d["N"] = -P * s; d["Q_OD"] = P * c - F / c; d["Q_DK"] = P * c; d["M_D"] = d["Q_OD"] * d["lOD"]
    return d

lmin, lmax = e / cos(rad(phi_k)), e / cos(rad(phi_n))
R["mech"] = dict(phi_n=phi_n, phi_k=phi_k, phi_ob=phi_ob, phi_y=phi_y, lOD_min=lmin, lOD_max=lmax, F_t=F_t, F_max=F_max)

# ------------------------------------------------------------------ 1. опасные положения
phs = np.linspace(phi_k, phi_ob, 40001)
LD = [loads(p) for p in phs]
crit = {
    "M_D":  lambda d: abs(d["M_D"]) / 1000, "Q_DK": lambda d: d["Q_DK"], "R12N": lambda d: d["R12N"],
    "R10":  lambda d: d["R10"], "F": lambda d: d["F"], "R30N": lambda d: abs(d["R30N"]), "P": lambda d: d["P"],
}
R["crit"] = {}
for k, fn in crit.items():
    v = np.array([fn(d) for d in LD]); i = int(np.argmax(v))
    R["crit"][k] = dict(phi=float(phs[i]), max=float(v[i]))
A_pos, B_pos = loads(phi_y), loads(phi_k)
R["A"], R["B"] = A_pos, B_pos

# ------------------------------------------------------------------ 2. каталоги, материал
SHEET = [6.0, 8.0, 10.0, 12.0]                                         # ГОСТ 19903-2015, табл. 4
BAR = [5, 5.5, 6, 6.3, 6.5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
RA20 = [10, 11, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 45, 50, 56, 63, 71, 80, 90, 100]
up = lambda x, ser: min(v for v in ser if v >= x - 1e-9)
sig_T45, n_T = 355.0, 2.5
sa, ta = sig_T45 / n_T, 0.5 * sig_T45 / n_T                            # [σ] = 142, [τ] = 71
HRC_lo, HRC_hi = 45.0, 50.0                                             # закалка ТВЧ ролика и стенок паза
HRC_m = (HRC_lo + HRC_hi) / 2
sHlim = 17 * HRC_m + 200; S_H = 1.2; sHP = sHlim / S_H                  # ГОСТ 21354-87, табл. 11, 12 (Z_N = 1)
sHPmax = 44 * HRC_m                                                     # ГОСТ 21354-87, п. 3.2.2
sHP_soft = (2 * 350 + 70) / 1.1                                         # без закалки, предельно 350 НВ
R["mat"] = dict(sig_T=sig_T45, n_T=n_T, sig_a=sa, tau_a=ta, HRC_lo=HRC_lo, HRC_hi=HRC_hi, HRC_m=HRC_m, sHlim=sHlim, S_H=S_H,
                sHP=sHP, sHPmax=sHPmax, sHP_soft=sHP_soft)

g, l_h, l_rod, mu_rod, rho, E = 1.0, 16.0, 60.0, 2.0, 7850e-9, 2.1e5
KH = 0.418                                                              # σH = 0,418·√(F·E/(l·ρ)) — сталь по стали, ν = 0,3
sigH = lambda F, l, Rr: KH * sqrt(F * E / (l * Rr))

def ff_point(span, c, F):
    """балка с заделанными концами, сосредоточенная сила F на расстоянии c от левого конца"""
    d = span - c
    MA, MB = -F * c * d ** 2 / span ** 2, -F * c ** 2 * d / span ** 2
    RA = F * d ** 2 * (span + 2 * c) / span ** 3
    Mc = MA + RA * c
    return MA, MB, Mc, RA

def wall_epure(span, c, F, n=601):
    MA, MB, Mc, RA = ff_point(span, c, F)
    x = np.linspace(0, span, n)
    return x, MA + RA * x - F * np.clip(x - c, 0, None)

def round_pass(cond):
    return next(d for d in BAR if cond(d))

def profile(z, H, h, z1, lt):
    z = np.asarray(z, float)
    return np.where(z <= z1, H, np.where(z <= z1 + lt, H + (h - H) * (z - z1) / lt, h))

def kulisa_props(b, H, h, Dr, a1, a2, dO, Dh, t, pos):
    """масса, центр масс, моменты инерции планки с пазом (скруглённые концы радиусом Dr/2) и ступицы; прогиб конца K"""
    z1 = a2 + t; lt = 2.5 * (H - h)
    dz = 0.1
    Z, Y = np.meshgrid(np.arange(-H / 2, L + dz / 2, dz), np.arange(-H / 2, H / 2 + dz / 2, dz), indexing="xy")
    hz = profile(np.clip(Z, 0, None), H, h, z1, lt)
    plate = ((Z < 0) & (Z ** 2 + Y ** 2 <= (H / 2) ** 2)) | ((Z >= 0) & (Z <= L) & (np.abs(Y) <= hz / 2))
    rr = Dr / 2; zc1, zc2 = a1 + rr, a2 - rr
    slot = ((Z >= zc1) & (Z <= zc2) & (np.abs(Y) <= rr)) | ((Z - zc1) ** 2 + Y ** 2 <= rr ** 2) | ((Z - zc2) ** 2 + Y ** 2 <= rr ** 2)
    plate &= ~slot
    dA = dz * dz; Ap = plate.sum() * dA
    m_pl = rho * b * Ap; zc_pl = Z[plate].sum() * dA / Ap
    J_pl = rho * b * (Z[plate] ** 2 + Y[plate] ** 2).sum() * dA
    m_hub = rho * pi / 4 * (Dh ** 2 - dO ** 2) * l_h; J_hub = m_hub * (Dh ** 2 + dO ** 2) / 8
    m1 = m_pl + m_hub; zc = m_pl * zc_pl / m1; JO = J_pl + J_hub
    zg = np.linspace(0, L, 50001)
    hzg = profile(zg, H, h, z1, lt)
    I = np.where((zg >= a1) & (zg <= a2), b * (H ** 3 - Dr ** 3) / 12, b * hzg ** 3 / 12)
    Mz = np.where(zg <= pos["lOD"], pos["Q_OD"] * zg, pos["Q_DK"] * (zg - L))
    kap = Mz / (E * I)
    th = np.concatenate([[0], np.cumsum((kap[1:] + kap[:-1]) / 2 * np.diff(zg))])
    v0 = np.concatenate([[0], np.cumsum((th[1:] + th[:-1]) / 2 * np.diff(zg))])
    v = v0 - np.interp(pos["lOD"], zg, v0) * zg / pos["lOD"]
    return dict(A_plate=Ap, m_plate=m_pl, m_hub=m_hub, m1=m1, zc1=zc, JO=JO * 1e-6, JS=(JO - m1 * zc ** 2) * 1e-6,
                z1=z1, lt=lt, fK=float(abs(v[-1])), fK_vert=float(abs(v[-1]) * cos(rad(pos["phi"]))))

def design(b):
    r = dict(b=b)
    # палец D — консоль, плечо до середины ролика
    aD = g + b / 2; RD = A_pos["R23"]; MDp = RD * aD
    sD = lambda d: 32 * MDp / (pi * d ** 3); tD = lambda d: 16 * RD / (3 * pi * d ** 2)
    dD = round_pass(lambda d: sD(d) <= sa and tD(d) <= ta)
    r["pinD"] = dict(R=RD, a=aD, M=MDp, d=dD, sig=sD(dD), tau=tD(dD))
    # ролик: контакт со стенкой паза по линии длиной b (толщина планки); радиус — из условия σH ≤ [σH]
    F = A_pos["R12N"]
    R_req = KH ** 2 * F * E / (b * sHP ** 2)
    Dr = up(max(2 * R_req, dD + 2 * 3.0), RA20)
    r["roller"] = dict(F=F, R_req=R_req, D_req=2 * R_req, D=Dr, sigH=sigH(F, b, Dr / 2), sigH_B=sigH(B_pos["R12N"], b, Dr / 2),
                       p_pin=RD / (dD * b), sigH_soft_D=2 * KH ** 2 * F * E / (b * sHP_soft ** 2))
    # паз (концы скруглены радиусом Dr/2) и стенка паза
    a1, a2 = lmin - Dr / 2 - g, lmax + Dr / 2 + g; span = a2 - a1
    r["slot"] = dict(a1=a1, a2=a2, span=span, w=Dr)
    # рукоять
    Nh = abs(A_pos["N"]); Mh = abs(A_pos["Q_DK"]) * (L - a2)
    h_req = (Nh + sqrt(Nh ** 2 + 24 * sa * b * Mh)) / (2 * sa * b); h = up(h_req, RA20)
    r["handle"] = dict(N=Nh, M=Mh, h_req=h_req, h=h, sig=Nh / (b * h) + 6 * Mh / (b * h ** 2))
    # сечение А–А под роликом: общий + местный изгиб стенки (сосредоточенная сила ролика)
    def sec(H, pos):
        t = (H - Dr) / 2; A = b * (H - Dr); W = b * (H ** 3 - Dr ** 3) / (6 * H)
        MA, MB, Mc, _ = ff_point(span, pos["lOD"] - a1, pos["R12N"])
        Ml = max(abs(MA), abs(MB), abs(Mc))
        sg = abs(pos["N"]) / A + abs(pos["M_D"]) / W; sl = 6 * Ml / (b * t ** 2)
        return dict(H=H, t=t, A=A, W=W, sig_N=abs(pos["N"]) / A, sig_M=abs(pos["M_D"]) / W, sig_g=sg, MA=MA, MB=MB, Mc=Mc,
                    Mloc=Ml, sig_loc=sl, sig=sg + sl, tau=1.5 * abs(pos["Q_OD"]) / A)
    H_req = bisect(lambda H: max(sec(H, A_pos)["sig"], sec(H, B_pos)["sig"]) - sa, Dr + 1.0, Dr + 90.0)
    H = up(H_req, RA20)
    r["slotsec"] = dict(H_req=H_req, H=H, A=sec(H, A_pos), B=sec(H, B_pos))
    # ось O
    aO = g + l_h + b / 2; RO = A_pos["R10"]; MOp = RO * aO
    sO = lambda d: 32 * MOp / (pi * d ** 3); tO = lambda d: 16 * RO / (3 * pi * d ** 2)
    dO = round_pass(lambda d: sO(d) <= sa and tO(d) <= ta)
    Dh = up(2 * dO, RA20)
    r["axO"] = dict(R=RO, a=aO, M=MOp, d=dO, sig=sO(dO), tau=tO(dO), Dh=Dh, lh=l_h, p=RO / (dO * l_h))
    # шток
    Fr = B_pos["F"]
    d_str = round_pass(lambda d: 4 * Fr / (pi * d ** 2) <= sa)
    d_rod = round_pass(lambda d: 4 * Fr / (pi * d ** 2) <= sa and mu_rod * l_rod / (d / 4) <= 40 + 1e-9)
    r["rod"] = dict(F=Fr, d_strength=d_str, sig_strength=4 * Fr / (pi * d_str ** 2), lam_strength=mu_rod * l_rod / (d_str / 4),
                    d=d_rod, sig=4 * Fr / (pi * d_rod ** 2), lam=mu_rod * l_rod / (d_rod / 4))
    r["kul"] = kulisa_props(b, H, h, Dr, a1, a2, dO, Dh, r["slotsec"]["A"]["t"], A_pos)
    return r

VAR = {f"{b:g}": design(b) for b in SHEET}
R["var"] = VAR
b_sel = 12.0
FIN = VAR[f"{b_sel:g}"]
R["fin"] = FIN

# проверки принятых размеров в положении φк и при перегрузке
fz = FIN
R["fin_check"] = {
    "handle_B": abs(B_pos["N"]) / (b_sel * fz["handle"]["h"]) + 6 * abs(B_pos["Q_DK"]) * (L - fz["slot"]["a2"]) / (b_sel * fz["handle"]["h"] ** 2),
    "pinD_B": 32 * B_pos["R23"] * fz["pinD"]["a"] / (pi * fz["pinD"]["d"] ** 3),
    "axO_B": 32 * B_pos["R10"] * fz["axO"]["a"] / (pi * fz["axO"]["d"] ** 3),
}
xw, Mw = wall_epure(fz["slot"]["span"], A_pos["lOD"] - fz["slot"]["a1"], A_pos["R12N"])
R["wall_epure"] = dict(x=xw.tolist(), M=Mw.tolist())

Pd = 120.0; pk = rad(phi_k)
F_ov = Pd * L * cos(pk) ** 3 / e
ov = dict(P=Pd, F=F_ov, R12N=F_ov / cos(pk), k_F=F_ov / B_pos["F"])
sB = dict(handle=R["fin_check"]["handle_B"], slot=FIN["slotsec"]["B"]["sig"], pinD=R["fin_check"]["pinD_B"],
          axO=R["fin_check"]["axO_B"], rod=FIN["rod"]["sig"])
ov["sig"] = {k: v * ov["k_F"] for k, v in sB.items()}
ov["sigH"] = sigH(ov["R12N"], b_sel, FIN["roller"]["D"] / 2)
R["overload"] = ov

# массы звеньев 2 и 3
dD_, Dr_ = fz["pinD"]["d"], fz["roller"]["D"]
m2 = rho * b_sel * pi / 4 * (Dr_ ** 2 - dD_ ** 2)
JS2 = m2 * (Dr_ ** 2 + dD_ ** 2) / 8
blk = (24.0, 40.0, 16.0)
parts3 = {"направляемая часть 24 × 40 × 16": rho * blk[0] * blk[1] * blk[2],
          f"палец D Ø{dD_:g} × {blk[2] + g + b_sel:g}": rho * pi / 4 * dD_ ** 2 * (blk[2] + g + b_sel),
          f"шток Ø{fz['rod']['d']:g} × {l_rod:g}": rho * pi / 4 * fz["rod"]["d"] ** 2 * l_rod,
          "головка Ø40 × 24": rho * pi / 4 * (40 ** 2 * 24 - 30 ** 2 * 20)}
R["mass23"] = dict(m2=m2, JS2=JS2 * 1e-6, parts3=parts3, m3=sum(parts3.values()))

# перебор диаметров (b = b_sel) и перебор диаметров ролика
aD, aO = g + b_sel / 2, g + l_h + b_sel / 2
R["iter_bar"] = [dict(d=d, sigD=32 * A_pos["R23"] * aD / (pi * d ** 3), sigO=32 * A_pos["R10"] * aO / (pi * d ** 3),
                      sigR=4 * B_pos["F"] / (pi * d ** 2), lam=mu_rod * l_rod / (d / 4)) for d in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]]
R["iter_roller"] = [dict(D=D, sigH=sigH(A_pos["R12N"], b_sel, D / 2)) for D in [16, 18, 20, 22, 25, 28]]
R["aD"], R["aO"], R["b_sel"] = aD, aO, b_sel

json.dump(R, open(os.path.join(OUT, "strength_r.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)

pr = print
pr(f"[σ] {sa}, [τ] {ta}; ТВЧ HRC {HRC_lo:g}…{HRC_hi:g}: σHlim {sHlim:.1f}, [σH] {sHP:.1f}, σHPmax {sHPmax:.0f}; без закалки [σH] ≤ {sHP_soft:.0f}")
for k, v in R["crit"].items():
    pr(f"  {k}: {v['max']:.2f} при φ = {v['phi']:.3f}")
for k, r in VAR.items():
    rl, ss, hd, kl = r["roller"], r["slotsec"], r["handle"], r["kul"]
    pr(f"b={k:>2}: D Ø{r['pinD']['d']:g} (σ {r['pinD']['sig']:.0f}) | ролик Dтреб {rl['D_req']:.1f} → Ø{rl['D']:g} σH {rl['sigH']:.0f} "
       f"(без закалки нужен Ø{rl['sigH_soft_D']:.0f}) p {rl['p_pin']:.1f} | h {hd['h_req']:.2f}→{hd['h']} | H {ss['H_req']:.2f}→{ss['H']} "
       f"(t {ss['A']['t']:.1f}; σг {ss['A']['sig_g']:.1f} σм {ss['A']['sig_loc']:.1f} Σ {ss['A']['sig']:.1f}; B Σ {ss['B']['sig']:.1f}; "
       f"M {ss['A']['MA']/1000:.2f}/{ss['A']['MB']/1000:.2f}/{ss['A']['Mc']/1000:.2f}) | O Ø{r['axO']['d']:g} (σ {r['axO']['sig']:.0f}) "
       f"Ø{r['axO']['Dh']} | m1 {kl['m1']:.3f} fK {kl['fK']:.2f} | паз {r['slot']['a1']:.2f}…{r['slot']['a2']:.2f} ℓ {r['slot']['span']:.2f}")
pr("φк:", {k: round(v, 1) for k, v in R["fin_check"].items()})
pr("перегрузка:", round(ov["F"], 1), round(ov["k_F"], 3), {k: round(v, 1) for k, v in ov["sig"].items()}, "σH", round(ov["sigH"], 0))
pr("массы:", {k: round(v, 4) for k, v in FIN["kul"].items()}, "m2", round(m2, 4), "JS2", JS2 * 1e-6, "m3", round(R["mass23"]["m3"], 3))
pr("ролики (b = 12):", [(x["D"], round(x["sigH"], 0)) for x in R["iter_roller"]])
