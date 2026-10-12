# -*- coding: utf-8 -*-
"""Раздел 12 (v10) — прочностной расчёт звеньев по образцу курсового РК6-54Б (лесопильная рама) и семинара 12:
положения φу, φк → эпюры N, Q, M кулисы → шарниры и камень → подбор сечения кулисы кодом по ГОСТ 6636-69 →
рукоять h(z) → ползун → компоновка у оси O → массы и моменты инерции. Результаты → strength_v10.json."""
import json, os
import numpy as np
from math import pi, tan, atan, sin, cos, radians as rad, degrees as deg, log, sqrt

OUT = os.path.dirname(os.path.abspath(__file__))
R = {}                                      # всё, что пойдёт в документ

# ------------------------------------------------------------------ механизм (как в разд. 7–11)
e, psi, S, Sob, L = 12.53, 36.75, 16.0, 6.0, 500.0
sig_t, kk, Dk, Dobzh, s_j, n_f, Eel = 415.0, 1.05, 32.10, 28.6, 0.22, 2.0, 2.1e5

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
F_t, F_max = sig_t * A_pr, kk * sig_t * A_pr
d_y = (sig_t / Eel) * Dk / 2 / (((Dk - Dobzh) / 2) / Sob)
phi_ob = deg(atan(tan(rad(phi_k)) + Sob / e))
phi_y = deg(atan(tan(rad(phi_k)) + (Sob - d_y) / e))
C_el, k_h = F_t / d_y, (F_max - F_t) / (Sob - d_y)

def Fphi(phi):
    if phi > phi_ob: return 0.0
    dl = e * (tan(rad(phi_ob)) - tan(rad(phi)))
    return C_el * dl if dl <= d_y else F_t + k_h * (dl - d_y)

def loads(phi):
    F = Fphi(phi); p = rad(phi); c, s = cos(p), sin(p)
    P = F * e / (L * c ** 3)
    d = dict(phi=phi, F=F, P=P, R10x=F * tan(p), R10y=P - F, R12N=F / c, R23x=-F * tan(p), R23y=F, R30N=-F * tan(p), lOD=e / c)
    d["R10"] = float(np.hypot(d["R10x"], d["R10y"])); d["R23"] = float(np.hypot(d["R23x"], d["R23y"]))
    # проекции на ось звена u = (cos φ, sin φ) и нормаль n = (−sin φ, cos φ)
    d["N"] = -P * s                              # продольная сила (растяжение +) — по всей длине
    d["Q_OD"] = P * c - F / c                    # поперечная сила на участке O–D (по силам левее сечения)
    d["Q_DK"] = P * c                            # на участке D–K
    d["M_D"] = d["Q_OD"] * d["lOD"]              # изгибающий момент у камня, Н·мм (по силам левее)
    return d

A_pos, B_pos = loads(phi_y), loads(phi_k)
R["mech"] = dict(phi_n=phi_n, phi_k=phi_k, phi_ob=phi_ob, phi_y=phi_y, lOD_min=e / cos(rad(phi_k)), lOD_max=e / cos(rad(phi_n)))
R["A"], R["B"] = A_pos, B_pos
# |M_D| по всему рабочему ходу — подтверждение выбора положения
phs = np.linspace(phi_k, phi_ob, 20001)
MD = np.array([abs(loads(p)["M_D"]) for p in phs]); QD = np.array([abs(loads(p)["Q_OD"]) for p in phs])
R["MD_max_phi"], R["MD_max"] = float(phs[np.argmax(MD)]), float(MD.max())
R["QD_max_phi"], R["QD_max"] = float(phs[np.argmax(QD)]), float(QD.max())

# ------------------------------------------------------------------ материал и допускаемые
sig_T, sig_B, E, rho = 355.0, 600.0, 2.1e5, 7850e-9          # МПа, МПа, МПа, кг/мм³
n_T = 2.5
sig_a = sig_T / n_T; tau_a = 0.6 * sig_a; p_a = 30.0
R["mat"] = dict(sig_T=sig_T, sig_B=sig_B, n_T=n_T, sig_a=sig_a, tau_a=tau_a, p_a=p_a)

RA10 = [10, 12, 16, 20, 25, 32, 40, 50]
RA20 = [10, 11, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 45, 50]
RA40 = [10, 10.5, 11, 11.5, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 28, 30, 32, 34, 36, 38, 40, 42, 45, 48, 50]
up = lambda x, ser: min(v for v in ser if v >= x - 1e-9)

# ------------------------------------------------------------------ шарниры, камень
b, g, sw = 10.0, 1.0, 3.0            # толщина планки и камня; зазор между слоями; стенка камня вокруг пальца
Rd = A_pos["R23"]                    # палец D: |R23| = R12N в положении φу
armD = g + b / 2
d_req_D = dict(shear=sqrt(4 * Rd / (pi * tau_a)), bend=(Rd * armD / (0.1 * sig_a)) ** (1 / 3), bear=Rd / (b * p_a))
dD = up(max(d_req_D.values()), RA10)
w = up(dD + 2 * sw, RA20)            # ширина камня = ширина паза
ls = w                               # длина камня вдоль паза
dlt3 = 12.0                          # толщина проушины ползуна под палец D
pinD = dict(R=Rd, arm=armD, M=Rd * armD, d_req=d_req_D, d=dD, sig=Rd * armD / (0.1 * dD ** 3), tau=4 * Rd / (pi * dD ** 2),
            p_stone=Rd / (dD * b), p_lug=Rd / (dD * dlt3), lug_D=24.0, sig_lug=Rd / ((24.0 - dD) * dlt3))
stone = dict(w=w, ls=ls, b=b, p=A_pos["R12N"] / (ls * b))
Ro = A_pos["R10"]                    # ось O
# вариант 1: всё в одной плоскости, ось консольно из стойки через бобышку планки
arm1 = g + b / 2
dO1 = up((Ro * arm1 / (0.1 * sig_a)) ** (1 / 3), RA10); rb1 = dO1 / 2 + 3.0
# вариант 2 (принят): ступица позади планки, планка с пазом — перед ступицей
lh = 16.0
arm2 = g + lh + b / 2
dO2 = up((Ro * arm2 / (0.1 * sig_a)) ** (1 / 3), RA10); Dh = 2 * dO2
axO = dict(R=Ro, arm1=arm1, d1=dO1, rb1=rb1, sig1=Ro * arm1 / (0.1 * dO1 ** 3),
           arm2=arm2, d2=dO2, Dh=Dh, lh=lh, sig2=Ro * arm2 / (0.1 * dO2 ** 3), tau2=4 * Ro / (pi * dO2 ** 2), p2=Ro / (dO2 * lh),
           d2_req=(Ro * arm2 / (0.1 * sig_a)) ** (1 / 3), d1_req=(Ro * arm1 / (0.1 * sig_a)) ** (1 / 3))
R["pinD"], R["stone"], R["axO"] = pinD, stone, axO

# ------------------------------------------------------------------ компоновка у оси O
lmin, lmax = R["mech"]["lOD_min"], R["mech"]["lOD_max"]
gap = 1.0
need1 = rb1 + gap + ls / 2
lay = dict(lmin=lmin, lmax=lmax, stone_inner=lmin - ls / 2, need1=need1, short1=need1 - lmin,
           overlap1=rb1 - (lmin - ls / 2), e_req1=need1 * cos(rad(phi_k)),
           a1=lmin - ls / 2 - gap, a2=lmax + ls / 2 + gap)
R["lay"] = lay
a1, a2 = lay["a1"], lay["a2"]; span = a2 - a1

# ------------------------------------------------------------------ сечение кулисы в зоне паза (код по ГОСТ 6636-69)
def fixed_fixed_Mmax(span, c, ls, P, n=4001):
    """Стенка паза — балка с заделанными концами; нагрузка P равномерно на [c − ls/2, c + ls/2]."""
    x = np.linspace(0, span, n); q = np.where(np.abs(x - c) <= ls / 2, P / ls, 0.0)
    dx = x[1] - x[0]
    MA = -np.trapezoid(q * x * (span - x) ** 2, x) / span ** 2
    MB = -np.trapezoid(q * x ** 2 * (span - x), x) / span ** 2
    RA = np.trapezoid(q * (span - x) ** 2 * (span + 2 * x), x) / span ** 3
    cumq = np.concatenate([[0], np.cumsum((q[1:] + q[:-1]) / 2 * dx)])
    cumqx = np.concatenate([[0], np.cumsum((q[1:] * x[1:] + q[:-1] * x[:-1]) / 2 * dx)])
    M = MA + RA * x - (x * cumq - cumqx)
    return float(np.max(np.abs(M))), float(MA), float(MB)

def section(H, pos):
    t = (H - w) / 2
    A = b * (H - w); W = b * (H ** 3 - w ** 3) / (6 * H)
    sg = abs(pos["N"]) / A + abs(pos["M_D"]) / W
    c = pos["lOD"] - a1
    Mloc, _, _ = fixed_fixed_Mmax(span, c, ls, pos["R12N"])
    sl = 6 * Mloc / (b * t ** 2)
    tau = 1.5 * abs(pos["Q_OD"]) / A
    return dict(H=H, t=t, A=A, W=W, sig_g=sg, Mloc=Mloc, sig_loc=sl, sig=sg + sl, tau=tau)

cand = []
for H in [h for h in RA40 if 26 <= h <= 40]:
    sa, sb = section(H, A_pos), section(H, B_pos)
    ser = "Ra10" if H in RA10 else ("Ra20" if H in RA20 else "Ra40")
    cand.append(dict(H=H, ser=ser, A=sa, B=sb, ok=sa["sig"] <= sig_a and sb["sig"] <= sig_a))
Hsel = next(c["H"] for c in cand if c["ok"] and c["ser"] in ("Ra10", "Ra20"))
R["cand"] = cand; R["H"] = Hsel; R["secA"], R["secB"] = section(Hsel, A_pos), section(Hsel, B_pos)
R["b"], R["w"], R["span"] = b, w, span

# ------------------------------------------------------------------ рукоять: требуемая высота h(z) и принятый профиль
hr, ltap = 16.0, 100.0
zt = a2 + ltap
def h_acc(z):
    z = np.asarray(z, float)
    return np.where(z <= a2, Hsel, np.where(z <= zt, Hsel + (hr - Hsel) * (z - a2) / ltap, hr))
def M_of(z, pos):                          # |M(z)| по формулам разд. 12.2
    z = np.asarray(z, float)
    return np.where(z <= pos["lOD"], abs(pos["Q_OD"]) * z, pos["Q_DK"] * (L - z))
zz = np.linspace(a2, L, 4001)
MA_z = M_of(zz, A_pos); NA = abs(A_pos["N"])
h_req = (NA + np.sqrt(NA ** 2 + 24 * sig_a * b * MA_z)) / (2 * sig_a * b)
sig_h = NA / (b * h_acc(zz)) + 6 * MA_z / (b * h_acc(zz) ** 2)
i = int(np.argmax(sig_h))
R["handle"] = dict(hr=hr, ltap=ltap, zt=zt, h_req_a2=float(h_req[0]), h_req_zt=float(np.interp(zt, zz, h_req)),
                   sig_max=float(sig_h[i]), z_sig_max=float(zz[i]), sig_a2=float(sig_h[0]))
# прогиб конца рукояти: v'' = M/(E·I), опоры O (z = 0) и камень D (z = lOD), положение φу
zg = np.linspace(0, L, 50001)
def I_of(z):
    hh = h_acc(z); I = b * hh ** 3 / 12
    return np.where((z >= a1) & (z <= a2), b * (Hsel ** 3 - w ** 3) / 12, I)
Mz = np.where(zg <= A_pos["lOD"], A_pos["Q_OD"] * zg, A_pos["Q_DK"] * zg - A_pos["F"] * e / cos(rad(phi_y)) ** 2)
kap = Mz / (E * I_of(zg))
th = np.concatenate([[0], np.cumsum((kap[1:] + kap[:-1]) / 2 * np.diff(zg))])
v0 = np.concatenate([[0], np.cumsum((th[1:] + th[:-1]) / 2 * np.diff(zg))])      # частное решение с v(0) = 0, v'(0) = 0
vD = np.interp(A_pos["lOD"], zg, v0)
v = v0 - vD * zg / A_pos["lOD"]                                                # поворот, чтобы v(lOD) = 0
R["handle"]["vK"] = float(v[-1]); R["handle"]["vK_vert"] = float(abs(v[-1]) * cos(rad(phi_y)))
R["Mz_check"] = float(Mz[-1])

# ------------------------------------------------------------------ ползун
d3, l3, mu3 = 16.0, 60.0, 2.0
A3 = pi * d3 ** 2 / 4
R["slider"] = dict(d=d3, l=l3, mu=mu3, sig=F_max / A3, lam=mu3 * l3 / (d3 / 4), F=F_max,
                   p_guide=abs(A_pos["R30N"]) / (24.0 * dlt3), R30=abs(A_pos["R30N"]))

# ------------------------------------------------------------------ массы и моменты инерции
dz = 0.05
Z, Y = np.meshgrid(np.arange(-Hsel / 2, L + dz, dz), np.arange(-Hsel / 2, Hsel / 2 + dz, dz), indexing="xy")
hz = h_acc(np.clip(Z, 0, None))
plate = ((Z <= 0) & (Z ** 2 + Y ** 2 <= (Hsel / 2) ** 2)) | ((Z > 0) & (Z <= L) & (np.abs(Y) <= hz / 2))
slot = (Z >= a1) & (Z <= a2) & (np.abs(Y) <= w / 2)
plate &= ~slot
dA = dz * dz
Ap = plate.sum() * dA
m_pl = rho * b * Ap
zc_pl = (Z[plate].sum() * dA) / Ap
Jp = rho * b * ((Z[plate] ** 2 + Y[plate] ** 2).sum() * dA)                   # кг·мм²
m_hub = rho * pi / 4 * (Dh ** 2 - dO2 ** 2) * lh
J_hub = m_hub * ((Dh / 2) ** 2 + (dO2 / 2) ** 2) / 2
m1 = m_pl + m_hub; zc1 = m_pl * zc_pl / m1; JO1 = Jp + J_hub; JS1 = JO1 - m1 * zc1 ** 2
m2 = rho * b * (w * ls - pi * dD ** 2 / 4); JS2 = rho * b * (w * ls * (w ** 2 + ls ** 2) / 12 - pi * dD ** 4 / 32)
parts3 = {"проушина Ø24×12": (rho * (pi / 4) * (24 ** 2 - dD ** 2) * dlt3, 0.0),
          "палец D Ø12×25": (rho * (pi / 4) * dD ** 2 * 25.0, 0.0),
          "шток Ø16×60": (rho * A3 * l3, -(12 + l3 / 2)),
          "головка Ø40×24": (rho * (pi / 4) * (40 ** 2 * 24 - 30 ** 2 * 20), -(12 + l3 + 12))}
m3 = sum(m for m, _ in parts3.values()); yc3 = sum(m * y for m, y in parts3.values()) / m3
R["mass"] = dict(m_plate=m_pl, m_hub=m_hub, m1=m1, zc1=zc1, JO1=JO1 * 1e-6, JS1=JS1 * 1e-6, m2=m2, JS2=JS2 * 1e-6,
                 m3=m3, yc3=yc3, parts3={k: v[0] for k, v in parts3.items()},
                 G1=m1 * 9.81, dP_G1=m1 * 9.81 * zc1 / L, dP_J=JO1 * 1e-6 * 3.1976 / (L / 1000 * cos(rad(phi_n))))

json.dump(R, open(os.path.join(OUT, "strength_v10.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)

# ------------------------------------------------------------------ печать
pr = lambda *a: print(*a)
pr(f"окно {phi_n:.3f}→{phi_k:.3f}, φоб {phi_ob:.3f}, φу {phi_y:.4f}; lOD {lmin:.3f}…{lmax:.3f}")
for nm, p in (("A φу", A_pos), ("B φк", B_pos)):
    pr(f"{nm}: φ={p['phi']:.3f} F={p['F']:.1f} P={p['P']:.2f} lOD={p['lOD']:.3f} N={p['N']:.2f} Q_OD={p['Q_OD']:.1f} Q_DK={p['Q_DK']:.2f} "
       f"M_D={p['M_D']/1000:.3f} Н·м R12N={p['R12N']:.1f} |R10|={p['R10']:.1f} |R23|={p['R23']:.1f} R30N={p['R30N']:.1f}")
pr(f"max|M_D| = {R['MD_max']/1000:.3f} Н·м при φ = {R['MD_max_phi']:.3f}; max|Q_OD| = {R['QD_max']:.1f} при φ = {R['QD_max_phi']:.3f}")
pr(f"[σ]={sig_a:.1f} [τ]={tau_a:.1f} [p]={p_a}")
pr(f"палец D: требуемые d {', '.join(f'{k}={v:.2f}' for k, v in d_req_D.items())} → d={dD}; σи={pinD['sig']:.1f} τ={pinD['tau']:.1f} "
   f"p камень={pinD['p_stone']:.1f} p проушина={pinD['p_lug']:.1f} σ проушины={pinD['sig_lug']:.1f}")
pr(f"камень {w}×{ls}×{b}: p={stone['p']:.1f}")
pr(f"ось O вар.1: плечо {arm1} → d≥{axO['d1_req']:.2f} → {dO1}, бобышка r={rb1}; вар.2: плечо {arm2} → d≥{axO['d2_req']:.2f} → {dO2}, "
   f"σ={axO['sig2']:.1f} τ={axO['tau2']:.1f} p={axO['p2']:.1f}, ступица Ø{Dh}×{lh}")
pr(f"компоновка: камень у оси в конце хода ближе всего на {lay['stone_inner']:.2f} мм; вар.1 нужно lOD ≥ {need1:.2f} (нехватка {lay['short1']:.2f}, "
   f"перекрытие с бобышкой {lay['overlap1']:.2f}) → e ≥ {lay['e_req1']:.2f}; паз a1={a1:.2f} a2={a2:.2f} пролёт {span:.2f}")
for c in cand:
    pr(f"  H={c['H']:>4} ({c['ser']}): t={c['A']['t']:.1f} σг={c['A']['sig_g']:.1f} σм={c['A']['sig_loc']:.1f} Σ={c['A']['sig']:.1f} | "
       f"B: σг={c['B']['sig_g']:.1f} σм={c['B']['sig_loc']:.1f} Σ={c['B']['sig']:.1f} τ={c['A']['tau']:.1f} {'OK' if c['ok'] else '—'}")
pr(f"принято H = {Hsel}: A {R['secA']}")
pr(f"рукоять: h_req(a2)={R['handle']['h_req_a2']:.2f}, h_req(zt)={R['handle']['h_req_zt']:.2f}, σmax={R['handle']['sig_max']:.1f} при z={R['handle']['z_sig_max']:.1f}; "
   f"прогиб K {R['handle']['vK']:.2f} мм (по вертикали {R['handle']['vK_vert']:.2f}); M(L) check {R['Mz_check']:.3f}")
pr(f"ползун: σ={R['slider']['sig']:.2f} λ={R['slider']['lam']:.0f} p направл.={R['slider']['p_guide']:.1f}")
m = R["mass"]
pr(f"массы: планка {m['m_plate']:.3f}, ступица {m['m_hub']:.3f} → m1={m['m1']:.3f} кг, zc={m['zc1']:.1f} мм, JO={m['JO1']:.4f}, JS={m['JS1']:.4f} кг·м²; "
   f"m2={m['m2']:.4f} JS2={m['JS2']:.2e}; m3={m['m3']:.3f} (yc {m['yc3']:.1f}) {m['parts3']}; G1·zc/L={m['dP_G1']:.2f} Н, Jε→{m['dP_J']:.2f} Н")
