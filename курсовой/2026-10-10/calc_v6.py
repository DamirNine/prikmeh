# -*- coding: utf-8 -*-
"""Расчёт v6: компромисс A–ψ (равные относительные уступки), проекции на оси ДСК, первичный силовой расчёт."""
import numpy as np
from math import radians, degrees, tan, atan, cos, sin, log, pi

out = []
def p(*a):
    out.append(" ".join(str(x) for x in a))

# ---------------- 1. A_min(ψ) и угловой ход
S, Sob, F_UK, P_HAND = 16.0, 6.0, 1974.0, 120.0
Lmax, emin, phimax = 500.0, 10.0, 60.0

def best_for_psi(psi, n=40001):
    pk = np.linspace(0.0, phimax - psi, n)
    pn = pk + psi
    d = np.tan(np.radians(pn)) - np.tan(np.radians(pk))
    e = S / d
    phob = np.degrees(np.arctan(np.tan(np.radians(pk)) + Sob / e))
    L = F_UK * e / (P_HAND * np.cos(np.radians(phob)) ** 3)
    ok = (e >= emin - 1e-9) & (L <= Lmax + 1e-9)
    if not ok.any():
        return None
    A = 0.5 * e * S
    i = int(np.argmin(np.where(ok, A, np.inf)))
    return dict(psi=psi, pk=pk[i], pn=pn[i], e=e[i], A=A[i], phob=phob[i], L=L[i])

grid = np.round(np.arange(29.30, 58.00001, 0.01), 2)
rows = [r for r in (best_for_psi(x, 8001) for x in grid) if r]
ps = np.array([r['psi'] for r in rows]); A = np.array([r['A'] for r in rows]); E_ = np.array([r['e'] for r in rows])
psi_star, A_star = ps.min(), A.min()
dA = A / A_star - 1.0; dpsi = ps / psi_star - 1.0
diff = dA - dpsi
i = int(np.where(np.diff(np.sign(diff)) != 0)[0][0])
psi_c = ps[i] - diff[i] * (ps[i + 1] - ps[i]) / (diff[i + 1] - diff[i])
rc = best_for_psi(psi_c)
p(f"psi*={psi_star:.2f} A*={A_star:.2f}; crossing psi_c={psi_c:.2f}: A={rc['A']:.2f} e={rc['e']:.3f} pk={rc['pk']:.2f} pn={rc['pn']:.2f} L={rc['L']:.1f} concession={100*(rc['A']/A_star-1):.1f}% / {100*(psi_c/psi_star-1):.1f}%")
for x in (30, 35, 37.06, 40, 45, 50, 52.48):
    r = best_for_psi(x)
    p(f"  psi={x:5.2f}: A={r['A']:7.2f} e={r['e']:6.3f} dA={100*(r['A']/A_star-1):6.1f}% dpsi={100*(x/psi_star-1):6.1f}%")
# минимальный ψ для e = 12 мм при φн ≤ 60°
e12 = 12.0
pk12 = degrees(atan(tan(radians(60)) - S / e12)); psi12 = 60 - pk12
phob12 = degrees(atan(tan(radians(pk12)) + Sob / e12)); L12 = F_UK * e12 / (P_HAND * cos(radians(phob12)) ** 3)
p(f"e=12: min psi={psi12:.2f} (window 60 -> {pk12:.2f}), phob={phob12:.2f}, L={L12:.1f}, P(L=500)={F_UK*e12/(500*cos(radians(phob12))**3):.1f}")
np.savez("amin_v6.npz", ps=ps, A=A, e=E_, psi_star=psi_star, A_star=A_star, psi_c=psi_c, A_c=rc['A'], e_c=rc['e'])

# ---------------- 2. Принятый механизм
e, L = 12.0, 500.0
phi_k = 19.29
tk = tan(radians(phi_k))
phi_n = degrees(atan(tk + S / e)); phi_ob = degrees(atan(tk + Sob / e))
sig_t, E = 415.0, 2.1e5
Dk, Dobzh, s, n_coef = 32.10, 28.6, 0.22, 2.0
k5 = 1.05
eps_y = sig_t / E; dr_y = eps_y * Dk / 2; tg_a = ((Dk - Dobzh) / 2) / Sob; d_y = dr_y / tg_a
phi_y = degrees(atan(tk + (Sob - d_y) / e))
A_sk = pi * (Dobzh - s) * s
lnD = log(Dk / Dobzh)
A_pr = n_coef * A_sk * lnD
F_t = sig_t * A_pr; F_max = k5 * sig_t * A_pr
C = F_t / d_y; k_h = (F_max - F_t) / (Sob - d_y)
eps_max = lnD; E_t = (k5 * sig_t - sig_t) / (eps_max - eps_y)
p(f"phi_n={phi_n:.3f} phi_ob={phi_ob:.3f} phi_y={phi_y:.3f} phi_k={phi_k:.3f}; d_y={d_y:.4f} tg_a={tg_a:.4f}")
p(f"A_sk={A_sk:.3f} lnD={lnD:.5f} A_pr={A_pr:.4f} F_t={F_t:.1f} F_max={F_max:.1f} C={C:.0f} N/mm k={k_h:.2f} N/mm; eps_max={eps_max:.4f} E_t={E_t:.1f} MPa")

def F_of_phi(ph):
    ph = np.asarray(ph, float)
    y_ob = e * tan(radians(phi_ob))
    dl = y_ob - e * np.tan(np.radians(ph))          # внедрение головки в крышку, мм
    Fv = np.where(dl <= 0, 0.0, np.where(dl <= d_y, C * dl, F_t + k_h * (dl - d_y)))
    return Fv, dl

def forces(ph):
    ph = np.asarray(ph, float)
    Fv, dl = F_of_phi(ph)
    c, sn, t = np.cos(np.radians(ph)), np.sin(np.radians(ph)), np.tan(np.radians(ph))
    N = Fv / c                                       # R12N = R21N
    P_ = Fv * e / (L * c ** 3)
    R10x = Fv * t; R10y = P_ - Fv
    R23x = -Fv * t; R23y = Fv
    R32x, R32y = Fv * t, -Fv
    R30 = -Fv * t
    return dict(F=Fv, dl=dl, N=N, P=P_, R10x=R10x, R10y=R10y, R10=np.hypot(R10x, R10y), R23x=R23x, R23y=R23y, R32x=R32x, R32y=R32y, R30=R30)

# проверка равновесия механизма в целом и моментов относительно произвольной точки H
for ph in (phi_y, 30.0, phi_k):
    d = forces(ph); c, sn = cos(radians(ph)), sin(radians(ph))
    xD, yD = e, e * tan(radians(ph)); xK, yK = L * c, L * sn
    for xH, yH in ((0, 0), (-40, 300), (123, -77)):
        M = d['R10x'] * (0 - yH) * (-1) * (-1)  # placeholder
        M = (0 - xH) * d['R10y'] - (0 - yH) * d['R10x'] \
            + (xD - xH) * (d['N'] * c) - (yD - yH) * (-d['N'] * sn) \
            + (xK - xH) * (-d['P'])
        assert abs(M) < 1e-6 * max(1, d['F']), (ph, xH, yH, M)
    fx = d['R10x'] + d['R30']; fy = d['R10y'] + d['F'] - d['P']
    assert abs(fx) < 1e-9 and abs(fy) < 1e-9
p("checks: moments about arbitrary H = 0, whole-mechanism equilibrium OK")

rows_t = [("начало хода", phi_n), ("касание с крышкой", phi_ob), ("начало пластической деформации", phi_y),
          ("середина пластического участка", 30.0), ("конец хода", phi_k)]
p("Таблица сил (кв.-статика):")
for name, ph in rows_t:
    d = forces(ph)
    p(f"  {name:32s} φ={ph:6.2f} δ={float(d['dl']):6.3f} F={float(d['F']):7.1f} P={float(d['P']):6.1f} N={float(d['N']):7.1f} "
      f"R10x={float(d['R10x']):7.1f} R10y={float(d['R10y']):8.1f} |R10|={float(d['R10']):7.1f} R23x={float(d['R23x']):7.1f} R23y={float(d['R23y']):7.1f} R30={float(d['R30']):7.1f}")
phs = np.linspace(phi_n, phi_k, 200001)
d = forces(phs)
for key in ("F", "P", "N", "R10x", "R10y", "R10", "R30"):
    v = d[key]; j = int(np.argmax(np.abs(v)))
    p(f"  max|{key}| = {abs(v[j]):.1f} at φ={phs[j]:.3f}")
np.savez("forces_v6.npz", phi=phs, **{k: v for k, v in d.items()},
         phi_n=phi_n, phi_ob=phi_ob, phi_y=phi_y, phi_k=phi_k, F_t=F_t, F_max=F_max, d_y=d_y, C=C, k_h=k_h, A_pr=A_pr,
         eps_y=eps_y, eps_max=eps_max, sig_t=sig_t, E_t=E_t)

# ---------------- 3. Проекции на оси ДСК (характерные положения) — аналоги
for name, ph in (("начало хода", phi_n), ("касание", phi_ob), ("конец хода", phi_k)):
    f = radians(ph); c, sn = cos(f), sin(f)
    p(f"  {name:12s} φ={ph:.2f}: VqDx=0 VqDy={-e/c**2:.2f} aqDx=0 aqDy={2*e*sn/c**3:.2f} | VqKx={L*sn:.1f} VqKy={-L*c:.1f} aqKx={-L*c:.1f} aqKy={-L*sn:.1f}")

open("calc_v6_out.txt", "w", encoding="utf-8").write("\n".join(out))
