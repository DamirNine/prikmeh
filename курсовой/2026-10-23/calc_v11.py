# -*- coding: utf-8 -*-
"""Раздел 12 (v11) — прочностной расчёт звеньев по схеме консультации 19.10:
опасные положения механизма → эпюры N, Q, M → σ = |N|/A + |M|/W ≤ [σ] →
пруток: перебор диаметров по сортаменту ГОСТ 2590-2006; лист: толщина b по ГОСТ 19903-2015 известна, h — из уравнения →
выбор материала → массы звеньев. Результаты → strength_v11.json."""
import json, os
import numpy as np
from math import pi, tan, atan, sin, cos, radians as rad, degrees as deg, log, sqrt

OUT = os.path.dirname(os.path.abspath(__file__))
R = {}

# ------------------------------------------------------------------ механизм и нагрузки (разд. 7–11, без изменений)
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
    """решение разд. 11.6 и внутренние силовые факторы кулисы (z — от оси O вдоль звена; Q, M — по силам левее сечения)"""
    F = Fphi(phi); p = rad(phi); c, s = cos(p), sin(p)
    P = F * e / (L * c ** 3) if F > 0 else 0.0
    d = dict(phi=phi, F=F, P=P, R10x=F * tan(p), R10y=P - F, R12N=F / c, R23x=-F * tan(p), R23y=F, R30N=-F * tan(p), lOD=e / c)
    d["R10"] = float(np.hypot(d["R10x"], d["R10y"])); d["R23"] = float(np.hypot(d["R23x"], d["R23y"]))
    d["N"] = -P * s
    d["Q_OD"] = P * c - F / c
    d["Q_DK"] = P * c
    d["M_D"] = d["Q_OD"] * d["lOD"]                       # Н·мм
    return d

lmin, lmax = e / cos(rad(phi_k)), e / cos(rad(phi_n))
R["mech"] = dict(phi_n=phi_n, phi_k=phi_k, phi_ob=phi_ob, phi_y=phi_y, lOD_min=lmin, lOD_max=lmax, F_t=F_t, F_max=F_max)

# ------------------------------------------------------------------ 1. опасные положения: максимум определяющей нагрузки каждого элемента по всему рабочему ходу
phs = np.linspace(phi_k, phi_ob, 40001)
LD = [loads(p) for p in phs]
crit = {
    "M_D":  ("изгибающий момент в кулисе у камня |M_D|", lambda d: abs(d["M_D"]) / 1000, "Н·м"),
    "Q_DK": ("момент в рукояти за пазом ∝ P·cos φ", lambda d: d["Q_DK"], "Н"),
    "R12N": ("сила камня на кулису R12N = |R23| (палец D, камень, стенка паза)", lambda d: d["R12N"], "Н"),
    "R10":  ("реакция оси O |R10|", lambda d: d["R10"], "Н"),
    "F":    ("сила обжима Fук (сжатие штока)", lambda d: d["F"], "Н"),
    "R30N": ("поперечная реакция направляющей |R30N|", lambda d: abs(d["R30N"]), "Н"),
    "P":    ("сила руки P", lambda d: d["P"], "Н"),
}
R["crit"] = {}
for k, (nm, fn, un) in crit.items():
    v = np.array([fn(d) for d in LD]); i = int(np.argmax(v))
    R["crit"][k] = dict(name=nm, phi=float(phs[i]), max=float(v[i]), unit=un)
A_pos, B_pos = loads(phi_y), loads(phi_k)
R["A"], R["B"] = A_pos, B_pos

# ------------------------------------------------------------------ 2. каталоги
SHEET = [6.0, 8.0, 10.0]                                               # ГОСТ 19903-2015, табл. 4 (фрагмент ряда толщин)
BAR = [5, 5.5, 6, 6.3, 6.5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]  # ГОСТ 2590-2006
RA20 = [10, 11, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 45, 50, 56, 63]                        # ГОСТ 6636-69
up = lambda x, ser: min(v for v in ser if v >= x - 1e-9)
MATS = [  # марка, ГОСТ, σт, σв, свариваемость
    ("Ст3сп", "ГОСТ 14637-89", 245.0, 370.0),
    ("35", "ГОСТ 1050-2013", 315.0, 530.0),
    ("45", "ГОСТ 1050-2013", 355.0, 600.0),
    ("40Х", "ГОСТ 4543-2016", 785.0, 980.0),
]
n_T = 2.5
mats = [dict(name=m, gost=gs, sig_T=sT, sig_B=sB, sig_a=sT / n_T, tau_a=0.5 * sT / n_T) for m, gs, sT, sB in MATS]
R["mats"], R["n_T"] = mats, n_T

# ------------------------------------------------------------------ 3. конструктивные параметры (компоновка разд. 12: ползун — кулиса — ступица — стойка)
g = 1.0          # зазор между слоями по толщине, мм
s_k = 3.0        # стенка камня вокруг пальца, мм
l_h = 16.0       # длина ступицы кулисы на оси O, мм
l_rod, mu_rod = 60.0, 2.0     # свободная длина штока от направляющей до головки; консоль
rho, E = 7850e-9, 2.1e5

# коэффициент снижения допускаемого напряжения φ(λ) для Ст3 (сжатые стержни) — Феодосьев, табл.
LAM = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
PHI_ST3 = [1.00, 0.99, 0.96, 0.94, 0.92, 0.89, 0.86, 0.81, 0.75, 0.69, 0.60, 0.52, 0.45, 0.40, 0.36, 0.32]
phi_buck = lambda lam: float(np.interp(lam, LAM, PHI_ST3))

def fixed_fixed_M(span, c, lk, P, n=6001):
    """стенка паза — балка с заделанными концами; P равномерно на [c − lk/2, c + lk/2]; возвращает x, M(x)"""
    x = np.linspace(0, span, n); q = np.where(np.abs(x - c) <= lk / 2 + 1e-12, P / lk, 0.0)
    q *= P / np.trapezoid(q, x)
    dx = x[1] - x[0]
    MA = -np.trapezoid(q * x * (span - x) ** 2, x) / span ** 2
    RA = np.trapezoid(q * (span - x) ** 2 * (span + 2 * x), x) / span ** 3
    cumq = np.concatenate([[0], np.cumsum((q[1:] + q[:-1]) / 2 * dx)])
    cumqx = np.concatenate([[0], np.cumsum((q[1:] * x[1:] + q[:-1] * x[:-1]) / 2 * dx)])
    M = MA + RA * x - (x * cumq - cumqx)
    return x, M

def round_pass(cond):
    return next(d for d in BAR if cond(d))

def profile(z, H, h, t, a2):
    """высота планки кулисы по длине: хвост R = H/2 за осью O, H до конца паза + перемычка t, переход 1:5 на сторону, далее h"""
    z = np.asarray(z, float); z1 = a2 + t; lt = 2.5 * (H - h)
    hz = np.where(z <= z1, H, np.where(z <= z1 + lt, H + (h - H) * (z - z1) / lt, h))
    return hz, z1, lt

def kulisa_props(b, H, h, w, t, a1, a2, dO, Dh, pos):
    """масса, центр масс, момент инерции планки со ступицей; прогиб конца K (опоры O и D, положение pos)"""
    dz = 0.1
    Z, Y = np.meshgrid(np.arange(-H / 2, L + dz / 2, dz), np.arange(-H / 2, H / 2 + dz / 2, dz), indexing="xy")
    hz, z1, lt = profile(np.clip(Z, 0, None), H, h, t, a2)
    plate = ((Z < 0) & (Z ** 2 + Y ** 2 <= (H / 2) ** 2)) | ((Z >= 0) & (Z <= L) & (np.abs(Y) <= hz / 2))
    plate &= ~((Z >= a1) & (Z <= a2) & (np.abs(Y) <= w / 2))
    dA = dz * dz; Ap = plate.sum() * dA
    m_pl = rho * b * Ap; zc_pl = Z[plate].sum() * dA / Ap
    J_pl = rho * b * (Z[plate] ** 2 + Y[plate] ** 2).sum() * dA                     # кг·мм²
    m_hub = rho * pi / 4 * (Dh ** 2 - dO ** 2) * l_h; J_hub = m_hub * (Dh ** 2 + dO ** 2) / 8
    m1 = m_pl + m_hub; zc1 = m_pl * zc_pl / m1; JO = J_pl + J_hub
    # прогиб: v'' = M/(E·I), v(0) = 0, v(lOD) = 0
    zg = np.linspace(0, L, 50001)
    hzg, _, _ = profile(zg, H, h, t, a2)
    I = np.where((zg >= a1) & (zg <= a2), b * (H ** 3 - w ** 3) / 12, b * hzg ** 3 / 12)
    Mz = np.where(zg <= pos["lOD"], pos["Q_OD"] * zg, pos["Q_DK"] * (zg - L))
    kap = Mz / (E * I)
    th = np.concatenate([[0], np.cumsum((kap[1:] + kap[:-1]) / 2 * np.diff(zg))])
    v0 = np.concatenate([[0], np.cumsum((th[1:] + th[:-1]) / 2 * np.diff(zg))])
    v = v0 - np.interp(pos["lOD"], zg, v0) * zg / pos["lOD"]
    return dict(A_plate=Ap, m_plate=m_pl, m_hub=m_hub, m1=m1, zc1=zc1, JO=JO * 1e-6, JS=(JO - m1 * zc1 ** 2) * 1e-6,
                z1=z1, lt=lt, fK=float(abs(v[-1])), fK_vert=float(abs(v[-1]) * cos(rad(pos["phi"]))))

def design(mat, b, mat_bar=None):
    """все размеры при толщине листа b; mat — лист (кулиса), mat_bar — пруток (палец D, ось O, камень, ползун)"""
    mb = mat_bar or mat
    sa, ta = mat["sig_a"], mat["tau_a"]
    sab, tab = mb["sig_a"], mb["tau_a"]
    r = dict(mat=mat["name"], mat_bar=mb["name"], b=b)
    # --- палец D (пруток): консоль, плечо от торца ползуна до середины камня
    aD = g + b / 2; RD = A_pos["R23"]; MDp = RD * aD
    sigD = lambda d: 32 * MDp / (pi * d ** 3); tauD = lambda d: 16 * RD / (3 * pi * d ** 2)
    dD = round_pass(lambda d: sigD(d) <= sab and tauD(d) <= tab)
    r["pinD"] = dict(R=RD, a=aD, M=MDp, d=dD, sig=sigD(dD), tau=tauD(dD))
    # --- камень и паз
    w = up(dD + 2 * s_k, RA20); lk = w
    a1, a2 = lmin - lk / 2 - g, lmax + lk / 2 + g; span = a2 - a1
    r["stone"] = dict(w=w, lk=lk, p_slot=A_pos["R12N"] / (b * lk), p_pin=RD / (dD * b))
    r["slot"] = dict(a1=a1, a2=a2, span=span)
    # --- рукоять (лист b × h): опасное сечение — начало сплошной части z = a2
    Nh = abs(A_pos["N"]); Mh = abs(A_pos["Q_DK"]) * (L - a2)
    h_req = (Nh + sqrt(Nh ** 2 + 24 * sa * b * Mh)) / (2 * sa * b)
    h = up(h_req, RA20)
    r["handle"] = dict(N=Nh, M=Mh, z=a2, h_req=h_req, h=h, sig=Nh / (b * h) + 6 * Mh / (b * h ** 2))
    # --- зона паза: сечение b × H с вырезом w; общий изгиб + местный изгиб стенки
    def sec(H, pos):
        t = (H - w) / 2; A = b * (H - w); W = b * (H ** 3 - w ** 3) / (6 * H)
        x, Mx = fixed_fixed_M(span, pos["lOD"] - a1, lk, pos["R12N"])
        Ml = float(np.max(np.abs(Mx)))
        sg = abs(pos["N"]) / A + abs(pos["M_D"]) / W; sl = 6 * Ml / (b * t ** 2)
        return dict(H=H, t=t, A=A, W=W, sig_N=abs(pos["N"]) / A, sig_M=abs(pos["M_D"]) / W, sig_g=sg, Mloc=Ml, sig_loc=sl,
                    sig=sg + sl, tau=1.5 * abs(pos["Q_OD"]) / A)
    H_req = bisect(lambda H: max(sec(H, A_pos)["sig"], sec(H, B_pos)["sig"]) - sa, w + 1.0, w + 80.0)
    H = up(H_req, RA20)
    r["slotsec"] = dict(H_req=H_req, H=H, A=sec(H, A_pos), B=sec(H, B_pos))
    # --- ось O (пруток): консоль из стойки через ступицу, плечо до середины планки
    aO = g + l_h + b / 2; RO = A_pos["R10"]; MOp = RO * aO
    sigO = lambda d: 32 * MOp / (pi * d ** 3); tauO = lambda d: 16 * RO / (3 * pi * d ** 2)
    dO = round_pass(lambda d: sigO(d) <= sab and tauO(d) <= tab)
    Dh = up(2 * dO, RA20)
    r["axO"] = dict(R=RO, a=aO, M=MOp, d=dO, sig=sigO(dO), tau=tauO(dO), Dh=Dh, lh=l_h, p=RO / (dO * l_h))
    # --- шток ползуна (пруток): сжатие N = −Fук (φк); условие прочности и малой гибкости λ = μ·l/i ≤ 40
    Fr = B_pos["F"]
    d_str = round_pass(lambda d: 4 * Fr / (pi * d ** 2) <= sab)
    d_rod = round_pass(lambda d: 4 * Fr / (pi * d ** 2) <= sab and mu_rod * l_rod / (d / 4) <= 40 + 1e-9)
    r["rod"] = dict(F=Fr, d_strength=d_str, sig_strength=4 * Fr / (pi * d_str ** 2), lam_strength=mu_rod * l_rod / (d_str / 4),
                    d=d_rod, sig=4 * Fr / (pi * d_rod ** 2), lam=mu_rod * l_rod / (d_rod / 4))
    # --- масса и прогиб кулисы
    ss = r["slotsec"]
    r["kul"] = kulisa_props(b, ss["H"], h, w, ss["A"]["t"], a1, a2, dO, Dh, A_pos)
    return r

# ------------------------------------------------------------------ 4. варианты: марки стали × толщины листа (все детали из одной марки)
VAR = {}
for m in mats:
    for b in SHEET:
        VAR[f"{m['name']}|{b:g}"] = design(m, b)
R["var"] = VAR

# ------------------------------------------------------------------ 5. принятый вариант: кулиса — лист Ст3сп 8 мм; палец D, ось O, камень, ползун — сталь 45
M_ = {m["name"]: m for m in mats}
FIN = design(M_["Ст3сп"], 8.0, M_["45"])
R["fin"] = FIN
# проверка принятых размеров в обоих опасных положениях
fz = FIN
R["fin_check"] = {
    "handle_B": abs(B_pos["N"]) / (8.0 * fz["handle"]["h"]) + 6 * abs(B_pos["Q_DK"]) * (L - fz["slot"]["a2"]) / (8.0 * fz["handle"]["h"] ** 2),
    "pinD_B": 32 * B_pos["R23"] * fz["pinD"]["a"] / (pi * fz["pinD"]["d"] ** 3),
    "axO_B": 32 * B_pos["R10"] * fz["axO"]["a"] / (pi * fz["axO"]["d"] ** 3),
}
# стенка паза: эпюра местного момента в принятом варианте (для рисунка)
xw, Mw = fixed_fixed_M(fz["slot"]["span"], A_pos["lOD"] - fz["slot"]["a1"], fz["stone"]["lk"], A_pos["R12N"], n=6001)
R["wall_epure"] = dict(x=xw[::20].tolist(), M=Mw[::20].tolist())
# массы звеньев 2 и 3 (камень — по принятым размерам; ползун — ориентировочно)
dD_, w_, b_ = fz["pinD"]["d"], fz["stone"]["w"], 8.0
m2 = rho * b_ * (w_ * w_ - pi * dD_ ** 2 / 4)
JS2 = rho * b_ * (w_ * w_ * (2 * w_ ** 2) / 12 - pi * dD_ ** 4 / 32)
blk = (24.0, 40.0, 16.0)                                     # направляемая часть ползуна, мм
parts3 = {"направляемая часть 24 × 40 × 16": rho * blk[0] * blk[1] * blk[2],
          f"палец D Ø{dD_:g} × {blk[2] + g + b_:g}": rho * pi / 4 * dD_ ** 2 * (blk[2] + g + b_),
          f"шток Ø{fz['rod']['d']:g} × {l_rod:g}": rho * pi / 4 * fz["rod"]["d"] ** 2 * l_rod,
          "головка Ø40 × 24": rho * pi / 4 * (40 ** 2 * 24 - 30 ** 2 * 20)}
R["mass23"] = dict(m2=m2, JS2=JS2 * 1e-6, parts3=parts3, m3=sum(parts3.values()))

# ------------------------------------------------------------------ 6. перегрузка: конец хода, головка упёрлась, рука давит с Pдоп = 120 Н
Pd = 120.0; pk = rad(phi_k)
F_ov = Pd * L * cos(pk) ** 3 / e
ov = dict(P=Pd, F=F_ov, R12N=F_ov / cos(pk), R10=float(np.hypot(F_ov * tan(pk), Pd - F_ov)), M_D=Pd * (L * cos(pk) - e))
ov["k_F"] = F_ov / B_pos["F"]; ov["k_R12"] = ov["R12N"] / A_pos["R12N"]; ov["k_R10"] = ov["R10"] / A_pos["R10"]
ov["k_M"] = ov["M_D"] / abs(A_pos["M_D"]); ov["k_max"] = max(ov["k_F"], ov["k_R12"], ov["k_R10"], ov["k_M"])
# при упоре в φк все нагрузки пропорциональны Fук → напряжения принятых элементов в положении φк умножаются на k_F
sB = dict(handle=R["fin_check"]["handle_B"], slot=FIN["slotsec"]["B"]["sig"], pinD=R["fin_check"]["pinD_B"],
          axO=R["fin_check"]["axO_B"], rod=FIN["rod"]["sig"])
ov["sig"] = {k: v * ov["k_F"] for k, v in sB.items()}
R["overload"] = ov
# сравнение толщин листа для принятого сочетания материалов
R["fin_b"] = {f"{b:g}": design(M_["Ст3сп"], b, M_["45"]) for b in SHEET}

# итерационные таблицы «перебор по сортаменту» (b = 8): σ пальца D, оси O, штока для каждого диаметра
b_sel = 8.0
aD8, aO8 = g + b_sel / 2, g + l_h + b_sel / 2
it = []
for d in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]:
    it.append(dict(d=d, sigD=32 * A_pos["R23"] * aD8 / (pi * d ** 3), sigO=32 * A_pos["R10"] * aO8 / (pi * d ** 3),
                   sigR=4 * B_pos["F"] / (pi * d ** 2), lam=mu_rod * l_rod / (d / 4)))
R["iter_bar"] = it
R["aD8"], R["aO8"] = aD8, aO8

# ------------------------------------------------------------------ печать
pr = print
pr(f"окно {phi_n:.3f}→{phi_k:.3f}, φоб {phi_ob:.3f}, φу {phi_y:.4f}; lOD {lmin:.3f}…{lmax:.3f}; Fт {F_t:.1f}, Fmax {F_max:.1f}")
for k, v in R["crit"].items():
    pr(f"  max {v['name']}: {v['max']:.2f} {v['unit']} при φ = {v['phi']:.3f}")
for nm, p in (("A φу", A_pos), ("B φк", B_pos)):
    pr(f"{nm}: φ={p['phi']:.3f} F={p['F']:.1f} P={p['P']:.2f} lOD={p['lOD']:.3f} N={p['N']:.2f} Q_OD={p['Q_OD']:.1f} Q_DK={p['Q_DK']:.2f} "
       f"M_D={p['M_D']/1000:.3f} R12N={p['R12N']:.1f} |R10|={p['R10']:.1f} R30N={p['R30N']:.1f}")
for m in mats:
    pr(f"{m['name']}: σт {m['sig_T']}, [σ] {m['sig_a']:.1f}, [τ] {m['tau_a']:.1f}")
def show(k, r):
    pr(f"{k:>12}: D Ø{r['pinD']['d']:g} (σ {r['pinD']['sig']:.0f}, τ {r['pinD']['tau']:.0f}) камень {r['stone']['w']} "
       f"(p {r['stone']['p_slot']:.0f}/{r['stone']['p_pin']:.0f}) | h {r['handle']['h_req']:.2f}→{r['handle']['h']} (σ {r['handle']['sig']:.0f}) | "
       f"H {r['slotsec']['H_req']:.2f}→{r['slotsec']['H']} (t {r['slotsec']['A']['t']:.1f}, σг {r['slotsec']['A']['sig_g']:.0f} "
       f"σм {r['slotsec']['A']['sig_loc']:.0f} Σ {r['slotsec']['A']['sig']:.0f}; B Σ {r['slotsec']['B']['sig']:.0f}) | "
       f"O Ø{r['axO']['d']:g} (σ {r['axO']['sig']:.0f}) ступица Ø{r['axO']['Dh']} | шток Ø{r['rod']['d_strength']:g}/λ{r['rod']['lam_strength']:.0f} → Ø{r['rod']['d']:g} | "
       f"m1 {r['kul']['m1']:.3f} fK {r['kul']['fK']:.2f}")
for k, r in VAR.items():
    show(k, r)
show("ПРИНЯТО", FIN)
pr("  проверка в φк:", {k: round(v, 1) for k, v in R["fin_check"].items()}, "| паз:", {k: round(v, 2) if isinstance(v, float) else v for k, v in FIN["slot"].items()})
pr("  кулиса:", {k: round(v, 4) for k, v in FIN["kul"].items()})
pr("  m2", round(R["mass23"]["m2"], 4), "JS2", R["mass23"]["JS2"], "m3", round(R["mass23"]["m3"], 3), {k: round(v, 4) for k, v in R["mass23"]["parts3"].items()})
pr("  перегрузка:", {k: (round(v, 3) if not isinstance(v, dict) else {a: round(c, 1) for a, c in v.items()}) for k, v in ov.items()})
for k, r in R["fin_b"].items():
    show("Ст3сп+45|" + k, r)
pr("  местный момент стенки (принято):", round(FIN["slotsec"]["A"]["Mloc"], 1), "Н·мм; τ паза", round(FIN["slotsec"]["A"]["tau"], 1))
pr("перебор (b = 8):")
for x in it:
    pr(f"  d {x['d']:>4}: σD {x['sigD']:7.1f}  σO {x['sigO']:7.1f}  σшт {x['sigR']:6.1f}  λ {x['lam']:.0f}")

json.dump(R, open(os.path.join(OUT, "strength_v11.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
