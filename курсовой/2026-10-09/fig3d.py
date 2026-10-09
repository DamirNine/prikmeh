# -*- coding: utf-8 -*-
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
from matplotlib.ticker import FuncFormatter
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5})
F, P, S, SOB, LMAX, EMIN, PHIMAX = 1974.0, 120.0, 16.0, 6.0, 500.0, 10.0, 60.0
psi = np.arange(25.0, 60.0001, 0.25)
pk = np.arange(-20.0, 50.0001, 0.25)
PSI, PK = np.meshgrid(psi, pk, indexing="xy")
PN = PK + PSI
dt = np.tan(np.radians(np.minimum(PN, 89.0))) - np.tan(np.radians(PK))
E = S/dt
A = 0.5*E*S
tob = np.tan(np.radians(PK)) + SOB/E
worst = np.maximum(np.abs(PK), np.abs(np.degrees(np.arctan(tob))))
L = F*E/(P*np.cos(np.radians(worst))**3)
ok = (PN <= PHIMAX + 1e-9) & (E >= EMIN - 1e-9) & (L <= LMAX + 1e-9)
ZMAX = 300.0
Z = np.minimum(A, ZMAX)
# минимум по φк для каждого ψ
amin, pkmin = [], []
for j in range(psi.size):
    col = np.where(ok[:, j], A[:, j], np.inf); i = int(np.argmin(col))
    amin.append(col[i]); pkmin.append(pk[i])
amin, pkmin = np.array(amin), np.array(pkmin)
comma = FuncFormatter(lambda v, p: f"{v:g}".replace(".", ",").replace("-", "−"))
norm = Normalize(70, ZMAX)
colors = cm.viridis_r(norm(Z))
colors[~ok] = (0.78, 0.79, 0.81, 0.45)        # недопустимая часть — серая
fig = plt.figure(figsize=(9.6, 7.0), dpi=200)
ax = fig.add_subplot(111, projection="3d")
ax.plot_surface(PSI, PK, Z, facecolors=colors, rstride=1, cstride=1, linewidth=0.15, edgecolor=(1, 1, 1, 0.15), shade=False, antialiased=True)
m = np.isfinite(amin)
ax.plot(psi[m], pkmin[m], amin[m] + 1.5, color="#c4372b", lw=2.4, zorder=10, label="A_min(ψ) — минимум по φк")
for ps_, lab, c in ((40.0, "ψ = 40°: A = 93,6 мм², e = 11,7 мм\n(принято)", "#eb6834"), (52.5, "ψ = 52,5°: A = 80,0 мм², e = 10,0 мм\n(абсолютный минимум)", "#2a78d6")):
    j = int(np.argmin(np.abs(psi - ps_)))
    ax.scatter([psi[j]], [pkmin[j]], [amin[j] + 3], s=60, color=c, edgecolor="white", linewidth=1.2, zorder=11, depthshade=False)
    ax.scatter([], [], [], s=60, color=c, edgecolor="white", label=lab.replace(chr(10), " "))
# граница φн = 60° на поверхности
bp = np.linspace(25, 60, 200); bk = 60 - bp
bt = np.tan(np.radians(60)) - np.tan(np.radians(bk)); bA = np.minimum(0.5*S*S/bt, ZMAX)
ax.plot(bp, bk, bA + 1.0, color="#0b0b0b", lw=1.2, ls=(0, (4, 3)), zorder=9, label="граница φн = 60°")
ax.set_xlabel("угловой ход ψ, град", labelpad=8); ax.set_ylabel("конечный угол φк, град", labelpad=8)
ax.set_zlabel("площадь A, мм²   (e = A/8, мм)", labelpad=8)
ax.set_zlim(60, ZMAX); ax.set_xlim(25, 60); ax.set_ylim(-20, 45)
for a in (ax.xaxis, ax.yaxis, ax.zaxis): a.set_major_formatter(comma)
ax.view_init(elev=34, azim=-58)
ax.set_title("Площадь треугольника O–Bн–Bк в зависимости от ψ и φк (S = 16 мм)", loc="left", fontsize=11, fontweight="bold")
sm = cm.ScalarMappable(norm=norm, cmap="viridis_r"); sm.set_array([])
cb = fig.colorbar(sm, ax=ax, shrink=0.55, pad=0.08); cb.set_label("A, мм² (допустимая область)"); cb.ax.yaxis.set_major_formatter(comma)
ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.97), frameon=False, fontsize=8.8)
fig.text(0.02, 0.03, "Серым — недопустимые сочетания: φн > 60°, e < 10 мм или L > 500 мм (P = 120 Н, Fук = 1974 Н). Площадь выше 300 мм² срезана.", fontsize=8.5, color="#52514e")
fig.savefig("fig_area_3d.png", facecolor="white", bbox_inches="tight", pad_inches=0.15)
print("ok", [(p, round(a, 1), round(k, 2)) for p, a, k in zip(psi, amin, pkmin) if p in (30, 35, 40, 45, 50, 52.5)])
