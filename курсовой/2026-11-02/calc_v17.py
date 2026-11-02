# -*- coding: utf-8 -*-
"""v17 (02.11): уточнённый силовой расчёт — к первичному (разд. 11, calc_v8.py) добавлены силы тяжести и силы инерции звеньев
по массам табл. 18 (strength_v13.json) и закону ω(t) п. 9; трение и обратный ход не учитываются. Та же матрица A(φ),
новый столбец свободных членов B(φ). Проверочный прочностной расчёт кулисы — с распределёнными силами тяжести и инерции.
Результат: calc_v17.json, calc_v17.npz (для figs_v17.py)."""
import json, os
import numpy as np
from math import radians, degrees, tan, atan, cos, sin, log, pi, hypot, sqrt

HERE = os.path.dirname(os.path.abspath(__file__))
R13 = json.load(open(os.path.join(HERE, "..", "2026-10-24", "strength_v13.json"), encoding="utf-8"))

# ---------------- исходные данные (как calc_v8.py)
S, Sob, e, psi = 16.0, 6.0, 12.53, 36.75
P_dop, xM, yM, L = 120.0, 50.0, 500.0, 500.0
sig_t, E, Dk, Dobzh, s_, n_ = 415.0, 2.1e5, 32.10, 28.6, 0.22, 2.0
eps_y = sig_t / E; dr_y = eps_y * Dk / 2; tg_a = ((Dk - Dobzh) / 2) / Sob; d_y = dr_y / tg_a
A_pr = n_ * pi * (Dobzh - s_) * s_ * log(Dk / Dobzh); F_t = sig_t * A_pr; F_max = 1.05 * F_t
C, k_h = F_t / d_y, (F_max - F_t) / (Sob - d_y)

f_ = lambda pk: tan(radians(pk + psi)) - tan(radians(pk)) - S / e
lo, hi = 0.0, 60 - psi
for _ in range(200):
    mid = 0.5 * (lo + hi)
    lo, hi = (mid, hi) if f_(lo) * f_(mid) > 0 else (lo, mid)
phi_k = 0.5 * (lo + hi); phi_n = phi_k + psi; tk = tan(radians(phi_k))
phi_ob = degrees(atan(tk + Sob / e)); phi_y = degrees(atan(tk + (Sob - d_y) / e))
psi_xx, psi_u, psi_pl = radians(phi_n - phi_ob), radians(phi_ob - phi_y), radians(phi_y - phi_k)

# закон движения (п. 9): ω, ε — по модулю на рабочем ходе (φ убывает): φ' = −ω, φ'' = −ε
w = 700.0 / L
t_r, t_u, t_t = 2 * psi_xx / w, psi_u / w, 2 * psi_pl / w
eps_r, eps_t = w / t_r, -w / t_t

# массы (табл. 18)
KU = R13["kul"]; m1, zS, JO, JS = KU["m"], KU["zc"] / 1000, KU["JO"], KU["JS"]; m3 = R13["m3"]
g = 9.81; G1, G3 = m1 * g, m3 * g
b_k, h_k, rho = 8.0, 18.0, 7850.0
q_m = rho * b_k * h_k * 1e-6                      # кг/м — погонная масса полосы
A_k, W_k = b_k * h_k, b_k * h_k ** 2 / 6
sig_adm, tau_adm = 245 / 2.5, 0.5 * 245 / 2.5


def F_of(ph):
    dl = e * tan(radians(phi_ob)) - e * tan(radians(ph))
    if dl <= 0:
        return 0.0
    return C * dl if dl <= d_y else F_t + k_h * (dl - d_y)


def kin(ph, side=None):
    """ω, ε по углу; side = 'до'/'после' — по какую сторону скачка ε брать значение в точке смены фаз"""
    if ph > phi_ob or (side == "до" and abs(ph - phi_ob) < 1e-9):
        return sqrt(max(0.0, 2 * eps_r * radians(phi_n - ph))), eps_r
    if ph >= phi_y and not (side == "после" and abs(ph - phi_y) < 1e-9):
        return w, 0.0
    return sqrt(max(0.0, 2 * (-eps_t) * radians(ph - phi_k))), eps_t


def loads(ph, om, ep):
    """силы тяжести и инерции; единицы — Н, Н·м, м/с²"""
    c, s = cos(radians(ph)), sin(radians(ph))
    Ft1, Fn1 = m1 * ep * zS, m1 * om ** 2 * zS          # касательная (по нормали n к кулисе) и центробежная (по оси u)
    F1x, F1y = Fn1 * c - Ft1 * s, Fn1 * s + Ft1 * c       # Ф1 = Ф1τ·n + Ф1n·u
    MF1 = JS * ep                                         # M_Ф1 = −J_S·φ'' = J_S·ε (против часовой — плюс)
    aDy = (om ** 2 * 2 * e * s / c ** 3 + ep * (-e / c ** 2)) / 1000
    F3y = -m3 * aDy
    return dict(Ft1=Ft1, Fn1=Fn1, F1x=F1x, F1y=F1y, MF1=MF1, aDy=aDy, F3y=F3y,
                aS1t=ep * zS, aS1n=om ** 2 * zS)


def system(ph, F, ld=None):
    """A(φ)·X = B(φ); X = (R10x, R10y, R12N, M12, R23x, R23y, R30N, M30, P); ld = None — первичный расчёт"""
    c, s, t = cos(radians(ph)), sin(radians(ph)), tan(radians(ph))
    XD, YD = xM + e, yM - e * t
    XK = xM + L * c
    a = XD * c - YD * s
    A = np.zeros((9, 9)); B = np.zeros(9)
    A[0, [0, 2]] = [1, -s]; A[1, [1, 2, 8]] = [1, c, -1]; A[2, [0, 1, 2, 3, 8]] = [yM, xM, a, 1, -XK]
    A[3, [2, 4]] = [s, 1]; A[4, [2, 5]] = [-c, 1]; A[5, [2, 3, 4, 5]] = [-a, -1, YD, XD]
    A[6, [4, 6]] = [-1, 1]; A[7, 5] = -1; A[8, [4, 5, 6, 7]] = [-YD, -XD, YD, 1]
    Fe = F if ld is None else F - G3 + ld["F3y"]
    B[7] = -Fe; B[8] = -Fe * XD
    if ld is not None:
        XS, YS = xM + zS * 1000 * c, yM - zS * 1000 * s
        B[0] = -ld["F1x"]
        B[1] = G1 - ld["F1y"]
        B[2] = G1 * XS - ld["F1y"] * XS - ld["F1x"] * YS - ld["MF1"] * 1000
    return A, B


def analytic(ph, F, ld, ep):
    """P·L·cos φ = (F − G3 + Ф3)·e/cos²φ − G1·zS·cos φ + J_O·ε (моменты относительно O)"""
    c = cos(radians(ph))
    Fe = F - G3 + ld["F3y"]
    return (Fe * e / c ** 2 - G1 * zS * 1000 * c + JO * ep * 1000) / (L * c)


def beam(ph, P, R12N, om, ep):
    """внутренние силы кулисы под камнем (z = l_OD) с распределёнными силами тяжести и инерции; Н, Н·м"""
    c, s = cos(radians(ph)), sin(radians(ph))
    Lm, z = L / 1000, e / c / 1000
    Iu = q_m * (om ** 2 * (Lm ** 2 - z ** 2) / 2 - g * s * (Lm - z))
    In = q_m * (ep * (Lm ** 2 - z ** 2) / 2 - g * c * (Lm - z))
    Im = q_m * (ep * ((Lm ** 3 - z ** 3) / 3 - z * (Lm ** 2 - z ** 2) / 2) - g * c * (Lm - z) ** 2 / 2)
    N = -P * s + Iu
    MD = -P * c * (Lm - z) + Im
    In0 = q_m * (ep * Lm ** 2 / 2 - g * c * Lm)
    Q_OD = max(abs(P * c - R12N - In), abs(P * c - R12N - In0))
    sig = abs(N) / A_k + abs(MD) * 1000 / W_k
    return dict(N=N, MD=MD, Q_OD=Q_OD, sig=sig, tau=1.5 * Q_OD / A_k)


# ---------------- решение на 40 001 положении
phs = np.linspace(phi_n, phi_k, 40001)
X0 = np.zeros((phs.size, 9)); X1 = np.zeros((phs.size, 9))
OM = np.zeros(phs.size); EP = np.zeros(phs.size); SIG = np.zeros(phs.size); MDv = np.zeros(phs.size)
err_an = 0.0
for i, ph in enumerate(phs):
    F = F_of(ph); om, ep = kin(ph); ld = loads(ph, om, ep)
    OM[i], EP[i] = om, ep
    A0, B0 = system(ph, F); X0[i] = np.linalg.solve(A0, B0)
    A1, B1 = system(ph, F, ld); X1[i] = np.linalg.solve(A1, B1)
    assert np.allclose(A0, A1)
    err_an = max(err_an, abs(analytic(ph, F, ld, ep) - X1[i, 8]))
    bm = beam(ph, X1[i, 8], X1[i, 2], om, ep); SIG[i] = bm["sig"]; MDv[i] = bm["MD"]

# ---------------- характерные положения (до/после скачков ε)
pts = [("начало хода", phi_n, None), ("касание с крышкой (до)", phi_ob, "до"), ("касание (после)", phi_ob, "после"),
       ("начало пластической деформации (до)", phi_y, "до"), ("начало пластической деформации (после)", phi_y, "после"),
       ("промежуточное", 30.0, None), ("конец хода", phi_k, None)]
rows = []
for name, ph, side in pts:
    F = F_of(ph); om, ep = kin(ph, side); ld = loads(ph, om, ep)
    x0 = np.linalg.solve(*system(ph, F)); x1 = np.linalg.solve(*system(ph, F, ld))
    # первичный — без распределённых сил
    c, s_ = cos(radians(ph)), sin(radians(ph))
    MD0 = -x0[8] * c * (L - e / c) / 1000; N0 = -x0[8] * s_
    sig0 = abs(N0) / A_k + abs(MD0) * 1000 / W_k
    bm1 = beam(ph, x1[8], x1[2], om, ep)
    rows.append(dict(name=name, phi=ph, F=F, om=om, ep=ep, **{k: v for k, v in ld.items()},
                     X0=x0.tolist(), X1=x1.tolist(), R10_0=hypot(x0[0], x0[1]), R10_1=hypot(x1[0], x1[1]),
                     sig0=sig0, MD0=MD0, N0=N0, beam1=bm1, P_an=analytic(ph, F, ld, ep)))

# ---------------- экстремумы по ходу (сетка + точки по обе стороны скачков)
def ext(k, fn=max, absval=False):
    vals = [(abs(X1[i, k]) if absval else X1[i, k], phs[i]) for i in range(phs.size)]
    vals += [(abs(r["X1"][k]) if absval else r["X1"][k], r["phi"]) for r in rows]
    return fn(vals)

P1max, phP = ext(8)
P1min, phPmin = ext(8, min)
R12max, ph12 = ext(2, absval=True)
R30max, ph30 = ext(6, absval=True)
R10ymax, ph10y = ext(1, absval=True)
R10all = [(hypot(X1[i, 0], X1[i, 1]), phs[i]) for i in range(phs.size)] + [(r["R10_1"], r["phi"]) for r in rows]
R10max, ph10 = max(R10all)
sig_all = [(SIG[i], phs[i]) for i in range(phs.size)] + [(r["beam1"]["sig"], r["phi"]) for r in rows]
sig1max, phsig = max(sig_all)
tau1max = max(beam(r["phi"], r["X1"][8], r["X1"][2], r["om"], r["ep"])["tau"] for r in rows)
p1max = R12max / (b_k * 20)
# холостой ход: P < 0, R12N < 0
idle = phs > phi_ob
P_idle = (X1[idle, 8].min(), X1[idle, 8].max())
R12_idle = (X1[idle, 2].min(), X1[idle, 2].max())

# ---------------- шток: сжатие нижней части не больше силы обжима
rod_ok = all(g + r["aDy"] > 0 for r in rows)

# ---------------- проверка по работе за ход: ΔT = 0 → A_P = A_F − ΔП
dphi = np.radians(phs[0] - phs[1])
cphs = np.cos(np.radians(phs))
W_P = np.trapezoid(X1[:, 8] * L / 1000 * cphs, dx=dphi)             # работа силы руки (рука идёт вниз)
W_F = np.trapezoid(np.array([F_of(x) for x in phs]) * (e / 1000) / cphs ** 2, dx=dphi)
dPi = G1 * zS * (sin(radians(phi_n)) - sin(radians(phi_k))) + G3 * S / 1000
W_P0 = np.trapezoid(X0[:, 8] * L / 1000 * cphs, dx=dphi)

res = dict(phi_n=phi_n, phi_k=phi_k, phi_ob=phi_ob, phi_y=phi_y, w=w, eps_r=eps_r, eps_t=eps_t, t_r=t_r, t_u=t_u, t_t=t_t,
           m1=m1, zS=zS, JO=JO, JS=JS, m3=m3, G1=G1, G3=G3, q_m=q_m, F_t=F_t, F_max=F_max,
           rows=rows, P1max=P1max, phP=phP, P1min=P1min, phPmin=phPmin, P0max=X0[:, 8].max(),
           R12max=R12max, ph12=ph12, R30max=R30max, ph30=ph30, R10ymax=R10ymax, ph10y=ph10y, R10max=R10max, ph10=ph10,
           sig1max=sig1max, phsig=phsig, tau1max=tau1max, p1max=p1max, P_idle=P_idle, R12_idle=R12_idle, rod_ok=rod_ok,
           err_an=err_an, W_P=W_P, W_F=W_F, dPi=dPi, W_P0=W_P0, sig_adm=sig_adm, tau_adm=tau_adm,
           dets=[abs(np.linalg.det(system(x, 0.0)[0])) for x in (phi_n, phi_k)])
json.dump(res, open(os.path.join(HERE, "calc_v17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
np.savez(os.path.join(HERE, "calc_v17.npz"), phs=phs, X0=X0, X1=X1, OM=OM, EP=EP, SIG=SIG, MD=MDv,
         phi_ob=phi_ob, phi_y=phi_y, phi_n=phi_n, phi_k=phi_k)

# ---------------- печать
pr = lambda *a: print(*a)
pr(f"окно {phi_n:.3f}→{phi_k:.3f}, φоб {phi_ob:.3f}, φу {phi_y:.3f}; ω {w:.3f}, εр {eps_r:.4f}, εт {eps_t:.4f}")
pr(f"m1 {m1:.4f} zS {zS*1000:.2f} JO {JO:.5f} JS {JS:.5f} m3 {m3:.4f}; G1 {G1:.3f} G3 {G3:.3f}; q_m {q_m:.4f}")
for r in rows:
    x0, x1 = r["X0"], r["X1"]
    pr(f"{r['name'][:38]:38s} φ={r['phi']:.2f} F={r['F']:.1f} ω={r['om']:.3f} ε={r['ep']:+.3f} | Ф1τ={r['Ft1']:+.4f} Ф1n={r['Fn1']:.4f} "
       f"Ф1x={r['F1x']:+.4f} Ф1y={r['F1y']:+.4f} MФ1={r['MF1']:+.5f} aDy={r['aDy']*1000:+.1f} Ф3={r['F3y']:+.4f}")
    pr(f"   P {x0[8]:.2f}→{x1[8]:.2f} (an {r['P_an']:.2f}) R12N {x0[2]:.1f}→{x1[2]:.1f} R10x {x0[0]:.1f}→{x1[0]:.1f} R10y {x0[1]:.1f}→{x1[1]:.1f} "
       f"|R10| {r['R10_0']:.1f}→{r['R10_1']:.1f} R30N {x0[6]:.1f}→{x1[6]:.1f} M12 {x1[3]:.2e} M30 {x1[7]:.2e}")
    b1 = r["beam1"]
    pr(f"   кулиса: N {r['N0']:.2f}→{b1['N']:.2f}  MD {r['MD0']:.3f}→{b1['MD']:.3f} Н·м  σ {r['sig0']:.2f}→{b1['sig']:.2f}  τ {b1['tau']:.2f}")
pr(f"P max {X0[:,8].max():.2f} → {P1max:.2f} at {phP:.2f}; P min {P1min:.2f} at {phPmin:.2f}; idle P {P_idle}; idle R12N {R12_idle}")
pr(f"R12N max {R12max:.1f} at {ph12:.2f}; |R10| max {R10max:.1f} at {ph10:.2f}; |R30N| {R30max:.1f}; |R10y| {R10ymax:.1f} at {ph10y:.2f}")
pr(f"σ max {sig1max:.2f} at {phsig:.3f} (доп {sig_adm}); τ max {tau1max:.2f} (доп {tau_adm}); p max {p1max:.2f}; rod_ok {rod_ok}")
pr(f"analytic err {err_an:.2e}; W_P {W_P:.4f} J  W_F {W_F:.4f}  ΔП {dPi:.4f}  W_F−ΔП {W_F-dPi:.4f}; W_P0 {W_P0:.4f}")
