# -*- coding: utf-8 -*-
"""ДЗ-1 ПТП: расчёт токарной (часть 1) и фрезерной (часть 3) операций. Вариант — строка 4 таблицы вариантов
(Девяткин Д. А.): сечение IV, S*=2, L*=8, d1=3, d2=7, d3=4, d4=9, L1=5, L2=9, L3=3, L4=5, Rz1=6, Rz2=6, Rz4=3, Rz*=5,
материал 6, T 4. Методика — по «Задание и образец выполнения.pdf» и лекциям ПТП (лекция 7: слайды 3, 6, 10;
лекция 5-6: слайды 19, 21; лекция 3 — классификация сталей). Результат — calc.json (его читают отчёт и КОМПАС-скрипты)."""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- таблицы задания
T1 = {  # Таблица 1: строка -> (S*, L*, d1, d2, d3, d4, L1, L2, L3, L4)
    1: (100, 20, 50, 90, 70, 50, 25, 25, 25, 25), 2: (110, 22, 52, 92, 71, 52, 32, 32, 32, 32),
    3: (120, 25, 53, 95, 73, 53, 40, 40, 40, 40), 4: (125, 28, 55, 98, 75, 55, 45, 45, 45, 45),
    5: (130, 32, 56, 100, 78, 56, 50, 50, 50, 50), 6: (135, 36, 58, 102, 80, 58, 56, 56, 56, 56),
    7: (140, 40, 60, 105, 82, 60, 63, 63, 63, 63), 8: (145, 45, 63, 108, 85, 63, 67, 67, 67, 67),
    9: (150, 50, 65, 110, 88, 65, 71, 71, 71, 71)}
T2 = {1: 320, 2: 160, 3: 80, 4: 40, 5: 20, 6: 10}            # Таблица 2: строка -> Rz, мкм (одинаково для всех столбцов)
MATERIALS = {1: "15Н2М", 2: "22ХНМ", 3: "35ХГФ", 4: "12Х2М", 5: "20Х12Н12Г6", 6: "45Х4В3ГФ", 7: "15Х2ГН2ТРА",
             8: "12Х18Н10Т", 9: "АК9Ц6", 10: "АК7Ц9", 11: "АМг3"}
T_LIFE = {1: 10, 2: 15, 3: 30, 4: 45, 5: 60}
SECTIONS = {"I": ("круг с лыской", 1.2), "II": ("квадрат", 1.414), "III": ("квадрат со скруглёнными углами", 1.2),
            "IV": ("шестигранник", 1.155), "V": ("шестигранник со скруглёнными углами", 1.1)}  # D* = k·S* (рис. 2)
COLS = ["S*", "L*", "d1", "d2", "d3", "d4", "L1", "L2", "L3", "L4"]

# ---------------------------------------------------------------- вариант (строка 4 скрина таблицы вариантов)
VAR = dict(fio="Девяткин Д. А.", row=4, section="IV", t1=[2, 8, 3, 7, 4, 9, 5, 9, 3, 5], t2=[6, 6, 3, 5], mat=6, T=4)
code = f"{VAR['section']}-{''.join(map(str, VAR['t1']))}-{''.join(map(str, VAR['t2']))}-{VAR['mat']}-{VAR['T']}"
vals = {c: T1[r][i] for i, (c, r) in enumerate(zip(COLS, VAR["t1"]))}
S_, Ls, d1, d2, d3, d4, L1, L2, L3, L4 = (vals[c] for c in COLS)
Rz1, Rz2, Rz4, Rzs = (T2[r] for r in VAR["t2"])
mat, T = MATERIALS[VAR["mat"]], T_LIFE[VAR["T"]]
sec_name, k_sec = SECTIONS[VAR["section"]]
D_star = S_ / math.cos(math.radians(30))                       # описанная окружность шестигранника = 1,155·S*
L_total = L1 + L2 + L3 + Ls + L4

# ---------------------------------------------------------------- материал (лекция 3)
alloy = {"Х (хром)": 4, "В (вольфрам)": 3, "Г (марганец)": 1, "Ф (ванадий)": 1}   # цифры марки; без цифры — ≈1 %
C_pct = 0.45
alloy_sum = sum(alloy.values())
alloy_class = "низколегированная" if alloy_sum < 2.5 else ("среднелегированная" if alloy_sum <= 10 else "высоколегированная")
c_class = "малоуглеродистая" if C_pct < 0.25 else ("среднеуглеродистая" if C_pct <= 0.6 else "высокоуглеродистая")
steel_group = "высоколег" if alloy_sum > 10 else "констр"

# ================================================================ ЧАСТЬ 1. Токарная операция (шейка 1)
neck = dict(n=1, d=d1, L=L1, Rz=Rz1)                          # выбор: Rz1 = Rz2 = 10 -> шейка 1 (до уступа, ДЗ/Решения_по_ДЗ1.md)
Ra = neck["Rz"] / 4                                            # Ra = Rz/4
# лекция 7, слайд 10: заготовка 17 кв. -> 3 этапа (черн., получист., чист.); строка «диаметр заготовки до 80 мм»
T_ROWS = [(18, 2.0, 0.9, 0.5), (30, 2.5, 1.0, 0.6), (50, 3.0, 1.3, 0.7), (80, 3.5, 1.5, 0.8), (120, 4.5, 1.7, 0.9),
          (180, 5.0, 2.0, 1.0), (250, 5.5, 2.2, 1.1)]
for dmax, t_r, t_p, t_c in T_ROWS:                             # строка, у которой получившийся диаметр заготовки ≤ dmax
    D_min = neck["d"] + 2 * (t_r + t_p + t_c)
    if D_min <= dmax:
        break
t_sum = t_r + t_p + t_c
D_zag = math.ceil(D_min)                                       # 64,6 -> 65 мм (поковка, без десятых долей)
t_r_acc = round((D_zag - neck["d"]) / 2 - t_p - t_c, 2)        # черновой проход принимает округление: 3,7

phi, phi1 = 90.0, 10.0                                         # упорный резец (шейка ограничена уступом ⌀105)
Rz_mm = neck["Rz"] / 1000
S_calc = Rz_mm * math.sin(math.radians(phi + phi1)) / (math.sin(math.radians(phi)) * math.sin(math.radians(phi1)))
S = math.floor(S_calc * 100) / 100                             # до сотых в меньшую сторону (как в образце)
Cv = {"констр": (548, 478), "высоколег": (345, 301)}[steel_group][0 if S < 0.4 else 1]
m = 0.4
V = Cv / T ** m
n_calc = 1000 * V / (math.pi * D_zag)                          # D — наибольший диаметр обрабатываемой поверхности (заготовки)
n = math.ceil(n_calc)                                          # до целого в большую сторону (как в образце)
Smin = S * n
# время: To = (l + l_вр + l_пер)·i / Smin;  φ = 90° -> l_вр = t/tgφ + подвод = 0 + 2 мм; перебег 0 (обработка до уступа)
l_in, l_over, i_t = 2.0, 0.0, 3                                # i — по одному проходу на каждом из 3 этапов
L_rx = neck["L"] + l_in + l_over
To1 = L_rx * i_t / Smin

# ================================================================ ЧАСТЬ 3. Фрезерование граней под ключ
CUTTERS = [("0300", 3, 6, 8, 57), ("0400", 4, 6, 11, 57), ("0500", 5, 6, 13, 57), ("0600", 6, 6, 13, 57),
           ("0800", 8, 8, 19, 63), ("1000", 10, 10, 22, 72), ("1200", 12, 12, 26, 83), ("1400", 14, 14, 26, 83),
           ("1600", 16, 16, 32, 92), ("1800", 18, 18, 32, 92), ("2000", 20, 20, 38, 104)]   # код, D, d, H, L; z = 4
z = 4
a_face = S_ / math.sqrt(3)                                     # ширина грани шестигранника (сторона) = 63,51 мм
n_faces = 6
t_mill = D_star / 2 - S_ / 2                                   # толщина снимаемого слоя у середины грани = 8,51 мм
H_max = max(c[3] for c in CUTTERS)
one_pass = [c for c in CUTTERS if c[3] >= a_face]
i_w = 1 if one_pass else math.ceil(a_face / H_max)             # число проходов по ширине грани
cutter = min((c for c in CUTTERS if c[3] * i_w >= a_face), key=lambda c: c[3])   # минимальная H, закрывающая грань за i_w проходов
code_c, Dc, dc, Hc, Lc = cutter
Rzs_mm = Rzs / 1000
fz = math.sqrt(Dc ** 2 - (Dc - 2 * Rzs_mm) ** 2)               # из Rz = ½(D − √(D² − fz²))
fz_r = math.floor(fz * 100) / 100
So_m = fz_r * z
Cv_m, m_m = 33.81 * math.sqrt(Dc), 0.436                       # стали
V_m = Cv_m / T ** m_m
n_m_calc = 1000 * V_m / (math.pi * Dc)
n_m = math.ceil(n_m_calc)
Smin_m = So_m * n_m
l_in_m = math.sqrt(t_mill * (Dc - t_mill)) + 2.0                # врезание по дуге контакта + подвод 2 мм
l_over_m = 2.0
L_rx_m = Ls + l_in_m + l_over_m
To_face = L_rx_m * i_w / Smin_m
To3 = To_face * n_faces

R = dict(variant=VAR, code=code, vals=vals, S=S_, Ls=Ls, d=[d1, d2, d3, d4], L=[L1, L2, L3, L4], L_total=L_total,
         Rz=dict(Rz1=Rz1, Rz2=Rz2, Rz4=Rz4, Rzs=Rzs), material=mat, T=T, section=dict(code=VAR["section"], name=sec_name,
         k=k_sec, D_star=D_star), steel=dict(C=C_pct, c_class=c_class, alloy=alloy, alloy_sum=alloy_sum, alloy_class=alloy_class,
         group=steel_group), LD=L_total / D_star,
         p1=dict(neck=neck, Ra=Ra, row_dmax=dmax, t=[t_r, t_p, t_c], t_sum=t_sum, D_min=D_min, D_zag=D_zag, t_r_acc=t_r_acc,
                 phi=phi, phi1=phi1, S_calc=S_calc, S=S, Cv=Cv, m=m, V=V, n_calc=n_calc, n=n, Smin=Smin,
                 l_in=l_in, l_over=l_over, i=i_t, L_rx=L_rx, To=To1),
         p3=dict(a_face=a_face, faces=n_faces, t=t_mill, H_max=H_max, one_pass=bool(one_pass), i_w=i_w, cutter=dict(code=code_c,
                 D=Dc, d=dc, H=Hc, L=Lc, z=z), fz=fz, fz_r=fz_r, So=So_m, Cv=Cv_m, m=m_m, V=V_m, n_calc=n_m_calc, n=n_m,
                 Smin=Smin_m, l_in=l_in_m, l_over=l_over_m, L_rx=L_rx_m, To_face=To_face, To=To3))
json.dump(R, open(os.path.join(HERE, "calc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("шифр", code, vals, "Rz", Rz1, Rz2, Rz4, Rzs, mat, "T =", T, sec_name, f"D* = {D_star:.2f}", "L =", L_total)
    print(f"сталь: C {C_pct} {c_class}, Σлег {alloy_sum} % {alloy_class} -> Cv {Cv}")
    print(f"Ч1: Ra {Ra}, строка до {dmax}: t {t_r}/{t_p}/{t_c} Σ {t_sum:.1f}, Dmin {D_min:.1f} -> Dзаг {D_zag} (черн. {t_r_acc})")
    print(f"    S {S_calc:.4f} -> {S}, V {V:.2f}, n {n_calc:.1f} -> {n}, Smin {Smin:.1f}, Lрх {L_rx}, To {To1:.2f} мин")
    print(f"Ч3: грань {a_face:.2f}, t {t_mill:.2f}, Hmax {H_max}, за 1 проход: {bool(one_pass)}, i {i_w}, фреза {cutter}")
    print(f"    fz {fz:.4f} -> {fz_r}, So {So_m:.2f}, Cv {Cv_m:.2f}, V {V_m:.2f}, n {n_m_calc:.1f} -> {n_m}, Smin {Smin_m:.0f}")
    print(f"    Lрх {L_rx_m:.2f}, To грани {To_face:.4f}, To 6 граней {To3:.3f} мин = {To3*60:.1f} с")
