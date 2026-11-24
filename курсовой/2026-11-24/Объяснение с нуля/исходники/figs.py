# -*- coding: utf-8 -*-
"""Простые поясняющие рисунки к «Объяснению с нуля» → рисунки/*.png      python figs.py"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrowPatch, Arc, FancyBboxPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "рисунки"); os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "Arial", "font.size": 12, "mathtext.fontset": "stix"})
INK, NAVY, RED, BLUE, GREY, STEEL = "#222222", "#1F3864", "#B83A3A", "#2F6FB5", "#7A828C", "#C9D3E0"


def fig(w, h, xl, yl, eq=True):
    f, ax = plt.subplots(figsize=(w, h)); ax.set_xlim(*xl); ax.set_ylim(*yl); ax.axis("off")
    if eq: ax.set_aspect("equal")
    return f, ax


def arr(ax, a, b, c=RED, lw=2.4, ms=18, st="-|>"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=st, mutation_scale=ms, lw=lw, color=c, shrinkA=0, shrinkB=0, zorder=6))


def save(f, n):
    f.savefig(os.path.join(OUT, n), dpi=200, bbox_inches="tight", facecolor="white", pad_inches=0.08); plt.close(f)


# 1. дорожная карта
f, ax = fig(10, 3.9, (0, 10), (0, 3.9), eq=False)
st = ["1. Задание\nи сила крышки", "2. Схема\nмеханизма", "3. Синтез:\nразмеры", "4. Кинематика:\nдвижение", "5. Силы\nв звеньях",
      "6. Прочность:\nтолщины", "7. Уточнение:\nмассы", "8. 3D-модели\n(КОМПАС)", "9. МКЭ:\nдоработка", "10. Печать\nи сборка"]
for i, t in enumerate(st):
    r, k = divmod(i, 5); x = 0.1 + k * 1.98; y = 2.35 - r * 1.75
    ax.add_patch(FancyBboxPatch((x, y), 1.62, 1.1, boxstyle="round,pad=0.02,rounding_size=0.1", fc="#E9EFF8", ec=NAVY, lw=1.4))
    ax.text(x + 0.81, y + 0.55, t, ha="center", va="center", fontsize=11.5, color=INK)
    if k < 4: arr(ax, (x + 1.66, y + 0.55), (x + 1.95, y + 0.55), NAVY, 1.8, 14)
ax.plot([8.85, 8.85, 0.91, 0.91], [2.3, 2.0, 2.0, 1.95], color=NAVY, lw=1.8); arr(ax, (0.91, 2.0), (0.91, 1.74), NAVY, 1.8, 14)
save(f, "01_карта.png")

# 2. прямоугольный треугольник
f, ax = fig(6.4, 3.4, (-0.8, 6.2), (-0.7, 3.4))
ax.add_patch(Polygon([(0, 0), (4, 0), (4, 2.8)], fc="#EEF3FA", ec=NAVY, lw=2.2))
ax.add_patch(Arc((0, 0), 1.6, 1.6, theta1=0, theta2=35, color=RED, lw=2)); ax.text(1.0, 0.28, "φ", color=RED, fontsize=17)
ax.add_patch(Rectangle((3.75, 0), 0.25, 0.25, fc="none", ec=NAVY))
ax.text(2, -0.4, "прилежащий катет", ha="center"); ax.text(4.15, 1.3, "противолежащий\nкатет", va="center"); ax.text(1.65, 1.75, "гипотенуза", rotation=35, ha="center")
save(f, "02_треугольник.png")

# 3. момент силы
f, ax = fig(7.2, 2.5, (-0.6, 7.2), (-0.9, 1.9))
ax.add_patch(Rectangle((0, -0.12), 6, 0.24, fc=STEEL, ec=INK)); ax.add_patch(Circle((0, 0), 0.2, fc="white", ec=INK, lw=2, zorder=7)); ax.text(-0.45, -0.1, "O", fontsize=14)
arr(ax, (6, 1.6), (6, 0.14)); ax.text(6.15, 1.2, "F", color=RED, fontsize=15)
ax.annotate("", (0, -0.55), (6, -0.55), arrowprops=dict(arrowstyle="<|-|>", color=GREY)); ax.text(3, -0.85, "плечо h", ha="center", color=GREY)
ax.add_patch(Arc((0, 0), 1.7, 1.7, theta1=20, theta2=110, color=BLUE, lw=2.2)); arr(ax, (0.72, 0.46), (0.83, 0.28), BLUE, 2, 14)
ax.text(0.55, 1.0, "момент M = F · h", color=BLUE, fontsize=13)
save(f, "03_момент.png")

# 4. разложение силы камня
f, ax = fig(7.0, 4.6, (-4.4, 3.6), (-0.9, 4.6))
ph = np.radians(41.63); F = 3.3; R = F / np.cos(ph)
ax.plot([-1.9, 2.3], [-1.9 * np.tan(ph) + 0.55 * 0 + 0.0, 2.3 * np.tan(ph)], color=STEEL, lw=10, zorder=1, solid_capstyle="round")
ax.add_patch(Circle((0, 0), 0.16, fc="white", ec=INK, lw=2, zorder=8))
tip = (-R * np.sin(ph), R * np.cos(ph))
arr(ax, (0, 0), tip, NAVY, 3); arr(ax, (0, 0), (0, F), RED, 2.6); arr(ax, (0, 0), (tip[0], 0), BLUE, 2.6)
ax.plot([tip[0], tip[0], 0], [0, tip[1], F], "--", color=GREY, lw=1)
ax.text(tip[0] - 0.05, tip[1] + 0.18, "$R=F/\\cos\\varphi$", color=NAVY, fontsize=15, ha="center"); ax.text(0.12, 2.6, "$F$ — полезная\n(вдоль ползуна)", color=RED, fontsize=12)
ax.text(tip[0] / 2, -0.38, "$F\\,\\mathrm{tg}\\varphi$ — боковая", color=BLUE, fontsize=12, ha="center"); ax.text(1.4, 0.75, "кулиса", color=GREY, rotation=41)
ax.text(tip[0] - 0.1, tip[1] - 0.75, "сила камня" + chr(10) + "на кулису", color=NAVY, fontsize=11.5, ha="right")
ax.set_xlim(-4.4, 3.4); ax.set_ylim(-0.9, 4.1)
save(f, "04_разложение.png")

# 5. производная: путь и скорость
f, axs = plt.subplots(1, 2, figsize=(8.6, 2.9))
t = np.linspace(0, 2, 200); s = t ** 2
axs[0].plot(t, s, color=NAVY, lw=2.4); t0 = 1.2; axs[0].plot([0.6, 1.9], [t0 ** 2 + 2 * t0 * (0.6 - t0), t0 ** 2 + 2 * t0 * (1.9 - t0)], color=RED, lw=1.8)
axs[0].plot([t0], [t0 ** 2], "o", color=RED); axs[0].set_title("Положение: крутизна линии = скорость", fontsize=11); axs[0].set_xlabel("время"); axs[0].set_ylabel("путь")
axs[1].plot(t, 2 * t, color=RED, lw=2.4); axs[1].fill_between(t, 0, 2 * t, color=RED, alpha=0.12); axs[1].set_title("Скорость: площадь под линией = путь", fontsize=11); axs[1].set_xlabel("время"); axs[1].set_ylabel("скорость")
for a in axs: a.set_xticks([]); a.set_yticks([]); [a.spines[k].set_visible(False) for k in ("top", "right")]
save(f, "05_производная.png")

# 6. виды деформаций
f, ax = fig(10, 3.0, (0, 10), (0, 3.0), eq=False)
names = ["растяжение", "сжатие", "срез (сдвиг)", "изгиб", "смятие"]
for i, n in enumerate(names):
    x = 0.2 + i * 2.0; ax.text(x + 0.75, 0.12, n, ha="center", fontsize=12)
    if i < 2:
        ax.add_patch(Rectangle((x + 0.55, 0.95), 0.4, 1.1, fc=STEEL, ec=INK)); up = i == 0
        arr(ax, (x + 0.75, 2.1) if up else (x + 0.75, 2.75), (x + 0.75, 2.75) if up else (x + 0.75, 2.1)); arr(ax, (x + 0.75, 0.9) if up else (x + 0.75, 0.45), (x + 0.75, 0.45) if up else (x + 0.75, 0.9))
    elif i == 2:
        ax.add_patch(Rectangle((x + 0.1, 1.5), 0.65, 0.5, fc=STEEL, ec=INK)); ax.add_patch(Rectangle((x + 0.75, 1.3), 0.65, 0.5, fc=STEEL, ec=INK)); ax.plot([x + 0.75] * 2, [1.05, 2.25], "--", color=RED)
        arr(ax, (x + 0.6, 0.8), (x + 0.6, 1.45)); arr(ax, (x + 0.9, 2.5), (x + 0.9, 1.85))
    elif i == 3:
        tt = np.linspace(0, 1.5, 60); y = 1.45 - 0.5 * np.sin(np.pi * tt / 1.5); ax.fill_between(x + tt, y, y + 0.3, color=STEEL, ec=INK)
        arr(ax, (x + 0.75, 2.4), (x + 0.75, 1.3)); arr(ax, (x + 0.06, 0.8), (x + 0.06, 1.4)); arr(ax, (x + 1.44, 0.8), (x + 1.44, 1.4))
    else:
        ax.add_patch(Rectangle((x + 0.1, 0.75), 1.3, 0.8, fc=STEEL, ec=INK)); ax.add_patch(Circle((x + 0.75, 1.55), 0.3, fc="#E9C46A", ec=INK, zorder=4)); arr(ax, (x + 0.75, 2.65), (x + 0.75, 1.95))
save(f, "06_деформации.png")

# 7. диаграмма растяжения стали
f, ax = plt.subplots(figsize=(7.2, 3.4))
x = [0, 0.8, 1.0, 2.2, 4, 6, 7.4, 8.6]; y = [0, 245, 245, 245, 350, 415, 420, 360]
ax.plot(x, y, color=NAVY, lw=2.6); ax.axhline(98, color="#3F8F4F", lw=1.6, ls="--"); ax.text(5.3, 108, "[σ] = 98 МПа — сюда пускаем", color="#3F8F4F")
ax.plot([0, 1], [245, 245], ":", color=GREY); ax.text(1.2, 222, "σт = 245 — предел текучести (Ст3сп)", color=RED, va="top"); ax.text(5.0, 436, "σв — предел прочности", color=RED)
ax.text(0.1, 300, "упругий\nучасток", fontsize=10.5); ax.text(3.2, 255, "пластический участок", fontsize=10.5, rotation=14)
ax.set_xlabel("удлинение (не в масштабе)"); ax.set_ylabel("напряжение, МПа"); ax.set_xticks([]); ax.set_ylim(0, 480); [ax.spines[k].set_visible(False) for k in ("top", "right")]
save(f, "07_диаграмма.png")

# 8. изгиб: сжатые и растянутые волокна
f, ax = fig(8.4, 2.7, (-0.4, 8.4), (-0.2, 2.6))
tt = np.linspace(0, 4.6, 100); yb = 0.5 + 0.45 * ((tt - 2.3) / 2.3) ** 2
ax.fill_between(tt, yb, yb + 0.45, color="#F3C9C9", ec="none"); ax.fill_between(tt, yb + 0.45, yb + 0.9, color="#C9DDF3", ec="none"); ax.plot(tt, yb + 0.45, "--", color=INK, lw=1)
ax.plot(tt, yb, color=INK); ax.plot(tt, yb + 0.9, color=INK)
ax.text(2.3, 0.68, "растянуто", ha="center", color=RED); ax.text(2.3, 1.12, "сжато", ha="center", color=BLUE)
arr(ax, (2.3, 2.4), (2.3, 1.45)); arr(ax, (0.1, 0.25), (0.1, 0.9), GREY); arr(ax, (4.5, 0.25), (4.5, 0.9), GREY)
ax.plot([6.4, 6.4], [0.4, 2.0], color=INK); ax.add_patch(Polygon([(6.4, 1.2), (6.4, 2.0), (7.2, 2.0)], fc="#C9DDF3", ec=BLUE)); ax.add_patch(Polygon([(6.4, 1.2), (6.4, 0.4), (5.6, 0.4)], fc="#F3C9C9", ec=RED))
ax.text(6.5, 0.05, "напряжения: у краёв наибольшие,\nв середине — ноль", ha="center", fontsize=10.5, va="center")
save(f, "08_изгиб.png")

# 9. потеря устойчивости
f, ax = fig(6.6, 3.0, (0, 6.6), (0, 3.3))
for x0, bend, n in ((1.2, 0, "короткий толстый:\nсжимается"), (4.6, 0.55, "длинный тонкий:\nвыгибается")):
    z = np.linspace(0.8, 2.6, 60); w = 0.28 if bend == 0 else 0.09
    xc = x0 + bend * np.sin(np.pi * (z - 0.8) / 1.8); ax.fill_betweenx(z, xc - w, xc + w, color=STEEL, ec=INK); ax.plot([x0 - 0.6, x0 + 0.6], [0.78, 0.78], color=INK, lw=3)
    arr(ax, (x0, 3.25), (x0, 2.65)); ax.text(x0, 0.35, n, ha="center", va="center", fontsize=11)
save(f, "09_устойчивость.png")

# 10. стенки и полка
f, ax = fig(8.6, 4.2, (0, 9), (0, 4.3))
for x0, walls, n in ((2.2, True, "со стенками: опора рядом с силой —\nшток не гнётся"), (6.8, False, "только полка: опора далеко от силы —\nшток работает на изгиб")):
    d = 0 if walls else 0.18
    ax.add_patch(Rectangle((x0 - 0.12, 0.9), 0.24, 1.6, fc=STEEL, ec=INK)) if walls else ax.add_patch(Polygon([(x0 - 0.12, 0.9), (x0 + 0.12, 0.9), (x0 + 0.5, 2.5), (x0 + 0.26, 2.5)], fc=STEEL, ec=INK))
    ax.add_patch(Rectangle((x0 - 0.4 + 2 * d, 2.5), 0.8, 1.1, fc="#A9B7CC", ec=INK)); ax.add_patch(Circle((x0 + 2 * d, 3.05), 0.13, fc="#E9C46A", ec=INK, zorder=5))
    ax.add_patch(Rectangle((x0 - 1.0, 1.15), 0.82, 0.3, fc="#6C8EB5", ec=INK)); ax.add_patch(Rectangle((x0 + 0.24, 1.15), 0.82, 0.3, fc="#6C8EB5", ec=INK))
    arr(ax, (x0 - 1.3 + 2 * d, 3.05), (x0 - 0.15 + 2 * d, 3.05)); ax.text(x0 - 1.35 + 2 * d, 3.2, "1671 Н", color=RED, ha="center")
    if walls:
        ax.add_patch(Rectangle((x0 + 0.44, 1.45), 0.35, 2.3, fc="#6C8EB5", ec=INK)); ax.add_patch(Rectangle((x0 - 0.79, 1.45), 0.35, 2.3, fc="#6C8EB5", ec=INK, alpha=0.35)); arr(ax, (x0 + 1.5, 3.05), (x0 + 0.82, 3.05), BLUE)
    else:
        arr(ax, (x0 + 1.5, 1.3), (x0 + 0.28, 1.3), BLUE); ax.annotate("", (x0 + 1.75, 1.3), (x0 + 1.75, 3.05), arrowprops=dict(arrowstyle="<|-|>", color=GREY)); ax.text(x0 + 1.82, 2.1, "58 мм", color=GREY)
    ax.text(x0, 0.4, n, ha="center", va="center", fontsize=11)
save(f, "10_стенки.png")

# 11. идея МКЭ
f, ax = fig(7.6, 2.5, (0, 8), (0, 2.6))
ax.add_patch(Rectangle((0.2, 0.6), 2.6, 1.4, fc=STEEL, ec=INK)); ax.text(1.5, 0.25, "сплошная деталь", ha="center")
arr(ax, (3.1, 1.3), (4.1, 1.3), NAVY)
for i in range(7):
    for j in range(4):
        x, y = 4.5 + i * 0.4, 0.6 + j * 0.35; v = np.exp(-((i - 1) ** 2 + (j - 3) ** 2) / 5)
        c = plt.cm.jet(0.08 + 0.85 * v)
        ax.add_patch(Polygon([(x, y), (x + 0.4, y), (x, y + 0.35)], fc=c, ec="white", lw=0.6)); ax.add_patch(Polygon([(x + 0.4, y), (x + 0.4, y + 0.35), (x, y + 0.35)], fc=c, ec="white", lw=0.6))
ax.text(5.9, 0.25, "сетка кусочков: красное — опасно", ha="center")
save(f, "11_мкэ.png")

# 12. рычаг: рука и крышка
f, ax = fig(7.6, 3.0, (-0.8, 8.2), (-0.9, 2.4))
ax.add_patch(Rectangle((0, -0.1), 7, 0.2, fc=STEEL, ec=INK)); ax.add_patch(Polygon([(0, -0.1), (-0.3, -0.6), (0.3, -0.6)], fc=GREY, ec=INK))
arr(ax, (7, 1.1), (7, 0.12), RED, 2); ax.text(7.1, 0.8, "рука: мало", color=RED, va="center", fontsize=11)
arr(ax, (0.9, 0.12), (0.9, 2.1), BLUE, 4, 24); ax.text(1.05, 1.5, "крышка: много", color=BLUE, fontsize=12)
ax.annotate("", (0, -0.75), (0.9, -0.75), arrowprops=dict(arrowstyle="<|-|>", color=GREY)); ax.annotate("", (0, -0.35), (7, -0.35), arrowprops=dict(arrowstyle="<|-|>", color=GREY)); ax.text(4, -0.62, "длинное плечо", color=GREY, ha="center"); ax.text(1.0, -0.8, "короткое плечо", color=GREY, fontsize=10)
save(f, "12_рычаг.png")
print(sorted(os.listdir(OUT)))
