# -*- coding: utf-8 -*-
"""v7: система 9 уравнений (моменты относительно точки M).
Неизвестные: R10x, R10y, R12N, M12, R23x, R23y, R30N, M30, P (сила руки) — все функции угла φ; L — параметр.
Требуемая длина рукояти при допустимой силе руки P_доп = 120 Н: L_треб(φ) = F(φ)·e/(P_доп·cos³φ); L_проект = max → ГОСТ 6636."""
import numpy as np
from math import radians, degrees, tan, atan, cos, sin, log, pi

out = []
def p(*a):
    out.append(" ".join(str(x) for x in a))

e, S, Sob, phi_k = 12.0, 16.0, 6.0, 19.29
P_dop = 120.0
xM, yM = 50.0, 500.0          # точка O правее M на x_M и ниже на y_M
tk = tan(radians(phi_k))
phi_n = degrees(atan(tk + S / e)); phi_ob = degrees(atan(tk + Sob / e))
sig_t, E, Dk, Dobzh, s_, n_ = 415.0, 2.1e5, 32.10, 28.6, 0.22, 2.0
eps_y = sig_t / E; d_y = (eps_y * Dk / 2) / (((Dk - Dobzh) / 2) / Sob)
phi_y = degrees(atan(tk + (Sob - d_y) / e))
A_pr = n_ * pi * (Dobzh - s_) * s_ * log(Dk / Dobzh)
F_t, F_max = sig_t * A_pr, 1.05 * sig_t * A_pr
C, k_h = F_t / d_y, (F_max - F_t) / (Sob - d_y)

def F_of(ph):
    dl = e * tan(radians(phi_ob)) - e * tan(radians(ph))
    if dl <= 0:
        return 0.0
    return C * dl if dl <= d_y else F_t + k_h * (dl - d_y)

NAMES = ["R10x", "R10y", "R12N", "M12", "R23x", "R23y", "R30N", "M30", "P"]

def system(ph, F, L):
    c, s, t = cos(radians(ph)), sin(radians(ph)), tan(radians(ph))
    XD, YD = xM + e, yM - e * t                  # плечи точки D от M (вправо, вниз)
    XK = xM + L * c                              # плечо точки K по горизонтали
    a = XD * c - YD * s
    A = np.zeros((9, 9)); B = np.zeros(9)
    A[0, [0, 2]] = [1, -s]                                   # зв.1 ΣFx
    A[1, [1, 2, 8]] = [1, c, -1]                             # зв.1 ΣFy
    A[2, [0, 1, 2, 3, 8]] = [yM, xM, a, 1, -XK]              # зв.1 ΣM_M
    A[3, [2, 4]] = [s, 1]                                    # зв.2 ΣFx
    A[4, [2, 5]] = [-c, 1]                                   # зв.2 ΣFy
    A[5, [2, 3, 4, 5]] = [-a, -1, YD, XD]                    # зв.2 ΣM_M
    A[6, [4, 6]] = [-1, 1]                                   # зв.3 ΣFx
    A[7, 5] = -1;                     B[7] = -F              # зв.3 ΣFy
    A[8, [4, 5, 6, 7]] = [-YD, -XD, YD, 1]; B[8] = -F * XD   # зв.3 ΣM_M
    return A, B

def closed(ph, F, L):
    c, t = cos(radians(ph)), tan(radians(ph))
    Pv = F * e / (L * c ** 3)
    return np.array([F * t, Pv - F, F / c, 0.0, -F * t, F, -F * t, 0.0, Pv])

# ---------------- 1) требуемая длина рукояти
phs = np.linspace(phi_n, phi_k, 40001)
Fv = np.array([F_of(x) for x in phs])
Lreq = Fv * e / (P_dop * np.cos(np.radians(phs)) ** 3)
iL = int(np.argmax(Lreq)); L_max = Lreq[iL]; ph_Lmax = phs[iL]
L_des = 450.0
p(f"phi_n={phi_n:.3f} phi_ob={phi_ob:.3f} phi_y={phi_y:.3f}; F_t={F_t:.1f} F_max={F_max:.1f}")
p(f"L_req max={L_max:.2f} at phi={ph_Lmax:.3f}; L_design={L_des} (Ra20); at end L_req={Lreq[-1]:.1f}; at 30deg {F_of(30.0)*e/(P_dop*cos(radians(30))**3):.1f}")

# ---------------- 2) система при L = 450
X = np.zeros((phs.size, 9)); dets = []
for i, ph in enumerate(phs):
    A, B = system(ph, Fv[i], L_des)
    X[i] = np.linalg.solve(A, B)
    if i % 4000 == 0:
        dets.append(abs(np.linalg.det(A)))
    assert np.allclose(X[i], closed(ph, Fv[i], L_des), atol=1e-6 * max(1.0, Fv[i])), (ph, X[i])
p("system solved for", phs.size, "angles; = closed form; |det| from", round(min(dets), 1), "to", round(max(dets), 1))
for xm2, ym2 in ((0.0, 450.0), (120.0, 900.0)):
    xM0, yM0 = xM, yM; xM, yM = xm2, ym2
    A, B = system(phi_y, F_t, L_des); X2 = np.linalg.solve(A, B)
    xM, yM = xM0, yM0
    assert np.allclose(X2, closed(phi_y, F_t, L_des)), X2
p("independent of M: ok")
j = int(np.argmax(X[:, 8]))
p(f"P max={X[j,8]:.2f} at phi={phs[j]:.3f}; P_end={X[-1,8]:.2f}")
for name, ph in (("начало хода", phi_n), ("касание", phi_ob), ("нач. пласт.", phi_y), ("30", 30.0), ("конец хода", phi_k)):
    F = F_of(ph); A, B = system(ph, F, L_des); x = np.linalg.solve(A, B)
    p(f"  {name:12s} φ={ph:6.2f} F={F:7.1f} | " + " ".join(f"{n}={v:9.2f}" for n, v in zip(NAMES, x)) + f" | |R10|={np.hypot(x[0], x[1]):.1f}")
A, B = system(phi_y, F_t, L_des)
np.set_printoptions(linewidth=220, suppress=True, precision=3)
p("A(phi_y)=\n" + str(A)); p("B(phi_y)=" + str(B))
c_ = cos(radians(phi_y)); t_ = tan(radians(phi_y)); XD = xM + e; YD = yM - e * t_
p(f"at phi_y: XD={XD:.2f} YD={YD:.3f} a={XD*c_ - YD*sin(radians(phi_y)):.3f} XK={xM + L_des*c_:.2f}")
np.savez("forces_v7.npz", phi=phs, X=X, F=Fv, Lreq=Lreq, phi_n=phi_n, phi_ob=phi_ob, phi_y=phi_y, phi_k=phi_k,
         L_max=L_max, ph_Lmax=ph_Lmax, L_des=L_des, P_dop=P_dop, xM=xM, yM=yM, F_t=F_t, F_max=F_max)

# окно ψ = 38,26° для сравнения (п. 6.6)
pk2 = degrees(atan(tan(radians(60)) - S / e)); phy2 = degrees(atan(tan(radians(pk2)) + (Sob - d_y) / e))
p(f"psi=38.26 window: phi_k={pk2:.2f} phi_y={phy2:.2f} L_req max={F_t*e/(P_dop*cos(radians(phy2))**3):.1f}")
# оценка инерции/веса стальной рукояти 20x8 мм, L = 450
m = 7850 * 0.02 * 0.008 * L_des / 1000; J = m * (L_des / 1000) ** 2 / 3
p(f"handle m={m:.3f} kg J={J:.4f} J*eps(3.66)={J*3.663:.3f} N*m -> dP={J*3.663/((L_des/1000)*cos(radians(phi_n))):.2f} N; weight {m*9.81:.2f} N -> dP={m*9.81/2:.2f} N")
open("calc_v7_out.txt", "w", encoding="utf-8").write("\n".join(out))
