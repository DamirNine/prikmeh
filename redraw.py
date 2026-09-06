# -*- coding: utf-8 -*-
# Перерисовка рисунков ДЗ по ПМ с учётом замечаний Подчасова:
# масштаб, базис в начале координат на всех рисунках, векторы везде где нужно,
# пространственные рисунки — только окрестность точки (не вся траектория) + базис + V,a.
# Равный аспект осей, эллипс 24x8 (настоящие пропорции), векторы в верных пропорциях.
# Запуск: py redraw.py  ->  media_fixed/
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from mpl_toolkits.mplot3d import Axes3D  # noqa
import os

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False
OUT = os.path.join(os.path.dirname(__file__), "media_fixed")
os.makedirs(OUT, exist_ok=True)
PI = np.pi
# рисуем на холсте побольше (фикс. размер шрифтов/линий в pt не меняется),
# а потом уменьшаем готовую картинку обратно — так цифры и стрелки выходят
# тоньше/мельче относительно сетки ("как на миллиметровке"), а итоговый размер картинки тот же
SCALE = 1.6

def ellipse_full():
    u = np.linspace(0, 2*PI, 600)
    return 24*np.cos(u), -8*np.sin(u)

def traj_traced():
    u = np.linspace(0, PI, 300)   # t: 0 -> 1
    return 24*np.cos(u), -8*np.sin(u)

def arrow(ax, base, tip, color="k", lw=2.2, label=None, loff=(0, 0), fs=15):
    ax.annotate("", xy=tip, xytext=base,
                arrowprops=dict(arrowstyle="-|>", lw=lw, color=color, mutation_scale=18))
    if label:
        ax.text((base[0]+tip[0])/2+loff[0], (base[1]+tip[1])/2+loff[1], label, fontsize=fs, color=color)

def decompose(ax, base, vx, vy, color, lx, ly, la, fs=14):
    # компоненты (vx вдоль x, vy вдоль y от base) + пунктирная рамка + итоговый вектор-диагональ
    p1 = (base[0]+vx, base[1]); p2 = (base[0], base[1]+vy); p3 = (base[0]+vx, base[1]+vy)
    arrow(ax, base, p1, color, lw=2.2, label=lx, loff=(0, -1.1), fs=fs)
    arrow(ax, base, p2, color, lw=2.2, label=ly, loff=(-1.5, 0.4), fs=fs)
    ax.plot([p1[0], p3[0]], [p1[1], p3[1]], "--", color="0.35", lw=1.1)
    ax.plot([p2[0], p3[0]], [p2[1], p3[1]], "--", color="0.35", lw=1.1)
    arrow(ax, base, p3, color, lw=2.8, label=la, loff=(0.4, 1.0), fs=fs)

def draw_basis(ax, kind, origin=(0, 0)):
    ax.plot(0, 0, "o", color="black", ms=6)
    ax.text(-1.6, -1.4, "O", fontsize=12, ha="center")
    def lbl(x, y, text, color):
        ax.text(x, y, text, fontsize=16, color=color, ha="center", va="center", zorder=5)
    ox, oy = origin
    L = 1.0  # базисные векторы — единичной длины
    if kind == "dsk":
        arrow(ax, (ox, oy), (ox+L, oy), "red", lw=2)
        lbl(ox+L+0.7, oy+0.6, r"$\vec i$", "red")
        arrow(ax, (ox, oy), (ox, oy+L), "blue", lw=2)
        lbl(ox-0.6, oy+L+0.6, r"$\vec j$", "blue")
    elif kind == "psk":
        arrow(ax, (ox, oy), (ox-L, oy), "blue", lw=2)
        lbl(ox-L-0.7, oy+0.6, r"$\vec e_r$", "blue")
        arrow(ax, (ox, oy), (ox, oy-L), "blue", lw=2)
        lbl(ox+0.6, oy-L-0.6, r"$\vec e_\theta$", "blue")
    elif kind == "esp":
        # тёмно-серый, не чёрный/малиновый: τ,n коллинеарны V,a в Рис.8,9 —
        # тот же цвет полностью скрыл бы единичный орт под более длинным вектором
        arrow(ax, (ox, oy), (ox, oy+L), "0.3", lw=2)
        lbl(ox-0.6, oy+L+0.6, r"$\vec\tau$", "0.3")
        arrow(ax, (ox, oy), (ox+L, oy), "0.3", lw=2)
        lbl(ox+L+0.7, oy+0.6, r"$\vec n$", "0.3")

def base_plane(ax, title, basis="dsk", basis_at=(0, 0), defer_basis=False):
    xf, yf = ellipse_full(); ax.plot(xf, yf, "--", color="0.6", lw=1.1, label="эллипс x²/24²+y²/8²=1")
    xt, yt = traj_traced(); ax.plot(xt, yt, "-", color="tab:blue", lw=2.4, label="траектория 0≤t≤1")
    ax.plot(-24, 0, "o", color="tab:blue", ms=8); ax.text(-25.5, 0.3, "M(t=1)", fontsize=12, ha="right", va="center")
    ax.plot(24, 0, "o", color="0.5", ms=7); ax.text(24, 1.0, "t=0", fontsize=11, ha="center")
    ax.axhline(0, color="0.4", lw=0.8); ax.axvline(0, color="0.4", lw=0.8)
    # basis_at-овый орт коллинеарен V/a в Рис.8,9 — если рисовать его здесь (до V/a),
    # более длинный вектор сверху полностью скрывает короткий орт. defer_basis=True
    # откладывает draw_basis на вызывающую сторону, чтобы орт рисовался ПОСЛЕ V/a (сверху, виден).
    if not defer_basis:
        draw_basis(ax, basis, origin=basis_at)
    ax.set_aspect("equal", adjustable="box"); ax.set_xlim(-30, 30); ax.set_ylim(-12, 12)
    # мелкая сетка "графовая бумага" как в Desmos: крупная сетка через 2(x)/1(y) с подписями + мелкая внутри
    ax.xaxis.set_major_locator(MultipleLocator(2)); ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.xaxis.set_minor_locator(AutoMinorLocator(4)); ax.yaxis.set_minor_locator(AutoMinorLocator(4))
    ax.grid(which="major", linewidth=0.6, color="0.7", alpha=0.9)
    ax.grid(which="minor", linewidth=0.3, color="0.85", alpha=0.7)
    ax.tick_params(axis="both", labelsize=8)
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_title(title)

def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=220, bbox_inches="tight"); plt.close(fig)
    from PIL import Image
    im = Image.open(path)
    im = im.resize((max(1, round(im.width/SCALE)), max(1, round(im.height/SCALE))), Image.LANCZOS)
    im.save(path)
    print("saved", name)

M = np.array([-24.0, 0.0]); sV = 0.18; sA = 20.0/(96*PI**2)  # sV: |V|=16π≈50 -> ~9 ед., влезает в ylim=12

fig, ax = plt.subplots(figsize=(11*SCALE, 5.2*SCALE)); base_plane(ax, "Рис.1. Плоское движение: траектория (эллипс 24×8)", "dsk")
ax.legend(loc="upper center", fontsize=10); save(fig, "fig01_traj.png")

fig, ax = plt.subplots(figsize=(11*SCALE, 5.2*SCALE)); base_plane(ax, "Рис.2. ДСК: вектор скорости  V=16π·j  (≈50.3)", "dsk")
arrow(ax, M, M+np.array([0, 16*PI])*sV, "k", label=r"$\vec V$", loff=(0.6, 0))
ax.text(0, -11, f"масштаб скорости 1:{1/sV:.1f}", fontsize=9, color="0.4"); save(fig, "fig02_dsk_v.png")

fig, ax = plt.subplots(figsize=(11*SCALE, 5.2*SCALE)); base_plane(ax, "Рис.3. ДСК: ускорение  a=96π²·i+16π·j", "dsk")
decompose(ax, M, 96*PI**2*sA, 16*PI*sA, "crimson", r"$a_x$", r"$a_y$", r"$\vec a$")
ax.text(0, -11, f"масштаб ускорения 1:{1/sA:.0f}  (|a_x|:|a_y|≈18.8)", fontsize=9, color="0.4"); save(fig, "fig03_dsk_a.png")

fig, ax = plt.subplots(figsize=(11*SCALE, 5.2*SCALE)); base_plane(ax, "Рис.4. ПСК: радиус-вектор r=24, θ=π", "psk")
arrow(ax, (0, 0), (-24, 0), "darkgreen", label="r=24", loff=(0, 0.8)); save(fig, "fig04_psk_r.png")

fig, ax = plt.subplots(figsize=(11*SCALE, 5.2*SCALE)); base_plane(ax, "Рис.5. ПСК: компоненты скорости  V_r=0,  V_θ=−16π", "psk")
arrow(ax, M, M+(-16*PI)*np.array([0, -1])*sV, "k", label=r"$V_\theta=-16\pi$", loff=(0.6, 0))
ax.text(0, -11, f"масштаб скорости 1:{1/sV:.1f}", fontsize=9, color="0.4"); save(fig, "fig05_psk_v.png")

fig, ax = plt.subplots(figsize=(11*SCALE, 5.2*SCALE)); base_plane(ax, "Рис.6. ПСК: компоненты ускорения  a_r=−96π², a_θ=−16π", "psk")
decompose(ax, M, 96*PI**2*sA, 16*PI*sA, "crimson", r"$a_r=-96\pi^2$", r"$a_\theta=-16\pi$", r"$\vec a$")
ax.text(0, -11, f"масштаб ускорения 1:{1/sA:.0f}", fontsize=9, color="0.4"); save(fig, "fig06_psk_a.png")

fig, ax = plt.subplots(figsize=(11*SCALE, 5.2*SCALE)); base_plane(ax, "Рис.7. ЕСПЗД: орты τ (вверх) и n (вправо)", "esp", basis_at=M)
save(fig, "fig07_espzd_tn.png")

fig, ax = plt.subplots(figsize=(11*SCALE, 5.2*SCALE)); base_plane(ax, "Рис.8. ЕСПЗД: скорость по касательной  V=16π", "esp", basis_at=M, defer_basis=True)
arrow(ax, M, M+np.array([0, 16*PI])*sV, "k", label=r"$\vec V=16\pi\,\vec\tau$", loff=(0.6, 0))
draw_basis(ax, "esp", origin=M)
ax.text(0, -11, f"масштаб скорости 1:{1/sV:.1f}", fontsize=9, color="0.4"); save(fig, "fig08_espzd_v.png")

fig, ax = plt.subplots(figsize=(11*SCALE, 5.2*SCALE)); base_plane(ax, "Рис.9. ЕСПЗД: a_τ=16π (по τ), a_n=96π² (по n)", "esp", basis_at=M, defer_basis=True)
decompose(ax, M, 96*PI**2*sA, 16*PI*sA, "crimson", r"$a_n=96\pi^2$", r"$a_\tau=16\pi$", r"$\vec a$")
draw_basis(ax, "esp", origin=M)
ax.text(0, -11, f"масштаб ускорения 1:{1/sA:.0f}", fontsize=9, color="0.4"); save(fig, "fig09_espzd_a.png")

def abs_curve(tt):
    x = 24*np.cos(PI*tt**2); y = -8*np.sin(PI*tt**2); z = 6*tt**2+2; phi = -np.sin(PI*tt)
    return x*np.cos(phi)-y*np.sin(phi), x*np.sin(phi)+y*np.cos(phi), z

def base_3d(ax, title):
    # отключаем авто-сортировку по глубине: иначе mplot3d иногда полностью прячет
    # векторы/подписи, добавленные позже, за более "близкими" по его расчёту объектами
    ax.computed_zorder = False
    # окрестность точки: траектория от старта (t=0) до точки (t=1) и немного дальше (t=1.2),
    # а не вся траектория 0..3 как раньше
    tt = np.linspace(0, 1.2, 700); X, Y, Z = abs_curve(tt)
    ax.plot(X, Y, Z, color="tab:blue", lw=2.2)
    ax.scatter([-24], [0], [8], color="black", s=40); ax.text(-24, 0, 11.5, "M(t=1)", fontsize=11)
    # базис i,j,k в начале координат — единичной длины, как и орты на плоских рисунках
    # (arrow_length_ratio увеличен, иначе наконечник на векторе длины 1 не виден на масштабе 52x52x16)
    L = 1.0
    ax.quiver(0, 0, 0, L, 0, 0, color="red", lw=2, arrow_length_ratio=0.4)
    ax.text(L+0.8, 0, 0, r"$\vec i$", color="red", fontsize=13)
    ax.quiver(0, 0, 0, 0, L, 0, color="green", lw=2, arrow_length_ratio=0.4)
    ax.text(0, L+0.8, 0, r"$\vec j$", color="green", fontsize=13)
    ax.quiver(0, 0, 0, 0, 0, L, color="blue", lw=2, arrow_length_ratio=0.4)
    ax.text(0, 0, L+0.8, r"$\vec k$", color="blue", fontsize=13)
    ax.scatter([0], [0], [0], color="black", s=30); ax.text(0.5, 0.5, -1.5, "O", fontsize=11)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z"); ax.set_title(title)
    ax.set_xlim(-26, 26); ax.set_ylim(-26, 26); ax.set_zlim(0, 16)
    # box_aspect по РЕАЛЬНЫМ диапазонам осей (52,52,16), а не кубом (1,1,1) —
    # иначе единичные базисные векторы i,j,k визуально получаются разной длины
    try: ax.set_box_aspect((52, 52, 16))
    except Exception: pass
    ax.view_init(elev=18, azim=-60)

def note3d(ax, text):
    ax.text2D(0.02, 0.02, text, transform=ax.transAxes, fontsize=9, color="0.4")

def arrow3(ax, b, v, color, label, loff=(0, 0, 2)):
    ax.quiver(b[0], b[1], b[2], v[0], v[1], v[2], color=color, lw=2.5, arrow_length_ratio=0.18)
    ax.text(b[0]+v[0]+loff[0], b[1]+v[1]+loff[1], b[2]+v[2]+loff[2], label, fontsize=12, color=color, zorder=20)

Mabs = np.array([-24.0, 0.0, 8.0]); Vabs = np.array([0.0, -8*PI, 12.0]); Aabs = np.array([88*PI**2, 16*PI, 12.0])
sV3 = 18.0/np.linalg.norm(Vabs); sA3 = 22.0/np.linalg.norm(Aabs)

fig = plt.figure(figsize=(8*SCALE, 7*SCALE)); ax = fig.add_subplot(111, projection="3d")
base_3d(ax, "Рис.10. Сложное движение: окрестность точки, V и a")
arrow3(ax, Mabs, Vabs*sV3, "black", r"$\vec V$")
# magenta, не crimson: вектор a почти параллелен оси i (красная) и при таком ракурсе
# кримзон на красном визуально пропадает (слипается с осью) — нужен контрастный цвет
arrow3(ax, Mabs, Aabs*sA3, "magenta", r"$\vec a$", loff=(2.5, 2.5, 2))
note3d(ax, f"масштаб: V 1:{1/sV3:.2f}, a 1:{1/sA3:.0f}")
save(fig, "fig10_3d_schema.png")

fig = plt.figure(figsize=(8*SCALE, 7*SCALE)); ax = fig.add_subplot(111, projection="3d")
base_3d(ax, "Рис.11. Абсолютная скорость  V=(0,−8π,12)"); arrow3(ax, Mabs, Vabs*sV3, "black", r"$\vec V$")
note3d(ax, f"масштаб скорости 1:{1/sV3:.2f}"); save(fig, "fig11_3d_v.png")

fig = plt.figure(figsize=(8*SCALE, 7*SCALE)); ax = fig.add_subplot(111, projection="3d")
base_3d(ax, "Рис.12. Абсолютное ускорение  a=(88π²,16π,12)"); arrow3(ax, Mabs, Aabs*sA3, "magenta", r"$\vec a$", loff=(2.5, 2.5, 2))
note3d(ax, f"масштаб ускорения 1:{1/sA3:.0f}"); save(fig, "fig12_3d_a.png")

# отдельный масштаб для разложений (V_e/a_r и т.п. длиннее результирующего V/a — иначе вектор
# вылезает за рамку рисунка); подбирается по самой длинной составляющей, чтобы все влезли
Ve = np.array([0, -24*PI, 0]); Vr_ = np.array([0, 16*PI, 12])
sV3b = 16.0/max(np.linalg.norm(Ve), np.linalg.norm(Vr_), np.linalg.norm(Vabs))

fig = plt.figure(figsize=(8*SCALE, 7*SCALE)); ax = fig.add_subplot(111, projection="3d")
base_3d(ax, "Рис.13. Метод 2: V_e=(0,−24π,0) + V_r=(0,16π,12)")
arrow3(ax, Mabs, Ve*sV3b, "darkgreen", r"$\vec V_e$")
arrow3(ax, Mabs, Vr_*sV3b, "darkorange", r"$\vec V_r$")
arrow3(ax, Mabs, Vabs*sV3b, "black", r"$\vec V$")
note3d(ax, f"масштаб скорости 1:{1/sV3b:.2f}"); save(fig, "fig13_3d_v2.png")

ar_ = np.array([96*PI**2, 16*PI, 12]); ae_ = np.array([24*PI**2, 0, 0]); akor_ = np.array([-32*PI**2, 0, 0])
sA3b = 16.0/max(np.linalg.norm(ar_), np.linalg.norm(ae_), np.linalg.norm(akor_), np.linalg.norm(Aabs))

fig = plt.figure(figsize=(8*SCALE, 7*SCALE)); ax = fig.add_subplot(111, projection="3d")
base_3d(ax, "Рис.14. Метод 2: a_r+a_e+a_кор")
# стрелки все из M как и были; почти совпадающие по направлению подписи a_r и a
# разводим по высоте (a_r ниже стрелки, a выше), чтобы буквы не сливались
arrow3(ax, Mabs, ar_*sA3b, "darkorange", r"$\vec a_r$", loff=(0, 0, -1.3))
arrow3(ax, Mabs, ae_*sA3b, "darkgreen", r"$\vec a_e$")
arrow3(ax, Mabs, akor_*sA3b, "purple", r"$\vec a_{кор}$")
arrow3(ax, Mabs, Aabs*sA3b, "crimson", r"$\vec a$", loff=(0, 0, 1.3))
note3d(ax, f"масштаб ускорения 1:{1/sA3b:.0f}"); save(fig, "fig14_3d_a2.png")
print("DONE")
