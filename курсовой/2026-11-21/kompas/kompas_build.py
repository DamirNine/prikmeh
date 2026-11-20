# -*- coding: utf-8 -*-
"""Детали укупоривателя в КОМПАС-3D v25 (Учебная) через API (COM) — каждая деталь отдельно, в своей системе координат
от своей базы; файлы — в папке «Детали». Сборка — kompas_assembly.py (детали соединяются сопряжениями).

Детали: Стойка (лист с отверстиями под крепёж к стене, основание под бутылку, ось O, направляющая ползуна, нижний и верхний
упоры — одна деталь),
Кулиса (полоса со ступицей, рукоять — конец полосы), Камень (обойма с отверстием под палец), Палец D, Ползун, Шайба и Гайка
(держат ползун на пальце), Кожух (закрывает механизм, снимается вперёд), Бутылка (обрабатываемое изделие: стоит на основании,
по оси ползуна).
Палец D отделён от камня (замечание преподавателя: камень — деталь с отверстием + штифт, нужна фиксация по оси): палец
запрессован в обойму, задний торец заподлицо с её задней гранью (сзади в 0,5 мм полоса кулисы — места под головку нет);
ползун вращается на пальце Ø10, спереди — шайба и гайка М10 на резьбовом конце. Резьба М10 × 1,5 — настоящая (витки
построены вырезом профиля по винтовой линии: деталь печатается на 3D-принтере, условная резьба не печатается). Гайка
навинчивается до сбега резьбы и прижимает шайбу; между шайбой и ползуном остаётся зазор — ползун не зажат и не может
сместиться по оси пальца.
Базы (ось z при сборке — к наблюдателю, ползун — в плоскости z = 0 сборки): Стойка — ось O на передней грани листа;
Кулиса — ось O на задней грани полосы, x — вдоль кулисы; Камень — ось отверстия на передней грани обоймы; Палец D, Шайба —
ось на заднем торце; Гайка — ось в средней плоскости; Ползун — ось отверстия под палец в средней плоскости; Бутылка — центр
дна, y вдоль оси."""
import json, os, subprocess, sys, time
from math import radians, tan, cos, sin
import pythoncom, pywintypes, win32api, win32con, win32process
from win32com.client import GetActiveObject, gencache

HERE = os.path.dirname(os.path.abspath(__file__))
PARTS_DIR = os.path.join(HERE, "Детали")
BIN = r"C:\Program Files\ASCON\KOMPAS-3D v25 Study\Bin"
RJ = json.load(open(os.path.join(HERE, "..", "..", "2026-11-04", "calc_v21.json"), encoding="utf-8"))
E = 12.53
PH_N, PH_K, PH_Y = RJ["phi_n"], RJ["phi_k"], RJ["phi_y"]
PH0 = PH_Y                                        # положение сборки — начало пластической деформации
yD = lambda ph: E * tan(radians(ph))


def mod(tlb):
    lib = pythoncom.LoadTypeLib(os.path.join(BIN, tlb))
    a = lib.GetLibAttr()
    return gencache.EnsureModule(str(a[0]), a[1], a[3], a[4])


C = mod("ksConstants.tlb").constants
C3 = mod("ksConstants3D.tlb").constants
A5, A7 = mod("kAPI5.tlb"), mod("kAPI7.tlb")


def wait_apps():
    """приложения КОМПАСа (APM FEM и др.) загружаются ещё 5–7 с после старта: ждём, пока число модулей перестанет расти.
    Деталь, созданная в это время, подхватывается APM FEM: рядом появляется .apmf, а следующий SaveAs падает в kAPI2D5"""
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq kStudy.exe", "/NH", "/FO", "CSV"], capture_output=True).stdout
    h = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False,
                             int(out.decode("cp866").split('","')[1]))
    n, t_same = 0, time.time()
    while time.time() - t_same < 4:
        try:
            m = len(win32process.EnumProcessModulesEx(h, win32process.LIST_MODULES_ALL))
        except pywintypes.error:                  # список модулей меняется прямо во время чтения
            m = 0
        if m != n:
            n, t_same = m, time.time()
        time.sleep(0.5)
    win32api.CloseHandle(h)


def connect():
    try:
        GetActiveObject("Kompas.Application.5")
    except pythoncom.com_error:                    # COM-сервер КОМПАС сам не стартует — запускаем программу и ждём
        subprocess.Popen([os.path.join(BIN, "kStudy.Exe")])
        for _ in range(60):
            time.sleep(2)
            try:
                GetActiveObject("Kompas.Application.5"); break
            except pythoncom.com_error:
                pass
        wait_apps()
    k5 = A5.KompasObject(GetActiveObject("Kompas.Application.5")._oleobj_.QueryInterface(A5.KompasObject.CLSID,
                                                                                         pythoncom.IID_IDispatch))
    app = A7.IApplication(GetActiveObject("Kompas.Application.7")._oleobj_.QueryInterface(A7.IApplication.CLSID,
                                                                                          pythoncom.IID_IDispatch))
    app.Visible = True
    return k5, app


k5, app = connect()
qi = lambda obj, cls: cls(obj._oleobj_.QueryInterface(cls.CLSID, pythoncom.IID_IDispatch))
rgb = lambda h: int(h[1:3], 16) | int(h[3:5], 16) << 8 | int(h[5:7], 16) << 16

# ---------------- размеры (мм)
B_ST, H_ST = 12.0, 390.0                          # стойка: лист 12 мм, высота 390
X_ST0, X_ST1 = -31.75, 60.25                      # кромки листа от оси O: центр 14,25 — посередине кожуха, поля по 14,75 мм
L_ROD = 60.0                                      # шток ползуна Ø8 × 60, как в расчёте
# головка ползуна Ø40 с конической горловиной (рисунок 1 расчёта). Ход ползуна 16 = 10 до касания + 6 обжима: при φк верх
# конуса (Ø28,6) — на уровне низа юбки, т. е. на 5,4 мм ниже торца горлышка; при касании (φоб) вход конуса Ø32,1 — у низа юбки.
# Поэтому головка выходит вниз на 12,65 мм за торец горлышка при φк (длина 36,65 вместо 24); шток прежний
CAP_TOP, CAP_SKIRT = 0.94, 5.4                    # крышка: верх над торцом горлышка, низ юбки под торцом
R_OBZH, R_K, S_OB, CH = 14.3, 16.05, 6.0, 1.25    # горловина: цилиндр Ø28,6, вход конуса Ø32,1, длина конуса, фаска входа
Y_GL = -44 - L_ROD                                # торец горлышка при φк в координатах ползуна (−104)
Y_CT = Y_GL - CAP_SKIRT                           # верх конуса
Y_CB = Y_CT - S_OB                                # низ конуса (вход)
Y_HB = Y_CB - CH                                  # нижний торец головки
Y_CEIL = Y_GL + CAP_TOP + 0.5                     # потолок полости: 0,5 мм над крышкой в конце хода
SLIDER_PROFILE = [(0, -20), (4, -20), (4, -20 - L_ROD), (20, -20 - L_ROD), (20, Y_HB), (R_K + CH, Y_HB), (R_K, Y_CB),
                  (R_OBZH, Y_CT), (R_OBZH, Y_CEIL), (0, Y_CEIL)]                  # (r, y), ось вращения — y
Y_ST0 = -325.25                                   # низ листа от оси O = дно бутылки: yD(φн) − (20 + шток + 24) − (226,5 + 6 + 10)
Z_ST = -34.0                                      # передняя грань стойки в сборке
Y_BOT, Y_TOP = yD(PH_K) - 55, yD(PH_N) + 26       # направляющая: на 35 мм ниже и на 6 мм выше хода ползуна
# Направляющая — отдельная деталь УКП.00.002 (15.11): с планками на стойке кулису нельзя было надеть на ось O — левая планка
# стоит прямо перед осью. Теперь: задняя пластина в выемке листа стойки (не насквозь — назад не провалится, вбок и вниз не
# сдвинется), кронштейны и планки. Вперёд её держит кожух: планки удлинены до 1 мм от его передней стенки.
# Координаты — как у стойки (ось O на передней грани листа), поэтому в сборке плоскости обеих деталей совпадают.
GD_TL, GD_TR = 6.0, 12.0                          # толщина планок: левая 6, правая 12 — на правую давит ползун (R30N до 1671 Н;
                                                  # APM 15.11 при 6 мм: ≈ 300–400 МПа у кронштейна > [σ] = 142)
GD_X0, GD_X1 = E - 12.5 - GD_TL, E + 12.5 + GD_TR   # наружные кромки планок (внутренние — по ползуну, e ± 12,5)
GD_R = 10.0                                       # скругление «верх кронштейна — планка» (пользователь 15.11: R5 → R10)
GD_RU_L, GD_RU_R = 10.0, 14.0                     # скругления «внутренняя грань кронштейна — пластина» («ванна» между кронштейнами;
                                                  # пользователь 15.11, APM 136 МПа < 142)
GD_PL_T, GD_PL_Y1 = 6.0, -17.0                    # пластина: толщина (= глубина выемки), верх — ниже кулисы и камня на всём ходе
GD_Z0, GD_Z1 = 26.0, 55.0                         # планки по z (у передней грани листа z = 0): спереди — 1 мм до кожуха (56)
POCKET_GAP = 0.2                                  # зазор пластины в выемке по бокам и сверху (вниз — опирается на дно выемки)
POCKET_R, GD_CH = 4.0, 4.0                        # 16.11: углы выемки R4, на углах пластины — фаски 4 × 45°: пластина стоит на дне
                                                  # выемки без зазора, а R4 касается дна в 4 мм от стенки — фаска вдоль дна должна
                                                  # доходить дальше (0,2 + 4 = 4,2 > 4); у верхних углов хватает 2,55
GD_CH_Z1 = 2.0                                    # фаски пластины — на 2 мм выше выемки (z −6…+2): у кромки выемки нет острого угла
# винт установочный М10 × 10 (ГОСТ 8878-84 / DIN 913: без головки, шестигранник S5) — направляющая к стойке (16.11, пользователь:
# без большой головки, Ø10, стойку насквозь не проходить, ближе к левому краю — там напряжения меньше). Ось — в координатах
# стойки и направляющей (они совпадают). Резьба витками, как у пальца D и гайки М10 × 1,5 (под печать): у винта Ø9,7, впадина
# Ø7,9; в пластине направляющей (6 мм) и в стойке (глухое, 4 мм резьбы до винта; до задней грани 1,2 мм) — отверстие Ø8,78,
# впадина Ø10,84. Торец винта — заподлицо с площадкой Ø11,2 на дне «ванны» (z = 0): ничего не выступает
SCR_X = E - 5.5                                   # ближе к левому кронштейну: площадка — 1,4 мм до его грани
SCR_Y = (Y_BOT + GD_PL_Y1) / 2                    # середина пластины по высоте — −33,38
SCR_P, SCR_L = 1.5, 10.0                          # шаг, длина винта (z 0…−10)
SCR_RMAJ, SCR_RROOT = 4.85, 3.95                  # винт: наружный радиус, радиус впадины (как палец D)
HOLE_R_BORE, HOLE_R_ROOT = 4.39, 5.42             # отверстия: Ø8,78, впадина резьбы Ø10,84 (как гайка М10)
HOLE_Z_BOT = -11.3                                # глухое отверстие в стойке до z = −11,3 (стойка −12: остаётся 0,7)
GD_SPOT_R = 5.6                                   # площадка Ø11,2 на дне «ванны» (скругления выше z = 0 срезаны)
SCR_HEX_S, SCR_HEX_T = 5.0, 5.0                   # шестигранник под ключ S5, глубина 5
SCR_Z_HELIX = -12.0                               # винт: начало винтовой линии (центр впадины) — целое число шагов
HOLE_Z_HELIX = -10.5                              # стойка: линия с угла 180° (на полвитка раньше −9,75 при 0°) — та же фаза:
                                                  # впадины на полшага от впадин винта; с 0° неполный первый виток задевал конец винта
GD_Z_HELIX = -6.75                                # направляющая: то же, начало за задней гранью пластины


def lower_edge_y(ph, x):
    """y нижнего ребра кулисы (полоса 18 мм) при угле ph над точкой x"""
    return (x * sin(radians(ph)) - 9) / cos(radians(ph))


def upper_edge_y(ph, x):
    return (x * sin(radians(ph)) + 9) / cos(radians(ph))


LO_X0, LO_X1, LO_Y0 = 31.0, 42.0, -5.0            # нижний упор: x 31…42, низ на 5 мм ниже оси O
HI_X0, HI_X1, HI_Y1 = 15.0, 21.0, 60.0            # верхний упор: x 15…21, верх на 60 мм выше оси O
# кожух: наружные кромки от оси O, стенка 2 мм; z — от задней кромки (передняя грань стойки) до передней стенки
CV_X0, CV_X1, CV_Y0, CV_Y1, CV_T, CV_Z = -12.0, 45.5, -53.0, 62.0, 2.0, 58.0   # глубина 58: передняя стенка в 3 мм от конца пальца
# левая стенка — в 1 мм от закруглённого конца кулисы (x = −9); верхняя стенка лежит на верхнем упоре (y = 60): кожух висит на нём.
# Ниже кулисы (y ≤ −9) левая стенка утолщена до направляющей (x = e − 18,5) по всей глубине: кожух упирается в планку
# направляющей и её кронштейн и при надевании скользит по ним (вплотную вся стенка не подойдёт — мешает конец кулисы)
CV_PAD_Y1 = -9.0
CV_GAP = 1.0                                      # зазор между кулисой и краями паза
# защёлки кожуха (15.11, расчёт — ../snap_calc.py): язычок — часть боковой стенки (2 мм) шириной SN_B и длиной SN_L,
# отделён двумя прорезями SN_SLOT от задней кромки; на конце — крючок внутрь на SN_Y со скосом 30° к оси надвигания
# (z) и удерживающей гранью 90° при z = SN_ZH. На стойке — зацеп: стойка-перемычка и козырёк над крючком (z SN_ZH…SN_ZL),
# между козырьком и стенкой кожуха — 0,2 мм, между вершиной крючка и стойкой зацепа — 0,5 мм. Левая — выше утолщения стенки
# (y 25…35), правая — ниже паза под кулису и нижнего упора (y −30…−20). Закрыть кожух — ≈ 7–12 Н, снять — отжать язычки
SN_B, SN_L, SN_Y, SN_SLOT = 10.0, 30.0, 1.5, 1.0
SN_ZH, SN_ZL = 4.0, 7.0                           # крючок z 0…4 (под козырьком), козырёк z 4…7
SN_POS = {"left": (25.0, 35.0), "right": (-30.0, -20.0)}   # y язычков
SN_CLR, SN_POST = 0.2, 1.0                        # зазор козырёк — стенка; толщина стойки зацепа
SN_TAN = 0.5773502691896258                       # tg 30°


def snap_x(side):
    """x внутренней грани стенки и знак направления внутрь кожуха"""
    return (CV_X0 + CV_T, 1.0) if side == "left" else (CV_X1 - CV_T, -1.0)

# палец D (ось z, начало — задний торец): Ø10 — обойма 4 + зазор 1 + ползун 16 + 0,5 + шайба 2 (21,5…23,5); дальше Ø9,7
# с резьбой М10 × 1,5 до 32 (гайка 8 + выступ 0,5, фаска 1). Резьба под печать (FDM): профиль 60°, впадина пальца Ø7,9;
# гайка — отверстие Ø8,78, впадина Ø10,84: по диаметру зазор 0,3…0,4 мм, по виткам 0,2. Резьба начинается под шайбой (первая
# впадина — с 23,0), поэтому гайка доходит до шайбы. Сечение среза одно — между обоймой и ползуном, на Ø10
PIN_D, PIN_L1, PIN_L = 10.0, 23.5, 32.0           # PIN_L1 — конец гладкой части Ø10 (передняя грань шайбы)
D_THR, P_THR = 9.7, 1.5                           # наружный Ø резьбы пальца, шаг
R_PIN_ROOT = 3.95                                 # впадина пальца (вершина треугольника выреза)
R_NUT_ROOT = R_PIN_ROOT + 0.866 * P_THR + 0.2 / (2 * tan(radians(30)))   # впадина гайки (H = 0,866p + зазор 0,2 по виткам) — 5,42
R_NUT_HOLE = 4.39                                 # отверстие гайки Ø8,78
Z_HELIX = PIN_L1 - 0.5                            # начало винтовой линии пальца (центр первой впадины) — под шайбой
WASHER = (10.5, 20.0, 2.0)                        # шайба 10 ГОСТ 11371-78: d1, d2, s
NUT_S, NUT_M = 16.0, 8.0                          # гайка М10 ГОСТ 5915-70: размер под ключ, высота
Z_NUT_C = PIN_L1 + NUT_M / 2                      # середина гайки в системе пальца (начало системы гайки) — 27,5
PIN_PROFILE = [(0, 0), (4.5, 0), (5, 0.5), (5, PIN_L1), (D_THR / 2, PIN_L1), (D_THR / 2, PIN_L - 1), (D_THR / 2 - 1, PIN_L),
               (0, PIN_L)]                        # (r, z)


def cover_slot():
    """паз под кулису: полоса между нижним ребром кулисы при φк и верхним ребром при φн, с зазором CV_GAP"""
    uk, nk = (cos(radians(PH_K)), sin(radians(PH_K))), (-sin(radians(PH_K)), cos(radians(PH_K)))
    un, nn = (cos(radians(PH_N)), sin(radians(PH_N))), (-sin(radians(PH_N)), cos(radians(PH_N)))
    h = 9 + CV_GAP
    pk = lambda r: (r * uk[0] - h * nk[0], r * uk[1] - h * nk[1])
    pn = lambda r: (r * un[0] + h * nn[0], r * un[1] + h * nn[1])
    return [pk(0), pk(200), pn(200), pn(0)]


BOTTLE_H, BOTTLE_R = 226.5, 30.2                  # Wiegand-Glas Longneck 0,33 л, арт. 456-10-03: высота и радиус


def bottle_contour():
    """половина сечения бутылки (ось вращения x = 0, дно y = 0): венчик 26 H 180 — наружный Ø26,55, горло Ø17,4; плечо — две
    сопряжённые дуги. Стенка и начало плеча подобраны под массу 220 г из ТЗ и вместимость до краёв 355 мл (0,33 л + запас
    до края). Вершина (x, y) — отрезок к ней, (x, y, xc, yc, r, d) — дуга к ней"""
    rb, rn, t, b = BOTTLE_R, 13.0, 2.3, 5.0       # радиус корпуса, радиус шейки, стенка, дно
    y1, y2 = 98.0, 173.4                          # начало плеча, начало шейки
    dx, dy = rb - rn, y2 - y1
    s = (dx ** 2 + dy ** 2) / (2 * dx)            # сумма радиусов дуг: при ней они касаются друг друга
    r1, r2 = 0.76 * s, 0.24 * s                   # выпуклая и вогнутая дуги плеча
    c1, c2 = (rb - r1, y1), (rn + r2, y2)
    ux, uy = (c2[0] - c1[0]) / s, (c2[1] - c1[1]) / s
    tan_pt = lambda r: (c1[0] + r * ux, c1[1] + r * uy)   # точка касания дуг на радиусе r первой дуги
    ri = rb - t                                   # внутренний радиус корпуса
    return [(0.0, 0.0), (24.0, 0.0), (rb, 6.2, 24.0, 6.2, 6.2, 1), (rb, y1),
            (*tan_pt(r1), *c1, r1, 1), (rn, y2, *c2, r2, -1),
            (rn, 218.2), (13.3, 219.6), (13.3, 225.0), (12.0, BOTTLE_H), (8.7, BOTTLE_H), (8.7, 212.0), (rn - t, 205.0),
            (rn - t, y2), (*tan_pt(r1 - t), *c2, r2 + t, 1), (ri, y1, *c1, r1 - t, -1),
            (ri, b + 3.2), (ri - 3.2, b, ri - 3.2, b + 3.2, 3.2, -1), (0.0, b)]


# ================================================================ параметрический эскиз
class Sketch2D:
    """эскиз с ограничениями: отрезки — горизонтальность/вертикальность и совпадение концов, одна точка зафиксирована;
    длины и диаметры — управляющими (фиксированными) размерами, ассоциированными с геометрией. Итог — эскиз полностью
    определён («+» в дереве)."""

    def __init__(self, d2):
        self.d2 = d2

    def cons(self, obj, kind, index=0, partner=0, pindex=0):
        cp = k5.GetParamStruct(C.ko_ConstraintParam)
        cp.Init()
        cp.constrType, cp.index, cp.partner, cp.partnerIndex = kind, index, partner, pindex
        assert self.d2.ksSetObjConstraint(obj, cp), ("ограничение не наложено", kind)

    def drive(self, dim):
        """размер ассоциируется с геометрией и становится управляющим"""
        o = qi(k5.TransferReference(dim, self.d2.reference), A7.IDrawingObject1)
        assert o.Associate(), "размер не ассоциирован"
        c = qi(o.NewConstraint(), A7.IParametriticConstraint)
        c.ConstraintType = C.ksCFixedDim
        assert c.Create(), "размер не зафиксирован"

    def dim_lin(self, p1, p2, vertical, off):
        lp = k5.GetParamStruct(C.ko_LDimParam)
        dp = lp.GetDPar(); dp.Init(); dp.pt1 = dp.pt2 = 1
        sp = lp.GetSPar(); sp.Init()
        sp.x1, sp.y1, sp.x2, sp.y2 = p1[0], p1[1], p2[0], p2[1]
        sp.dx, sp.dy, sp.basePoint, sp.ps = (off, 0, 1, 1) if vertical else (0, off, 1, 0)
        tp = lp.GetTPar(); tp.Init(False); tp.bitFlag = 1; tp.sign = 0      # 1 — номинал определяется автоматически
        lp.SetDPar(dp); lp.SetSPar(sp); lp.SetTPar(tp)
        self.drive(self.d2.ksLinDimension(lp))

    def poly(self, pts, hv, dims, fix=0, style=1):
        """замкнутый контур: hv[i] — 'H', 'V' или None для отрезка i (pts[i] -> pts[i+1]); dims — номера отрезков с размером
        длины (горизонтальные и вертикальные); fix — номер вершины, закреплённой на месте"""
        n = len(pts)
        seg = [self.d2.ksLineSeg(*pts[i], *pts[(i + 1) % n], style) for i in range(n)]
        for i, t in enumerate(hv):
            if t:
                self.cons(seg[i], C.ksCHorizontal if t == "H" else C.ksCVertical)
        for i in range(n):
            self.cons(seg[i], C.ksCMergePoints, 1, seg[(i + 1) % n], 0)
        self.cons(seg[fix], C.ksCFixedPoint, 0)
        cx, cy = sum(x for x, _ in pts) / n, sum(y for _, y in pts) / n
        for i in dims:
            a, b = pts[i], pts[(i + 1) % n]
            if hv[i] == "H":
                self.dim_lin(a, b, False, 6 if a[1] > cy else -6)
            else:
                self.dim_lin(a, b, True, 6 if a[0] > cx else -6)
        return seg

    def rect(self, x0, y0, x1, y1):
        return self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "HVHV", (0, 1))

    def circle(self, xc, yc, r, concentric_to=None):
        c = self.d2.ksCircle(xc, yc, r, 1)
        if concentric_to:
            self.cons(c, C.ksCConcentricity, 0, concentric_to, 0)
        else:
            self.cons(c, C.ksCFixedPoint, 0)
        rp = k5.GetParamStruct(C.ko_RDimParam)
        dp = rp.GetDPar(); dp.Init(); dp.pt1 = dp.pt2 = 1
        sp = rp.GetSPar(); sp.Init(); sp.xc, sp.yc, sp.rad = xc, yc, r
        tp = rp.GetTPar(); tp.Init(False); tp.bitFlag = 1; tp.sign = 1        # знак диаметра
        rp.SetDPar(dp); rp.SetSPar(sp); rp.SetTPar(tp)
        self.drive(self.d2.ksDiamDimension(rp))
        return c

    def poly_fixed(self, pts):
        """замкнутый контур с наклонными сторонами: все вершины закреплены (эскиз полностью определён без размеров)"""
        n = len(pts)
        seg = [self.d2.ksLineSeg(*pts[i], *pts[(i + 1) % n], 1) for i in range(n)]
        for i in range(n):
            self.cons(seg[i], C.ksCMergePoints, 1, seg[(i + 1) % n], 0)
            self.cons(seg[i], C.ksCFixedPoint, 0)
        return seg

    def contour(self, pts):
        """замкнутый контур из отрезков и дуг (d = 1 — дуга против часовой): концы и центры закреплены, эскиз определён без размеров"""
        p0 = pts[-1][:2]
        for q in pts:
            x, y = q[:2]
            if len(q) == 2:
                obj, points = self.d2.ksLineSeg(*p0, x, y, 1), (0, 1)
            else:
                obj, points = self.d2.ksArcByPoint(q[2], q[3], q[4], *p0, x, y, q[5], 1), (0, 1, 2)
            for i in points:
                self.cons(obj, C.ksCFixedPoint, i)
            p0 = (x, y)

    def axis(self, x0, y0, x1, y1):
        """осевая линия для вращения: вертикальная, начало закреплено, длина — размером"""
        a = self.d2.ksLineSeg(x0, y0, x1, y1, 3)
        self.cons(a, C.ksCVertical)
        self.cons(a, C.ksCFixedPoint, 0)
        self.dim_lin((x0, y0), (x1, y1), True, -6)
        return a


# ================================================================ построение детали (API5)
class Part:
    def __init__(self, name, marking, material, color, opacity=1.0):
        self.doc = k5.Document3D()
        self.doc.Create(False, True)
        self.p = self.doc.GetPart(C3.pTop_Part)
        self.p.name, self.p.marking = name, marking
        self.p.SetMaterial(*material)
        self.color, self.opacity = color, opacity
        self.first = True
        self.sketches = []

    def plane_z(self, z):
        if abs(z) < 1e-9:
            return self.p.GetDefaultEntity(C3.o3d_planeXOY)
        pl = self.p.NewEntity(C3.o3d_planeOffset)
        d = pl.GetDefinition()
        d.SetPlane(self.p.GetDefaultEntity(C3.o3d_planeXOY))
        d.offset, d.direction = abs(z), z > 0
        pl.hidden = True
        pl.Create()
        return pl

    def sketch(self, z, draw, plane=None):
        sk = self.p.NewEntity(C3.o3d_sketch)
        d = sk.GetDefinition()
        d.SetPlane(plane or self.plane_z(z))
        sk.Create()
        try:
            draw(Sketch2D(d.BeginEdit()))
        finally:
            d.EndEdit()                           # эскиз не должен остаться в режиме редактирования при ошибке
        self.sketches.append(sk)
        return sk

    def extrude(self, sk, depth, cut=False, both=False):
        """выдавливание по +z на depth; cut + both — вырез в обе стороны: насквозь (depth = 0) или на depth в каждую"""
        kind = C3.o3d_cutExtrusion if cut else (C3.o3d_baseExtrusion if self.first else C3.o3d_bossExtrusion)
        ex = self.p.NewEntity(kind)
        d = ex.GetDefinition()
        if both:
            d.directionType = C3.dtBoth
            end = C3.etBlind if depth else C3.etThroughAll
            d.SetSideParam(True, end, depth, 0, False)
            d.SetSideParam(False, end, depth, 0, False)
        else:
            d.directionType = C3.dtNormal
            d.SetSideParam(True, C3.etBlind, depth, 0, False)
        d.SetSketch(sk)
        assert ex.Create(), ("операция не построена", self.p.name)
        if not cut:
            self.first = False

    def sketch_xz(self, draw):
        """эскиз на плоскости XOZ: координаты эскиза (u, v) = (x, −z) детали (проверено по центру масс пробного тела);
        ось вращения — ось v эскиза = ось z детали"""
        return self.sketch(0, draw, self.p.GetDefaultEntity(C3.o3d_planeXOZ))

    def revolve(self, sk, cut=False):
        kind = C3.o3d_cutRotated if cut else (C3.o3d_baseRotated if self.first else C3.o3d_bossRotated)
        ent = self.p.NewEntity(kind)
        d = ent.GetDefinition()
        d.directionType = C3.dtNormal
        d.SetSideParam(True, 360)
        d.SetSketch(sk)
        assert ent.Create(), ("вращение не построено", self.p.name)
        if not cut:
            self.first = False

    def thread(self, x, y, z, dr, pitch):
        """условная резьба по всей длине цилиндрической грани; начало — круговое ребро через точку (x, y, z)"""
        top = qi(k5.TransferInterface(self.doc, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
        objs = [qi(o, A7.IModelObject) for o in (top.FindObjectsByPoint(x, y, z, True) or ())]
        edges = [o for o in objs if o.ModelObjectType == C3.o3d_edge]
        assert len(edges) == 1, ("ребро под резьбу", self.p.name, len(edges))
        th = self.p.NewEntity(C3.o3d_thread)
        d = th.GetDefinition()
        d.SetBaseObject(A5.ksEntity(k5.TransferInterface(edges[0], C.ksAPI5Auto, 0)))
        d.autoDefinDr, d.dr, d.p, d.allLength = False, dr, pitch, True
        assert th.Create(), ("резьба не построена", self.p.name)
        return d.outside

    def prism_xz(self, pts_xz, y0, y1):
        """тело из профиля (x, z), выдавленного вдоль y от y0 до y1: эскиз на XOZ, смещённой к y0 (direction = y0 > 0;
        эскиз: u = x, v = −z), выдавливание прямо — к +y (проверено по объёму и центру масс, 15.11)"""
        pl = self.p.NewEntity(C3.o3d_planeOffset)
        pd = pl.GetDefinition()
        pd.SetPlane(self.p.GetDefaultEntity(C3.o3d_planeXOZ))
        pd.offset, pd.direction = abs(y0), y0 > 0
        pl.hidden = True
        pl.Create()
        sk = self.sketch(0, lambda s: s.poly_fixed([(x, -z) for x, z in pts_xz]), pl)
        ex = self.p.NewEntity(C3.o3d_bossExtrusion)
        ed = ex.GetDefinition()
        ed.directionType = C3.dtNormal
        ed.SetSideParam(True, C3.etBlind, y1 - y0, 0, False)
        ed.SetSketch(sk)
        assert ex.Create(), ("призма XZ не построена", self.p.name)

    def poly(self, pts, z0, z1, hv, dims, fix=0):
        self.extrude(self.sketch(z0, lambda s: s.poly(pts, hv, dims, fix)), z1 - z0)

    def box(self, x0, x1, y0, y1, z0, z1):
        self.extrude(self.sketch(z0, lambda s: s.rect(x0, y0, x1, y1)), z1 - z0)

    def cyl(self, xc, yc, r, z0, z1, r_in=None):
        def draw(s):
            c = s.circle(xc, yc, r)
            if r_in:
                s.circle(xc, yc, r_in, concentric_to=c)
        self.extrude(self.sketch(z0, draw), z1 - z0)

    def cut(self, draw, z0, z1):
        """вырез между плоскостями z0 и z1: эскиз в средней плоскости, выдавливание в обе стороны на половину толщины"""
        self.extrude(self.sketch((z0 + z1) / 2, draw), (z1 - z0) / 2, cut=True, both=True)

    def hole(self, xc, yc, r):
        self.extrude(self.sketch(0, lambda s: s.circle(xc, yc, r)), 0, cut=True, both=True)

    def fillet(self, points, r, length=None):
        """скругление радиуса r рёбер, проходящих через точки (x, y, z) детали; length — брать только рёбра такой длины
        (в углу FindObjectsByPoint отдаёт и соседние рёбра)"""
        top = qi(k5.TransferInterface(self.doc, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
        f = self.p.NewEntity(C3.o3d_fillet)
        fd = f.GetDefinition()
        fd.radius, fd.tangent = r, True
        arr = fd.array()
        for x, y, z in points:
            objs = [qi(o, A7.IModelObject) for o in (top.FindObjectsByPoint(x, y, z, True) or ())]
            es = [o for o in objs if o.ModelObjectType == C3.o3d_edge]
            if length:
                es = [e for e in es if abs(qi(e, A7.IEdge).GetLength(1) - length) < 0.01]
            # одно и то же ребро может прийти дважды (по разу от каждой из двух граней) — проверяем, что это одно ребро
            lens = {round(qi(e, A7.IEdge).GetLength(1), 4) for e in es}
            assert len(es) >= 1 and len(lens) == 1, ("ребро под скругление", self.p.name, (x, y, z), len(es), lens)
            arr.Add(A5.ksEntity(k5.TransferInterface(es[0], C.ksAPI5Auto, 0)))
        assert f.Create(), ("скругления не построены", self.p.name)

    def save(self, fname):
        self.p.SetAdvancedColor(rgb(self.color), 0.5, 0.6, 0.8, 0.8, self.opacity, 0.5)   # 1 — непрозрачная
        for t in (C3.o3d_planeXOY, C3.o3d_planeXOZ, C3.o3d_planeYOZ):  # системные плоскости не показывать в сборке
            pl = self.p.GetDefaultEntity(t)
            pl.hidden = True
            pl.Update()
        self.p.Update()
        states = [qi(k5.TransferInterface(sk, C.ksAPI7Dual, 0), A7.ISketch).ConstraintsState for sk in self.sketches]
        assert all(st == C.ksStateWellConstrained for st in states), (fname, states)
        path = os.path.join(PARTS_DIR, fname)
        self.doc.SaveAs(path)
        assert not os.path.exists(path + ".apmf"), "APM FEM подключился к детали: удалите .apmf, закройте КОМПАС и запустите заново"
        # масса — у своего документа: активным окном может оказаться другой (КОМПАС восстанавливает черновики после сбоя)
        d7 = k5.TransferInterface(self.doc, C.ksAPI7Dual, 0)
        mi = qi(qi(d7, A7.IKompasDocument3D).TopPart, A7.IMassInertiaParam7)
        mass = mi.Mass
        self.doc.close()
        print(f"  {fname}: масса {mass:.1f} г, эскизов {len(states)} — все полностью определены")
        return path, mass


ST3, ST45, GLASS = ("Ст3сп ГОСТ 380-2005", 7.85), ("Сталь 45 ГОСТ 1050-2013", 7.85), ("Стекло", 2.5)
FILES = {"stand": "УКП.00.001 Стойка.m3d", "kulisa": "УКП.01.001 Кулиса.m3d", "kamen": "УКП.02.001 Камень.m3d",
         "pin": "УКП.02.002 Палец D.m3d", "polzun": "УКП.03.001 Ползун.m3d", "washer": "Шайба 10 ГОСТ 11371-78.m3d",
         "nut": "Гайка М10 ГОСТ 5915-70.m3d", "cover": "УКП.04.001 Кожух.m3d", "bottle": "УКП.05.001 Бутылка.m3d",
         "guide": "УКП.00.002 Направляющая.m3d", "screw": "Винт установочный М10 × 10 ГОСТ 8878-84.m3d",
         "head": "УКП.03.002 Головка ползуна.m3d"}      # 21.11: ползун разрезан под печать — головка клеится на хвостовик штока
FASTENER = "#c3c8cf"                              # шайба и гайка — светлая сталь
RIB_L, RIB_T, R_FIL_ST = 80.0, 8.0, 5.0           # рёбра стойки: вылет по основанию 80 (вся глубина основания), толщина 8; скругления R5
RIB_H = round(RIB_L * tan(radians(60.0)), 1)      # высота по листу 103,9: наклон ребра 60° к основанию
WALL_HOLES = [(X_ST0 + 8, Y_ST0 + H_ST - 10), (X_ST1 - 8, Y_ST0 + H_ST - 10), (X_ST0 + 8, Y_ST0 + RIB_H + 10),
              (X_ST1 - 8, Y_ST0 + RIB_H + 10)]                      # нижние — на 10 мм выше рёбер (шляпка шурупа не упирается)


def build():
    os.makedirs(PARTS_DIR, exist_ok=True)
    mass = {}
    print("Детали:")
    # стойка — одна деталь: лист 92 × 390 × 12 (крепится к стене), основание 128 × 92 × 20 под бутылку, ось O Ø10, направляющая
    # ползуна, нижний и верхний упоры;
    # начало — ось O на передней грани листа
    mass["stand"] = build_stand()

    L, R_ = 500.0, 9.0                                                # кулиса: полоса 8 × 18 × 500 + ступица Ø16 × 12
    p = Part("Кулиса", "УКП.01.001", ST3, "#2d3540")
    p.box(0, L - R_, -R_, R_, 0, 8.0)                                 # полоса между центрами скруглений
    p.extrude(p.sketch(0, lambda s: (s.circle(0, 0, R_), s.circle(L - R_, 0, R_))), 8.0)   # скругления концов R9
    p.cyl(0, 0, 8.0, -12.0, 0, r_in=5.0)
    p.hole(0, 0, 5.0)
    mass["kulisa"] = p.save(FILES["kulisa"])[1]

    p = Part("Камень", "УКП.02.001", ST45, "#e8c99a")               # обойма 20 мм, стенки 4, губки, отверстие Ø10 под палец
    p.box(-10, 10, 9.5, 13.5, -15.5, 0)
    p.box(-10, 10, -13.5, -9.5, -15.5, 0)
    p.box(-10, 10, -9.5, 9.5, -4.0, 0)
    p.box(-7, 10, 6.8, 9.5, -15.5, -13.0)                            # губки за рёбрами полосы, у оси O укорочены на 3 мм
    p.box(-7, 10, -9.5, -6.8, -15.5, -13.0)
    p.hole(0, 0, PIN_D / 2)                                           # под палец D с натягом (H7/r6)
    mass["kamen"] = p.save(FILES["kamen"])[1]

    mass["pin"] = build_pin()

    mass["washer"] = build_washer()
    mass["nut"] = build_nut()
    mass["screw"] = build_screw()

    mass["polzun"] = build_polzun()

    # кожух: коробка из листа 2 мм, открытая сзади (к стойке); паз под кулису в правой и верхней стенках и паз под шток в дне
    # открыты к задней кромке — кожух снимается сдвигом вперёд; начало — ось O на задней кромке
    mass["cover"] = build_cover()
    # бутылка: полая, стекло; не часть изделия, ставится на основание по оси ползуна
    p = Part("Бутылка", "УКП.05.001", GLASS, "#8a4b16", opacity=0.6)
    p.revolve(p.sketch(0, lambda s: (s.contour(bottle_contour()), s.axis(0, -10, 0, BOTTLE_H + 10))))
    mass["bottle"] = p.save(FILES["bottle"])[1]
    json.dump(mass, open(os.path.join(HERE, "parts_mass.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def build_cover():
    p = Part("Кожух", "УКП.04.001", ("АБС-пластик", 1.05), "#b03a2e")
    p.box(CV_X0, CV_X1, CV_Y0, CV_Y1, 0, CV_Z)
    p.cut(lambda s: s.rect(CV_X0 + CV_T, CV_Y0 + CV_T, CV_X1 - CV_T, CV_Y1 - CV_T), 0, CV_Z - CV_T)   # полость
    p.box(CV_X0 + CV_T, E - 18.5, CV_Y0 + CV_T, CV_PAD_Y1, 0, CV_Z - CV_T)     # утолщение левой стенки до направляющей
    p.cut(lambda s: s.poly_fixed(cover_slot()), 0, -13.5 - Z_ST + CV_GAP)       # паз под кулису: до передней грани полосы (z = −13,5) + 1 мм
    p.cut(lambda s: s.rect(E - 6, CV_Y0 - 1, E + 6, CV_Y0 + CV_T + 1), 0, -Z_ST + 6)   # паз под шток Ø8 в дне
    for side, (y0, y1) in SN_POS.items():                                        # защёлки (15.11)
        xw, k = snap_x(side)                                                     # внутренняя грань стенки, «внутрь» = k
        xa, xb = sorted((xw - k * (CV_T + 1), xw + k * 1))                       # прорезь — через всю стенку с запасом
        for ya, yb in ((y0 - SN_SLOT, y0), (y1, y1 + SN_SLOT)):
            p.cut(lambda s, xa=xa, xb=xb, ya=ya, yb=yb: s.rect(xa, ya, xb, yb), -1.0, SN_L)   # от задней кромки
        dz = SN_Y / SN_TAN                                                       # скос 30° к оси z
        p.prism_xz([(xw, 0.06), (xw + k * SN_Y, 0.06 + dz), (xw + k * SN_Y, SN_ZH), (xw, SN_ZH)], y0, y1)   # крючок
    return p.save(FILES["cover"])[1]


def build_stand():
    """стойка: лист, основание, ось O, упоры, выемка под направляющую (отдельная деталь), отверстия под шурупы, рёбра, скругления"""
    p = Part("Стойка", "УКП.00.001", ST3, "#8a94a3")
    p.box(X_ST0, X_ST1, Y_ST0, Y_ST0 + H_ST, -B_ST, 0)                # лист
    p.box(X_ST0 - 18, X_ST1 + 18, Y_ST0 - 20, Y_ST0, -B_ST, -B_ST + 92)     # основание 128 × 92 × 20: задняя кромка заподлицо с листом
                                                                      # (у стены), лист посередине по ширине, ось бутылки — по глубине
    p.cyl(0, 0, 5.0, 0, 20.5)                                         # ось O Ø10 — до передней грани кулисы
    for side, (y0, y1) in SN_POS.items():         # зацепы защёлок кожуха (15.11): козырёк над крючком на стойке-перемычке
        xw, k = snap_x(side)
        xl0, xl1 = xw + k * SN_CLR, xw + k * (SN_CLR + SN_Y + 1.5)           # козырёк: от стенки кожуха +0,2 на 3 мм внутрь
        xp0 = xl1 - k * SN_POST                                             # стойка зацепа — у внутреннего края козырька
        p.box(min(xp0, xl1), max(xp0, xl1), y0, y1, 0, SN_ZH)
        p.box(min(xl0, xl1), max(xl0, xl1), y0, y1, SN_ZH, SN_ZL)
    # выемка под пластину направляющей (УКП.00.002): глубина GD_PL_T из 12 мм — не насквозь
    p.cut(lambda s: s.rect(GD_X0 - POCKET_GAP, Y_BOT, GD_X1 + POCKET_GAP, GD_PL_Y1 + POCKET_GAP), -GD_PL_T, 0)
    p.fillet([(x, y, -GD_PL_T / 2) for x in (GD_X0 - POCKET_GAP, GD_X1 + POCKET_GAP)            # 16.11: углы выемки R4
              for y in (Y_BOT, GD_PL_Y1 + POCKET_GAP)], POCKET_R, length=GD_PL_T)
    p.poly([(LO_X0, LO_Y0), (LO_X1, LO_Y0), (LO_X1, lower_edge_y(PH_K, LO_X1)), (LO_X0, lower_edge_y(PH_K, LO_X0))],
           0, 20.5, ("H", "V", None, "V"), (0, 1, 3))                  # нижний упор: грань по нижнему ребру кулисы при φк
    p.poly([(HI_X0, upper_edge_y(PH_N, HI_X0)), (HI_X1, upper_edge_y(PH_N, HI_X1)), (HI_X1, HI_Y1), (HI_X0, HI_Y1)],
           0, 20.5, (None, "V", "H", "V"), (1, 2, 3), fix=3)           # верхний упор: грань по верхнему ребру кулисы при φн
    # 16.11: отверстия под шурупы к стене (WALL_HOLES) убраны — стойка стоит на столе на основании (просьба пользователя)
    # рёбра жёсткости (косынки) 8 мм по краям листа: треугольник 80 по основанию × 138,6 по листу (наклон 60°). Клин
    # выдавливается из эскиза на плоскости YOZ (эскиз: u = −z, v = −y; «прямое» направление — к −x) на всю ширину листа,
    # затем середина вырезается — остаются рёбра x X_ST0…X_ST0+6 и X_ST1−6…X_ST1 (бутылка Ø60 между ними, зазор ≥ 8 мм)
    tri = [(0.0, -Y_ST0), (-RIB_L, -Y_ST0), (0.0, -Y_ST0 - RIB_H)]  # (y, z): (Y_ST0, 0), (Y_ST0, RIB_L), (Y_ST0 + RIB_H, 0)
    sk = p.sketch(0, lambda s: s.poly_fixed(tri), p.p.GetDefaultEntity(C3.o3d_planeYOZ))
    ex = p.p.NewEntity(C3.o3d_bossExtrusion)
    ed = ex.GetDefinition()
    ed.directionType = C3.dtBoth
    ed.SetSideParam(True, C3.etBlind, -X_ST0, 0, False)             # к −x до левой кромки листа
    ed.SetSideParam(False, C3.etBlind, X_ST1, 0, False)             # к +x до правой кромки
    ed.SetSketch(sk)
    assert ex.Create(), "клин рёбер не построен"
    p.cut(lambda s: s.rect(X_ST0 + RIB_T, Y_ST0, X_ST1 - RIB_T, Y_ST0 + RIB_H + 1), 0, RIB_L + 1)   # вырез z 0…61 (в обе стороны от середины — односторонний вырез уходит к −z)
    # скругления R5: внутренний угол лист–основание между рёбрами и 4 вертикальных угла основания
    p.fillet([((X_ST0 + X_ST1) / 2, Y_ST0, 0.0)] +
             [(x, Y_ST0 - 10, z) for x in (X_ST0 - 18, X_ST1 + 18) for z in (-B_ST, -B_ST + 92)], R_FIL_ST)
    # 16.11: глухое отверстие М10 × 1,5 под винт направляющей — от дна выемки до z = −10,8, витками
    p.cut(lambda s: s.circle(SCR_X, SCR_Y, HOLE_R_BORE), HOLE_Z_BOT, -GD_PL_T)
    sp = helix(p, HOLE_Z_HELIX, -GD_PL_T + 1.0, SCR_RMAJ, SCR_P, SCR_X, SCR_Y, first_angle=180.0)
    r_in = HOLE_R_BORE - 0.2
    hw = (HOLE_R_ROOT - r_in) * tan(radians(30))
    assert HOLE_Z_HELIX - hw > HOLE_Z_BOT
    # профиль — в начале линии: угол 180° — со стороны −x от оси
    thread_cut(p, [(SCR_X - HOLE_R_ROOT, HOLE_Z_HELIX), (SCR_X - r_in, HOLE_Z_HELIX - hw), (SCR_X - r_in, HOLE_Z_HELIX + hw)], sp, SCR_Y)
    return p.save(FILES["stand"])[1]


PIN_COLOR = "#7fae6a"                             # палец D — отдельная деталь, свой цвет (как на рис. 13 расчёта)
GUIDE_COLOR = "#5b7896"                           # направляющая — отдельная деталь, сталь синеватого оттенка


def build_guide():
    """направляющая ползуна: задняя пластина (в выемке стойки), два кронштейна и две планки у боковых граней ползуна.
    ВНИМАНИЕ (15.11): рабочий файл «Детали/УКП.00.002 Направляющая.m3d» доработан пользователем в КОМПАСе (скругления «ванны»
    R10/R14 — нормальной операцией «Скругление», 603,5 г); этот скрипт строит её приближённо (выдавливанием профиля) и при
    запуске перезапишет файл пользователя — перестраивать только по просьбе: python kompas_build.py guide --force"""
    assert "--force" in sys.argv, "направляющая доработана пользователем — не перезаписываю (ключ --force)"
    p = Part("Направляющая", "УКП.00.002", ST3, GUIDE_COLOR)
    p.box(GD_X0, GD_X1, Y_BOT, GD_PL_Y1, -GD_PL_T, 0)                 # пластина
    for xa, xb in ((GD_X0, E - 12.5), (E + 12.5, GD_X1)):
        p.box(xa, xb, Y_BOT, GD_PL_Y1, 0, GD_Z0)                      # кронштейн
        p.box(xa, xb, Y_BOT, Y_TOP, GD_Z0, GD_Z1)                     # планка
    p.fillet([((GD_X0 + E - 12.5) / 2, GD_PL_Y1, GD_Z0), ((E + 12.5 + GD_X1) / 2, GD_PL_Y1, GD_Z0)], GD_R)
    # «ванна» (пользователь 15.11): скругления внутренних углов кронштейн — пластина R10 слева и R14 справа на всей высоте
    # кронштейна. Операция «Скругление» на этих рёбрах в КОМПАСе v25 получается недействительной (при любом радиусе), поэтому
    # тот же профиль (угол минус дуга) выдавливается вдоль y: эскиз на плоскости XOZ, смещённой к y = Y_BOT (direction=False —
    # в сторону −y; эскиз: u = x, v = −z), выдавливание прямо на высоту кронштейна. Проверено по массе (+16,33 г, как у
    # пользователя: 603,5) и по центру масс (центр «ванны» по y — середина кронштейна)
    pl = p.p.NewEntity(C3.o3d_planeOffset)
    pd = pl.GetDefinition()
    pd.SetPlane(p.p.GetDefaultEntity(C3.o3d_planeXOZ))
    pd.offset, pd.direction = abs(Y_BOT), False
    pl.hidden = True
    pl.Create()
    x0, x1, r0, r1 = E - 12.5, E + 12.5, GD_RU_L, GD_RU_R
    sk = p.sketch(0, lambda s: (s.contour([(x0 + r0, 0.0), (x0, -r0, x0 + r0, -r0, r0, 1), (x0, 0.0)]),
                                s.contour([(x1 - r1, 0.0), (x1, -r1, x1 - r1, -r1, r1, -1), (x1, 0.0)])), pl)
    ex = p.p.NewEntity(C3.o3d_bossExtrusion)
    ed = ex.GetDefinition()
    ed.directionType = C3.dtNormal
    ed.SetSideParam(True, C3.etBlind, GD_PL_Y1 - Y_BOT, 0, False)
    ed.SetSketch(sk)
    assert ex.Create(), "«ванна» не построена"
    return p.save(FILES["guide"])[1]


ST40X = ("Сталь 40Х ГОСТ 4543-2016", 7.85)          # палец: подшипниковая нагрузка (APM 192 МПа > 142 для стали 45)


def helix(p, z0, z1, r_path, pitch=None, xc=0.0, yc=0.0, first_angle=0.0):
    """винтовая линия по оси, параллельной z (через xc, yc), от z0 до z1, шаг pitch (по умолчанию P_THR), правая; начало —
    по направлению +x от оси (у пальца и гайки, у винта и отверстия в стойке одинаково)"""
    pitch = pitch or P_THR
    sp = p.p.NewEntity(C3.o3d_cylindricSpiral)
    sd = sp.GetDefinition()
    sd.SetPlane(p.plane_z(z0))
    sd.SetLocation(xc, yc)
    sd.buildMode = 0
    sd.diam, sd.step, sd.height, sd.turn = 2 * r_path, pitch, z1 - z0, (z1 - z0) / pitch
    sd.buildDir, sd.turnDir, sd.firstAngle = True, True, first_angle
    assert sp.Create(), "винтовая линия не построена"
    sp.hidden = True                              # вспомогательная линия — не показывать в детали и сборке
    sp.Update()
    return sp


def xz_plane(p, y0):
    """плоскость, параллельная XOZ, через y = y0 (эскиз на ней: u = x, v = −z — как на XOZ)"""
    if abs(y0) < 1e-9:
        return p.p.GetDefaultEntity(C3.o3d_planeXOZ)
    pl = p.p.NewEntity(C3.o3d_planeOffset)
    pd = pl.GetDefinition()
    pd.SetPlane(p.p.GetDefaultEntity(C3.o3d_planeXOZ))
    pd.offset, pd.direction = abs(y0), y0 > 0
    pl.hidden = True
    pl.Create()
    return pl


def thread_cut(p, tri_xz, sp, y0=0.0):
    """вырез треугольного профиля (x, z) по винтовой линии; профиль — ровно в начале линии (при sketchShiftType = 1 КОМПАС
    переносит эскиз в начало траектории); y0 — плоскость профиля (ось резьбы не на оси детали)"""
    sk = p.sketch(0, lambda s: s.poly_fixed([(x, -z) for x, z in tri_xz]), xz_plane(p, y0))
    ce = p.p.NewEntity(C3.o3d_cutEvolution)
    cd = ce.GetDefinition()
    cd.sketchShiftType = 1
    cd.SetSketch(sk)
    cd.PathPartArray().Add(sp)
    assert ce.Create(), "резьба не вырезана"


def build_pin():
    """палец D: телом вращения вокруг z; фаски 0,5 сзади и 1 на резьбовом конце, резьба М10 × 1,5 — витки"""
    p = Part("Палец D", "УКП.02.002", ST40X, PIN_COLOR)
    p.revolve(p.sketch_xz(lambda s: (s.contour([(r, -z) for r, z in PIN_PROFILE]), s.axis(0, 5, 0, -PIN_L - 5))))
    rt = D_THR / 2
    sp = helix(p, Z_HELIX, PIN_L + P_THR, rt)
    hw = (rt + 0.3 - R_PIN_ROOT) * tan(radians(30))
    thread_cut(p, [(R_PIN_ROOT, Z_HELIX), (rt + 0.3, Z_HELIX - hw), (rt + 0.3, Z_HELIX + hw)], sp)
    return p.save(FILES["pin"])[1]


def build_washer():
    d1, d2, s = WASHER
    p = Part("Шайба 10 ГОСТ 11371-78", "", ST3, FASTENER)
    p.cyl(0, 0, d2 / 2, 0, s, r_in=d1 / 2)
    return p.save(FILES["washer"])[1]


def build_nut():
    """гайка: шестигранник S16 × 8 (вершины на окружности S / cos 30°), отверстие Ø8,78 с витками М10 × 1,5, фаски 30° на углах
    с обеих сторон от окружности 0,9·S; начало — в средней плоскости. Винтовая линия — та же, что у пальца, пересчитанная
    в систему гайки (гайка на пальце: середина на Z_NUT_C, без поворота), — впадины гайки против выступов пальца"""
    R6, h = NUT_S / 2 / cos(radians(30)), NUT_M / 2
    p = Part("Гайка М10 ГОСТ 5915-70", "", ST3, FASTENER)
    p.extrude(p.sketch(-h, lambda s: s.poly_fixed([(R6 * cos(radians(30 + 60 * k)), R6 * sin(radians(30 + 60 * k)))
                                                   for k in range(6)])), NUT_M)
    p.hole(0, 0, R_NUT_HOLE)
    r0, r1 = 0.45 * NUT_S, R6 + 0.5
    dz = (r1 - r0) * tan(radians(30))
    p.revolve(p.sketch_xz(lambda s: (s.contour([(r0, h), (r1, h), (r1, h - dz)]), s.contour([(r0, -h), (r1, -h + dz), (r1, -h)]),
                                     s.axis(0, h + 2, 0, -h - 2))), cut=True)
    zh = Z_HELIX + P_THR / 2 - 2 * P_THR - Z_NUT_C     # начало линии — за задним торцом гайки, в фазе с пальцем
    assert zh < -h - 0.75
    sp = helix(p, zh, h + P_THR, D_THR / 2)
    r_in = 4.2
    hw = (R_NUT_ROOT - r_in) * tan(radians(30))
    thread_cut(p, [(R_NUT_ROOT, zh), (r_in, zh - hw), (r_in, zh + hw)], sp)
    return p.save(FILES["nut"])[1]


def build_screw():
    """винт установочный М10 × 10 ГОСТ 8878-84: цилиндр Ø9,7 с фасками 0,5 сверху и 1 на конце, шестигранник S5 × 5 в торце,
    резьба М10 × 1,5 витками по всей длине; начало — центр верхнего торца, винт к −z (как ставится)"""
    p = Part("Винт установочный М10 × 10 ГОСТ 8878-84", "", ST45, FASTENER)
    prof = [(0, 0), (SCR_RMAJ - 0.5, 0), (SCR_RMAJ, -0.5), (SCR_RMAJ, -SCR_L + 1.0), (SCR_RMAJ - 1.0, -SCR_L), (0, -SCR_L)]
    p.revolve(p.sketch_xz(lambda s: (s.contour([(r, -z) for r, z in prof]), s.axis(0, -5, 0, SCR_L + 5))))
    rh = SCR_HEX_S / 2 / cos(radians(30))
    p.cut(lambda s: s.poly_fixed([(rh * cos(radians(60 * k)), rh * sin(radians(60 * k))) for k in range(6)]), -SCR_HEX_T, 0.5)
    sp = helix(p, SCR_Z_HELIX, SCR_P, SCR_RMAJ, SCR_P)
    hw = (SCR_RMAJ + 0.3 - SCR_RROOT) * tan(radians(30))
    thread_cut(p, [(SCR_RROOT, SCR_Z_HELIX), (SCR_RMAJ + 0.3, SCR_Z_HELIX - hw), (SCR_RMAJ + 0.3, SCR_Z_HELIX + hw)], sp)
    return p.save(FILES["screw"])[1]


def build_polzun():
    """ползун: направляемая часть 24 × 40 × 16 с отверстием под палец D, шток Ø8 × L_ROD и головка Ø40 с конической
    горловиной (не плоское дно): вход Ø32,1 → Ø28,6 на длине хода обжима 6 мм, выше — цилиндр Ø28,6 до потолка полости.
    Шток и головка — одним телом вращения вокруг y"""
    p = Part("Ползун", "УКП.03.001", ST3, "#3a4049")
    p.box(-12, 12, -20, 20, -8.0, 8.0)
    p.revolve(p.sketch(0, lambda s: (s.contour(SLIDER_PROFILE), s.axis(0, 0, 0, Y_HB - 6))))
    p.hole(0, 0, 5.0)
    return p.save(FILES["polzun"])[1]


if __name__ == "__main__":
    if sys.argv[1:] and set(a for a in sys.argv[1:] if a != "--force") <= {"polzun", "pin", "washer", "nut", "stand", "cover", "guide", "screw"}:   # перестроить только эти детали, массы остальных — как были
        mj = os.path.join(HERE, "parts_mass.json")
        m = json.load(open(mj, encoding="utf-8"))
        for k in (a for a in sys.argv[1:] if a != "--force"):
            m[k] = {"polzun": build_polzun, "pin": build_pin, "washer": build_washer, "nut": build_nut, "stand": build_stand, "cover": build_cover, "guide": build_guide, "screw": build_screw}[k]()
        json.dump(m, open(mj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        # сопряжения сборки ссылаются на грани деталей; у перестроенной детали грани новые — старая сборка откроется с «!»
        print("ВАЖНО: закройте сборку без сохранения и пересоберите её: python kompas_assembly.py")
    else:
        build()
