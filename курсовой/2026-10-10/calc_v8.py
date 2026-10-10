# -*- coding: utf-8 -*-
"""v8: принят угловой ход в точке равных уступок ψ = 36,75°, e = 12,53 мм. Пересчёт всех углов, кинематики (L по max L_треб), сил."""
import numpy as np
from math import radians, degrees, tan, atan, cos, sin, log, pi, hypot
from scipy.optimize import brentq

out = []
def p(*a):
    out.append(" ".join(str(x) for x in a))

S, Sob, e, psi = 16.0, 6.0, 12.53, 36.75
P_dop, xM, yM = 120.0, 50.0, 500.0
sig_t, E, Dk, Dobzh, s_, n_ = 415.0, 2.1e5, 32.10, 28.6, 0.22, 2.0
eps_y = sig_t / E; dr_y = eps_y * Dk / 2; tg_a = ((Dk - Dobzh) / 2) / Sob; d_y = dr_y / tg_a
A_pr = n_ * pi * (Dobzh - s_) * s_ * log(Dk / Dobzh); F_t = sig_t * A_pr; F_max = 1.05 * F_t
C, k_h = F_t / d_y, (F_max - F_t) / (Sob - d_y)

# ---------------- окно
f = lambda pk: tan(radians(pk + psi)) - tan(radians(pk)) - S / e
phi_k = brentq(f, 0.0, 60 - psi); phi_n = phi_k + psi
tk = tan(radians(phi_k))
phi_ob = degrees(atan(tk + Sob / e)); phi_y = degrees(atan(tk + (Sob - d_y) / e))
psi_xx, psi_u, psi_pl = phi_n - phi_ob, phi_ob - phi_y, phi_y - phi_k
A_tri = 0.5 * e * S
p(f"window: phi_n={phi_n:.3f} phi_k={phi_k:.3f} psi={psi}; phi_ob={phi_ob:.3f} phi_y={phi_y:.3f}; A={A_tri:.2f}")
p(f"  check S = e(tg phi_n - tg phi_k) = {e*(tan(radians(phi_n))-tk):.4f}")
p(f"  psi_xx={psi_xx:.3f}° ({radians(psi_xx):.4f} rad) psi_u={psi_u:.3f}° ({radians(psi_u):.5f} rad) psi_pl={psi_pl:.3f}° ({radians(psi_pl):.4f} rad)")
p(f"  y_D: start {e*tan(radians(phi_n)):.3f}, contact {e*tan(radians(phi_ob)):.3f}, end {e*tk:.3f}; lOD start {e/cos(radians(phi_n)):.2f} end {e/cos(radians(phi_k)):.2f}")
L0 = F_max * e / (P_dop * cos(radians(phi_ob)) ** 3)
p(f"  L0 (F_uk at contact) = {L0:.1f}")

# ---------------- закон силы и требуемая длина
def F_of(ph):
    dl = e * tan(radians(phi_ob)) - e * tan(radians(ph))
    if dl <= 0:
        return 0.0
    return C * dl if dl <= d_y else F_t + k_h * (dl - d_y)
phs = np.linspace(phi_n, phi_k, 40001)
Fv = np.array([F_of(x) for x in phs])
Lreq = Fv * e / (P_dop * np.cos(np.radians(phs)) ** 3)
iL = int(np.argmax(Lreq)); L_max = Lreq[iL]; ph_Lmax = phs[iL]
L = 500.0
p(f"L_req max={L_max:.2f} at phi={ph_Lmax:.3f} -> L={L} (Ra10/Ra20); P_max = {P_dop*L_max/L:.2f}; L_req at end {Lreq[-1]:.1f}")

# ---------------- система 9 уравнений при L = 500
def system(ph, F):
    c, s, t = cos(radians(ph)), sin(radians(ph)), tan(radians(ph))
    XD, YD = xM + e, yM - e * t
    XK = xM + L * c
    a = XD * c - YD * s
    A = np.zeros((9, 9)); B = np.zeros(9)
    A[0, [0, 2]] = [1, -s]; A[1, [1, 2, 8]] = [1, c, -1]; A[2, [0, 1, 2, 3, 8]] = [yM, xM, a, 1, -XK]
    A[3, [2, 4]] = [s, 1]; A[4, [2, 5]] = [-c, 1]; A[5, [2, 3, 4, 5]] = [-a, -1, YD, XD]
    A[6, [4, 6]] = [-1, 1]; A[7, 5] = -1; B[7] = -F; A[8, [4, 5, 6, 7]] = [-YD, -XD, YD, 1]; B[8] = -F * XD
    return A, B
X = np.zeros((phs.size, 9)); dets = []
for i, ph in enumerate(phs):
    A_, B_ = system(ph, Fv[i]); X[i] = np.linalg.solve(A_, B_)
    if i % 4000 == 0:
        dets.append(abs(np.linalg.det(A_)))
    c = cos(radians(ph)); t = tan(radians(ph)); Pv = Fv[i] * e / (L * c ** 3)
    assert np.allclose(X[i], [Fv[i]*t, Pv - Fv[i], Fv[i]/c, 0, -Fv[i]*t, Fv[i], -Fv[i]*t, 0, Pv], atol=1e-6*max(1, Fv[i]))
p(f"system ok; |det| {min(dets):.1f}..{max(dets):.1f}; P max {X[:,8].max():.2f} at {phs[int(np.argmax(X[:,8]))]:.3f}")
rows = []
for name, ph in (("начало хода", phi_n), ("касание с крышкой", phi_ob), ("начало пластической деформации", phi_y), ("промежуточное", 30.0), ("конец хода", phi_k)):
    F = F_of(ph); A_, B_ = system(ph, F); x = np.linalg.solve(A_, B_)
    rows.append((name, ph, F, x))
    p(f"  {name:32s} φ={ph:7.3f} F={F:7.1f} P={x[8]:7.2f} R10x={x[0]:8.1f} R10y={x[1]:8.1f} |R10|={hypot(x[0],x[1]):7.1f} R12N={x[2]:7.1f} R23x={x[4]:8.1f} R23y={x[5]:7.1f} R30N={x[6]:8.1f}")
A_, B_ = system(phi_y, F_t)
c_ = cos(radians(phi_y)); t_ = tan(radians(phi_y)); XD = xM + e; YD = yM - e * t_
p(f"example at phi_y: XD={XD:.2f} YD={YD:.3f} XK={xM + L*c_:.2f} a={XD*c_ - YD*sin(radians(phi_y)):.3f}")
p(f"  M bending at D: {X[int(np.argmin(np.abs(phs-phi_y))),8]*(L*c_ - e)/1000:.2f} N*m; K height at start L*sin(phi_n)={L*sin(radians(phi_n)):.1f}")
np.savez("forces_v8.npz", phi=phs, X=X, F=Fv, Lreq=Lreq, phi_n=phi_n, phi_ob=phi_ob, phi_y=phi_y, phi_k=phi_k,
         L_max=L_max, ph_Lmax=ph_Lmax, L_des=L, P_dop=P_dop, xM=xM, yM=yM, F_t=F_t, F_max=F_max, e=e, eps_y=eps_y,
         eps_max=log(Dk / Dobzh), sig_t=sig_t, d_y=d_y, C=C, k_h=k_h)

# ---------------- аналоги (табл. 8) и K
p("Таблица 8:")
for name, ph in (("начало хода", phi_n), ("начало обжима", phi_ob), ("конец хода", phi_k)):
    f_ = radians(ph); c, s = cos(f_), sin(f_)
    p(f"  {name:14s} φ={ph:.2f} lOD={e/c:.2f} VqDy={-e/c**2:.2f} aqDy={2*e*s/c**3:.2f} Vqr={e*s/c**2:.2f} aqr={e*(1+s*s)/c**3:.2f} 2Vqr={2*e*s/c**2:.2f} F/P={L*c**3/e:.2f} | VqKx={L*s:.1f} VqKy={-L*c:.1f}")
p(f"  F/P at phi_y = {L*cos(radians(phi_y))**3/e:.2f}")

# ---------------- кинематика ω(t) при L = 500
v_max = 700.0; w = v_max / L
t_r, t_u, t_t = 2 * radians(psi_xx) / w, radians(psi_u) / w, 2 * radians(psi_pl) / w
eps_r, eps_t = w / t_r, -w / t_t; T = t_r + t_u + t_t; tp = t_r + t_u
p(f"KIN: w={w:.4f} t_r={t_r:.4f} t_u={t_u:.5f} t_t={t_t:.4f} T={T:.4f} eps_r={eps_r:.4f} eps_t={eps_t:.4f}")
p(f"  check psi = {degrees(0.5*w*t_r + w*t_u + 0.5*w*t_t):.3f}; sK = L*psi = {L*radians(psi):.1f}; v_sr = {L*radians(psi)/T:.1f} mm/s; lift L sin phi_n = {L*sin(radians(phi_n)):.1f}")
tt = np.linspace(0, T, 40001)
om = np.where(tt < t_r, eps_r * tt, np.where(tt < tp, w, w + eps_t * (tt - tp)))
ep = np.where(tt < t_r, eps_r, np.where(tt < tp, 0.0, eps_t))
q = np.where(tt < t_r, 0.5 * eps_r * tt ** 2, np.where(tt < tp, 0.5 * eps_r * t_r ** 2 + w * (tt - t_r),
             0.5 * eps_r * t_r ** 2 + w * t_u + w * (tt - tp) + 0.5 * eps_t * (tt - tp) ** 2))
ph_t = radians(phi_n) - q
VDy = om * (-e / np.cos(ph_t) ** 2); aDy = om ** 2 * (2 * e * np.sin(ph_t) / np.cos(ph_t) ** 3) + ep * (-e / np.cos(ph_t) ** 2)
Vr = om * e * np.sin(ph_t) / np.cos(ph_t) ** 2
i = int(np.argmin(VDy)); k = int(np.argmax(Vr))
p(f"  max|VDy|={-VDy[i]:.2f} at t={tt[i]:.3f} phi={degrees(ph_t[i]):.2f}; aDy(0)={aDy[0]:.2f}; Vr max={Vr[k]:.2f} at phi={degrees(ph_t[k]):.2f}")
def state(ph_deg, om_v, ep_v):
    f_ = radians(ph_deg); c, s = cos(f_), sin(f_)
    vq, aq = -e / c ** 2, 2 * e * s / c ** 3; vr = om_v * e * s / c ** 2
    return dict(V=om_v * vq, A=om_v ** 2 * aq + ep_v * vq, VK=om_v * L / 1000, aKt=ep_v * L / 1000, aKn=om_v ** 2 * L / 1000, Vr=vr, ak=2 * om_v * vr)
p("Таблица 9:")
for name, ph, om_v, ep_v, t0 in (("начало хода", phi_n, 0, eps_r, 0), ("касание (до)", phi_ob, w, eps_r, t_r), ("касание (после)", phi_ob, w, 0, t_r),
                                 ("нач. пласт. (до)", phi_y, w, 0, tp), ("нач. пласт. (после)", phi_y, w, eps_t, tp), ("конец хода", phi_k, 0, eps_t, T)):
    d = state(ph, om_v, ep_v)
    p(f"  {name:20s} t={t0:.4f} φ={ph:.2f} ω={om_v:.3f} ε={ep_v:+.3f} | VDy={d['V']:+.2f} aDy={d['A']:+.2f} | VK={d['VK']:.3f} aτ={d['aKt']:+.3f} an={d['aKn']:.3f} | Vr={d['Vr']:.2f} ak={d['ak']:.2f}")
np.savez("kin_v8.npz", t=tt, om=om, ep=ep, phi=np.degrees(ph_t), y=e*np.tan(ph_t), V=VDy, A=aDy, t_r=t_r, t_u=t_u, t_t=t_t)

# ---------------- нелинейность y(φ) относительно хорды
phg = np.linspace(radians(phi_k), radians(phi_n), 200001)
y = e * np.tan(phg); chord = e * tk + (phg - radians(phi_k)) * S / radians(psi)
dev = np.max(np.abs(chord - y))
p(f"nonlinearity: {dev:.3f} mm = {100*dev/S:.1f} % of stroke")
# инерция рукояти 500 мм
m = 7850 * 0.02 * 0.008 * 0.5; J = m * 0.5 ** 2 / 3
p(f"handle: m={m:.3f} J={J:.4f} J*eps={J*eps_r:.3f} N*m -> dP={J*eps_r/(0.5*cos(radians(phi_n))):.2f} N; weight {m*9.81:.2f} -> dP {m*9.81/2:.2f}")
open("calc_v8_out.txt", "w", encoding="utf-8").write("\n".join(out))
