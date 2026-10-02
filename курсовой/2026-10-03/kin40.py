# -*- coding: utf-8 -*-
"""Кинематика варианта ψ ≤ 40°: e = 12, L = 500, φ: 59,29° → 19,29°; закон ω(t) — трапеция."""
import numpy as np
from math import radians, degrees, tan, cos, sin, atan, pi
F, P, S, SOB = 1974.0, 120.0, 16.0, 6.0
e, L = 12.0, 500.0
phi_k = 19.29; phi_n = degrees(atan(tan(radians(phi_k)) + S/e))
phi_ob = degrees(atan(tan(radians(phi_k)) + SOB/e))
psi = radians(phi_n - phi_k); psi_t = radians(phi_ob - phi_k); psi_xx = radians(phi_n - phi_ob)
s_K = L*psi                      # путь конца рукояти, мм
v_sr, v_max = 350.0, 700.0       # мм/с — Фех, Эргономика, с. 46
t_rx = s_K / v_sr                # время рабочего хода
w = v_max / L                    # ω_max
t_t = 2*psi_t / w                # торможение — на обжиме (от начала деформации)
rest = t_rx - t_t
t_r = 2*(rest - psi_xx/w); t_u = rest - t_r
if t_u < 0:                      # площадка вырождается: разгон на всём холостом ходе
    t_u = 0.0; t_r = 2*psi_xx/w
eps_r, eps_t = w/t_r, -w/t_t
print(f"phi_n={phi_n:.2f} phi_ob={phi_ob:.2f} phi_k={phi_k:.2f} psi={degrees(psi):.2f} psi_xx={degrees(psi_xx):.2f} psi_t={degrees(psi_t):.2f}")
print(f"s_K={s_K:.1f} мм  t_rx(по v_ср)={t_rx:.3f} с  w_max={w:.3f} рад/с")
print(f"t_r={t_r:.3f} t_u={t_u:.3f} t_t={t_t:.3f}  сумма={t_r+t_u+t_t:.3f}  eps_r={eps_r:.3f} eps_t={eps_t:.3f}")
print(f"проверка psi: {0.5*w*t_r + w*t_u + 0.5*w*t_t:.4f} рад = {degrees(0.5*w*t_r + w*t_u + 0.5*w*t_t):.2f}°")
# законы движения
T = t_r + t_u + t_t
t = np.linspace(0, T, 4001)
om = np.where(t < t_r, eps_r*t, np.where(t < t_r + t_u, w, w + eps_t*(t - t_r - t_u)))
ep = np.where(t < t_r, eps_r, np.where(t < t_r + t_u, 0.0, eps_t))
q = np.where(t < t_r, 0.5*eps_r*t**2, np.where(t < t_r + t_u, 0.5*eps_r*t_r**2 + w*(t - t_r),
     0.5*eps_r*t_r**2 + w*t_u + w*(t - t_r - t_u) + 0.5*eps_t*(t - t_r - t_u)**2))
phi = radians(phi_n) - q
Vq = -e/np.cos(phi)**2                    # dy/dq (q = φн − φ)
Aq = 2*e*np.sin(phi)/np.cos(phi)**3       # d²y/dq²
y = e*np.tan(phi); V = om*Vq; A = om**2*Aq + ep*Vq
i = np.argmax(np.abs(V)); j = np.argmax(np.abs(A))
print(f"y: {y[0]:.2f} -> {y[-1]:.2f} (ход {y[0]-y[-1]:.2f} мм)")
print(f"max|V_D| = {abs(V[i]):.1f} мм/с при t={t[i]:.3f} с, φ={degrees(phi[i]):.2f}°;  max|a_D| = {abs(A[j]):.1f} мм/с² при t={t[j]:.3f}, φ={degrees(phi[j]):.2f}°")
def at(tt, side=0):
    k = np.searchsorted(t, tt) + side; k = min(max(k, 0), len(t)-1)
    return dict(t=t[k], phi=degrees(phi[k]), om=om[k], ep=ep[k], V=V[k], A=A[k], VK=om[k]*L, aKt=ep[k]*L, aKn=om[k]**2*L,
                lAC=e/cos(phi[k]), Vr=om[k]*e*sin(phi[k])/cos(phi[k])**2)
for name, tt, side in (("начало хода", 0, 0), ("начало обжима (до)", t_r + t_u, -1), ("начало обжима (после)", t_r + t_u, 1), ("конец хода", T, 0)):
    d = at(tt, side)
    print(f"{name:22s} t={d['t']:.3f} φ={d['phi']:.2f}° ω={d['om']:.3f} ε={d['ep']:+.3f} | D: V={d['V']:+.1f} мм/с a={d['A']:+.1f} мм/с² | K: V={d['VK']/1000:.3f} м/с aτ={d['aKt']/1000:+.3f} an={d['aKn']/1000:.3f} м/с² | C: l={d['lAC']:.2f} aτ={d['ep']*d['lAC']:+.1f} an={d['om']**2*d['lAC']:.1f} мм/с² | V_отн={d['Vr']:.1f} a_кор={2*d['om']*d['Vr']:.1f}")
np.savez("kin40.npz", t=t, om=om, ep=ep, phi=np.degrees(phi), y=y, V=V, A=A, t_r=t_r, t_u=t_u, t_t=t_t)
