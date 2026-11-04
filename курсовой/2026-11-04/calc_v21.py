# -*- coding: utf-8 -*-
"""v21 (04.11): 1) расчёт кинематических пар на срез и смятие (новый п. 12.6): ось O и палец D — срез, отверстия — смятие,
перемычки у отверстий — срез; [τср] крепежа не более 50 МПа (замечание преподавателя);
2) смятие отверстия кулисы на оси O не проходит при толщине полосы 8 мм → к кулисе у оси O приварена ступица Ø16 × 12
(вместо распорной втулки), поэтому уточнённый силовой расчёт разд. 13 (calc_v17.py) пересчитан с новой массой кулисы.
Результат: calc_v21.json, calc_v21.npz."""
import json, os
import numpy as np
from math import pi, sqrt, hypot, cos, radians

HERE = os.path.dirname(os.path.abspath(__file__))
SRC17 = os.path.join(HERE, "..", "2026-11-02", "calc_v17.py")

# ---------------- геометрия пар (мм)
D_O = D_D = 10.0                  # ось O и палец D, сталь 45, пруток ГОСТ 2590-2006
D_ST, L_ST = 16.0, 12.0           # ступица кулисы у оси O (заменяет распорную втулку): наружный диаметр, длина
B_K, H_K = 8.0, 18.0              # полоса кулисы
S_ST = 12.0                       # стойка — лист Ст3сп 12 мм, ось запрессована
S_P, W_P, H_P = 16.0, 24.0, 40.0  # направляемая часть ползуна: толщина (длина отверстия под палец D), ширина, высота
TAU_PIN = 50.0                    # [τср] крепежа — не более 50 МПа; сталь 45: 0,5·142 = 71 → 50
TAU_LUG = 0.5 * 245 / 2.5         # [τ] Ст3сп (перемычки кулисы и ползуна) = 49
P_MOV, P_FIX = 24.0, 65.0         # [σсм]: подвижное соединение (сталь) / неподвижное, Ст3 — повторная нагрузка (Inventor)

# ---------------- уточнённый силовой расчёт v17 с массой ступицы
src = open(SRC17, encoding="utf-8").read()
reps = [('KU = R13["kul"]; m1, zS, JO, JS = KU["m"], KU["zc"] / 1000, KU["JO"], KU["JS"]; m3 = R13["m3"]',
         'KU = R13["kul"]; m1, zS, JO, JS = KU["m"], KU["zc"] / 1000, KU["JO"], KU["JS"]; m3 = R13["m3"]\n'
         'm_st = 7850e-9 * pi / 4 * (D_ST ** 2 - D_O ** 2) * L_ST          # ступица: центр масс на оси O\n'
         'J_st = m_st * (D_ST ** 2 + D_O ** 2) / 8 * 1e-6\n'
         'm1_strip = m1; zS = m1 * zS / (m1 + m_st); m1 += m_st; JO += J_st; JS = JO - m1 * zS ** 2'),
        ('"calc_v17.json"', '"calc_v21.json"'), ('"calc_v17.npz"', '"calc_v21.npz"'),
        ('           m1=m1, zS=zS,', '           m1=m1, m1_strip=m1_strip, m_st=m_st, zS=zS,')]
for a, b in reps:
    assert src.count(a) == 1, a
    src = src.replace(a, b)
g17 = dict(__file__=os.path.join(HERE, "calc_v21.py"), __name__="calc_v21", D_ST=D_ST, D_O=D_O, L_ST=L_ST)
exec(compile(src, "calc_v17+ступица", "exec"), g17)
res = json.load(open(os.path.join(HERE, "calc_v21.json"), encoding="utf-8"))
X0, X1, phs = g17["X0"], g17["X1"], g17["phs"]

# ---------------- нагрузки на пары: первичный расчёт (разд. 11) — подбор, уточнённый (разд. 13) — проверка
def maxes(X):
    RO = np.hypot(X[:, 0], X[:, 1]); RD = np.hypot(X[:, 4], X[:, 5])
    i, j, k = RO.argmax(), RD.argmax(), np.abs(X[:, 6]).argmax()
    return dict(RO=float(RO[i]), phO=float(phs[i]), RD=float(RD[j]), phD=float(phs[j]), R30=float(abs(X[k, 6])), ph30=float(phs[k]))


def checks(ld):
    RO, RD, R30 = ld["RO"], ld["RD"], ld["R30"]
    return dict(
        tau_O=4 * RO / (pi * D_O ** 2),                        # срез оси O, одна плоскость
        p_O_strip=RO / (D_O * B_K),                            # смятие отверстия кулисы без ступицы
        p_O=RO / (D_O * (B_K + L_ST)),                         # смятие отверстия кулисы со ступицей
        tau_lug_O=RO / (2 * (H_K / 2 - D_O / 2) * B_K),        # срез перемычки кулисы у оси O
        p_O_stand=RO / (D_O * S_ST),                           # смятие отверстия стойки (ось запрессована)
        tau_D=4 * RD / (pi * D_D ** 2),                        # срез пальца D, одна плоскость
        p_D=RD / (D_D * S_P),                                  # смятие отверстия ползуна
        tau_lug_D=RD / (2 * (W_P / 2 - D_D / 2) * S_P),        # срез перемычки ползуна (наименьшая — по ширине)
        p_30=R30 / (H_P * S_P),                                # поступательная пара 3–0: боковая грань ползуна в направляющей
    )


L0, L1 = maxes(X0), maxes(X1)
C0, C1 = checks(L0), checks(L1)
need = dict(d_O_shear=sqrt(4 * L0["RO"] / (pi * TAU_PIN)), d_D_shear=sqrt(4 * L0["RD"] / (pi * TAU_PIN)),
            l_O=L0["RO"] / (D_O * P_MOV), d_O_strip=L0["RO"] / (B_K * P_MOV),
            tau_O8=4 * L0["RO"] / (pi * 64), tau_D8=4 * L0["RD"] / (pi * 64))
need["c_big"] = H_K / 2 - need["d_O_strip"] / 2
need["tau_lug_big"] = L0["RO"] / (2 * need["c_big"] * B_K)
# перегрузка: головка упёрлась в конце хода, рука давит с силой 120 Н (п. 12.1) — нагрузки в φк растут пропорционально
phk = g17["phi_k"]; F_k = g17["F_of"](phk)
k_over = 120.0 * 500.0 * cos(radians(phk)) ** 3 / 12.53 / F_k
x0k = X0[-1]
over = dict(k=k_over, RO=k_over * hypot(x0k[0], x0k[1]), RD=k_over * hypot(x0k[4], x0k[5]))
over["tau_O"] = 4 * over["RO"] / (pi * D_O ** 2); over["tau_D"] = 4 * over["RD"] / (pi * D_D ** 2)
over["tau_T"] = 0.5 * 355                                   # предел текучести при сдвиге стали 45 по третьей теории

res.update(pairs=dict(D_O=D_O, D_D=D_D, D_ST=D_ST, L_ST=L_ST, S_ST=S_ST, S_P=S_P, W_P=W_P, H_P=H_P, TAU_PIN=TAU_PIN,
                      TAU_LUG=TAU_LUG, P_MOV=P_MOV, P_FIX=P_FIX, L0=L0, L1=L1, C0=C0, C1=C1, need=need, over=over))
json.dump(res, open(os.path.join(HERE, "calc_v21.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"m_st {g17['m_st']*1000:.2f} г; m1 {res['m1']:.4f}; zS {res['zS']*1000:.2f}; JO {res['JO']:.6f}; JS {res['JS']:.5f}; G1 {res['G1']:.3f}")
print("нагрузки перв.", {k: round(v, 2) for k, v in L0.items()})
print("нагрузки уточн.", {k: round(v, 2) for k, v in L1.items()})
print("перв.", {k: round(v, 2) for k, v in C0.items()})
print("уточн.", {k: round(v, 2) for k, v in C1.items()})
print("need", {k: round(v, 3) for k, v in need.items()})
print("перегрузка", {k: round(v, 2) for k, v in over.items()})
