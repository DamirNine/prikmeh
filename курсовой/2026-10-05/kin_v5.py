# -*- coding: utf-8 -*-
"""Закон движения кулисы: разгон (холостой ход) → постоянная скорость (упругая деформация крышки) → торможение (пластическая деформация)."""
import numpy as np
from math import radians, degrees, tan, atan, cos, sin
e, L = 12.0, 500.0
phi_k, S, S_OB = 19.29, 16.0, 6.0
sig_t, E = 415.0, 2.1e5
Dk, Dobzh = 32.10, 28.6
v_max = 700.0                                    # мм/с
eps_y = sig_t/E; dr_y = eps_y*Dk/2; tg_a = ((Dk - Dobzh)/2)/S_OB; d_y = dr_y/tg_a
tk = tan(radians(phi_k))
phi_n = degrees(atan(tk + S/e)); phi_ob = degrees(atan(tk + S_OB/e)); phi_y = degrees(atan(tk + (S_OB - d_y)/e))
psi = radians(phi_n - phi_k); psi_xx = radians(phi_n - phi_ob); psi_u = radians(phi_ob - phi_y); psi_pl = radians(phi_y - phi_k)
w = v_max/L
t_r, t_u, t_t = 2*psi_xx/w, psi_u/w, 2*psi_pl/w
eps_r, eps_t = w/t_r, -w/t_t
T = t_r + t_u + t_t
print(f"eps_y={eps_y:.6f} dr_y={dr_y:.4f} tg_a={tg_a:.4f} alpha={degrees(atan(tg_a)):.2f} d_y={d_y:.4f}")
print(f"phi_n={phi_n:.2f} phi_ob={phi_ob:.2f} phi_y={phi_y:.2f} psi_xx={degrees(psi_xx):.2f} psi_u={degrees(psi_u):.3f} psi_pl={degrees(psi_pl):.2f} (rad {psi_xx:.4f} {psi_u:.5f} {psi_pl:.4f})")
print(f"w={w:.3f} t_r={t_r:.4f} t_u={t_u:.4f} t_t={t_t:.4f} T={T:.4f} eps_r={eps_r:.3f} eps_t={eps_t:.3f}")
print(f"check psi = {degrees(0.5*w*t_r + w*t_u + 0.5*w*t_t):.3f}; v_sr = {L*psi/T:.1f} mm/s")
t = np.linspace(0, T, 8001)
om = np.where(t < t_r, eps_r*t, np.where(t < t_r + t_u, w, w + eps_t*(t - t_r - t_u)))
ep = np.where(t < t_r, eps_r, np.where(t < t_r + t_u, 0.0, eps_t))
q = np.where(t < t_r, 0.5*eps_r*t**2, np.where(t < t_r + t_u, 0.5*eps_r*t_r**2 + w*(t - t_r),
     0.5*eps_r*t_r**2 + w*t_u + w*(t - t_r - t_u) + 0.5*eps_t*(t - t_r - t_u)**2))
phi = radians(phi_n) - q
Vq = -e/np.cos(phi)**2; Aq = 2*e*np.sin(phi)/np.cos(phi)**3
y = e*np.tan(phi); V = om*Vq; A = om**2*Aq + ep*Vq
i = np.argmax(np.abs(V)); j = np.argmax(np.abs(A))
print(f"y {y[0]:.2f}->{y[-1]:.2f}; max|V|={abs(V[i]):.1f} at t={t[i]:.3f} phi={degrees(phi[i]):.2f}; max|A|={abs(A[j]):.1f} at t={t[j]:.3f} phi={degrees(phi[j]):.2f}")
def state(ph_deg, om_v, ep_v):
    f = radians(ph_deg); c, s = cos(f), sin(f)
    vq, aq = -e/c**2, 2*e*s/c**3; vr = om_v*e*s/c**2
    return dict(V=om_v*vq, A=om_v**2*aq + ep_v*vq, VK=om_v*L/1000, aKt=ep_v*L/1000, aKn=om_v**2*L/1000, Vr=vr, ak=2*om_v*vr)
for name, ph, om_v, ep_v, tt in (("начало хода", phi_n, 0, eps_r, 0), ("касание (до)", phi_ob, w, eps_r, t_r), ("касание (после)", phi_ob, w, 0, t_r),
                                 ("нач. пласт. (до)", phi_y, w, 0, t_r + t_u), ("нач. пласт. (после)", phi_y, w, eps_t, t_r + t_u), ("конец хода", phi_k, 0, eps_t, T)):
    d = state(ph, om_v, ep_v)
    print(f"{name:20s} t={tt:.4f} φ={ph:.2f} ω={om_v:.2f} ε={ep_v:+.2f} | V_D={d['V']:+.1f} a_D={d['A']:+.1f} | V_K={d['VK']:.3f} aτ={d['aKt']:+.3f} an={d['aKn']:.3f} | Vr={d['Vr']:.1f} ak={d['ak']:.1f}")
np.savez("kin_v5.npz", t=t, om=om, ep=ep, phi=np.degrees(phi), y=y, V=V, A=A, t_r=t_r, t_u=t_u, t_t=t_t)
