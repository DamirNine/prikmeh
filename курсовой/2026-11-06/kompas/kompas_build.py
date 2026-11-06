# -*- coding: utf-8 -*-
"""Детали укупоривателя в КОМПАС-3D v25 (Учебная) через API (COM) — каждая деталь отдельно, в своей системе координат
от своей базы; файлы — в папке «Детали». Сборка — kompas_assembly.py (детали соединяются сопряжениями).

Детали: Стойка (лист с отверстиями под крепёж к стене, основание под бутылку, ось O, направляющая ползуна, нижний и верхний
упоры — одна деталь),
Кулиса (полоса со ступицей, рукоять — конец полосы), Камень с пальцем D, Ползун, Кожух (закрывает механизм, снимается
вперёд), Бутылка (обрабатываемое изделие: стоит на основании, по оси ползуна). Базы (ось z при сборке — к наблюдателю, ползун — в плоскости z = 0 сборки): Стойка — ось O на передней грани листа;
Кулиса — ось O на задней грани полосы, x — вдоль кулисы; Камень — ось пальца на передней грани обоймы; Ползун — ось
отверстия под палец в средней плоскости; Бутылка — центр дна, y вдоль оси."""
import json, os, subprocess, time
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
Y_ST0 = -325.25                                   # низ листа от оси O = дно бутылки: yD(φн) − (20 + шток + 24) − (226,5 + 6 + 10)
Z_ST = -34.0                                      # передняя грань стойки в сборке
Y_BOT, Y_TOP = yD(PH_K) - 55, yD(PH_N) + 26       # направляющая: на 35 мм ниже и на 6 мм выше хода ползуна


def lower_edge_y(ph, x):
    """y нижнего ребра кулисы (полоса 18 мм) при угле ph над точкой x"""
    return (x * sin(radians(ph)) - 9) / cos(radians(ph))


def upper_edge_y(ph, x):
    return (x * sin(radians(ph)) + 9) / cos(radians(ph))


LO_X0, LO_X1, LO_Y0 = 31.0, 42.0, -5.0            # нижний упор: x 31…42, низ на 5 мм ниже оси O
HI_X0, HI_X1, HI_Y1 = 15.0, 21.0, 60.0            # верхний упор: x 15…21, верх на 60 мм выше оси O
# кожух: наружные кромки от оси O, стенка 2 мм; z — от задней кромки (передняя грань стойки) до передней стенки
CV_X0, CV_X1, CV_Y0, CV_Y1, CV_T, CV_Z = -17.0, 45.5, -53.0, 64.0, 2.0, 46.0
CV_GAP = 1.0                                      # зазор между кулисой и краями паза


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

    def sketch(self, z, draw):
        sk = self.p.NewEntity(C3.o3d_sketch)
        d = sk.GetDefinition()
        d.SetPlane(self.plane_z(z))
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

    def revolve(self, sk):
        ent = self.p.NewEntity(C3.o3d_baseRotated if self.first else C3.o3d_bossRotated)
        d = ent.GetDefinition()
        d.directionType = C3.dtNormal
        d.SetSideParam(True, 360)
        d.SetSketch(sk)
        assert ent.Create(), ("вращение не построено", self.p.name)
        self.first = False

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
FILES = {"stand": "УКП.00.001 Стойка.m3d", "kulisa": "УКП.01.001 Кулиса.m3d",
         "kamen": "УКП.02.001 Камень с пальцем D.m3d", "polzun": "УКП.03.001 Ползун.m3d", "cover": "УКП.04.001 Кожух.m3d",
         "bottle": "УКП.05.001 Бутылка.m3d"}
WALL_HOLES = [(X_ST0 + 8, Y_ST0 + H_ST - 10), (X_ST1 - 8, Y_ST0 + H_ST - 10), (X_ST0 + 8, Y_ST0 + 10), (X_ST1 - 8, Y_ST0 + 10)]


def build():
    os.makedirs(PARTS_DIR, exist_ok=True)
    mass = {}
    print("Детали:")
    # стойка — одна деталь: лист 92 × 390 × 12 (крепится к стене), основание 128 × 92 × 20 под бутылку, ось O Ø10, направляющая
    # ползуна, нижний и верхний упоры;
    # начало — ось O на передней грани листа
    p = Part("Стойка", "УКП.00.001", ST3, "#8a94a3")
    p.box(X_ST0, X_ST1, Y_ST0, Y_ST0 + H_ST, -B_ST, 0)                # лист
    p.box(X_ST0 - 18, X_ST1 + 18, Y_ST0 - 20, Y_ST0, -B_ST, -B_ST + 92)     # основание 128 × 92 × 20: задняя кромка заподлицо с листом
                                                                      # (у стены), лист посередине по ширине, ось бутылки — по глубине
    p.cyl(0, 0, 5.0, 0, 20.5)                                         # ось O Ø10 — до передней грани кулисы
    for xa, xb in ((E - 18.5, E - 12.5), (E + 12.5, E + 18.5)):      # направляющая: планки у боковых граней ползуна
        p.box(xa, xb, Y_BOT, Y_TOP, 26.0, 42.0)
        p.box(xa, xb, Y_BOT, Y_BOT + 12.0, 0, 26.0)                   # кронштейны планок
    p.poly([(LO_X0, LO_Y0), (LO_X1, LO_Y0), (LO_X1, lower_edge_y(PH_K, LO_X1)), (LO_X0, lower_edge_y(PH_K, LO_X0))],
           0, 20.5, ("H", "V", None, "V"), (0, 1, 3))                  # нижний упор: грань по нижнему ребру кулисы при φк
    p.poly([(HI_X0, upper_edge_y(PH_N, HI_X0)), (HI_X1, upper_edge_y(PH_N, HI_X1)), (HI_X1, HI_Y1), (HI_X0, HI_Y1)],
           0, 20.5, (None, "V", "H", "V"), (1, 2, 3), fix=3)           # верхний упор: грань по верхнему ребру кулисы при φн
    for x, y in WALL_HOLES:                                          # 4 отверстия Ø6 под шурупы: 8 мм от боковых краёв (шляпка не заходит под кожух), 10 от верхнего и нижнего
        p.hole(x, y, 3.0)
    mass["stand"] = p.save(FILES["stand"])[1]

    L, R_ = 500.0, 9.0                                                # кулиса: полоса 8 × 18 × 500 + ступица Ø16 × 12
    p = Part("Кулиса", "УКП.01.001", ST3, "#2d3540")
    p.box(0, L - R_, -R_, R_, 0, 8.0)                                 # полоса между центрами скруглений
    p.extrude(p.sketch(0, lambda s: (s.circle(0, 0, R_), s.circle(L - R_, 0, R_))), 8.0)   # скругления концов R9
    p.cyl(0, 0, 8.0, -12.0, 0, r_in=5.0)
    p.hole(0, 0, 5.0)
    mass["kulisa"] = p.save(FILES["kulisa"])[1]

    p = Part("Камень с пальцем D", "УКП.02.001", ST45, "#e8c99a")   # обойма 20 мм, стенки 4, губки, палец Ø10 × 17
    p.box(-10, 10, 9.5, 13.5, -15.5, 0)
    p.box(-10, 10, -13.5, -9.5, -15.5, 0)
    p.box(-10, 10, -9.5, 9.5, -4.0, 0)
    p.box(-7, 10, 6.8, 9.5, -15.5, -13.0)                            # губки за рёбрами полосы, у оси O укорочены на 3 мм
    p.box(-7, 10, -9.5, -6.8, -15.5, -13.0)
    p.cyl(0, 0, 5.0, 0, 17.0)
    mass["kamen"] = p.save(FILES["kamen"])[1]

    def rod(s):                                                       # шток Ø8 и головка Ø40 × 24 вращением вокруг y
        y1, y2 = -20 - L_ROD, -44 - L_ROD
        s.poly([(0, -20), (4, -20), (4, y1), (20, y1), (20, y2), (0, y2)], "HVHVHV", (0, 1, 3, 4))
        s.axis(0, 0, 0, y2 - 6)
    p = Part("Ползун", "УКП.03.001", ST3, "#3a4049")
    p.box(-12, 12, -20, 20, -8.0, 8.0)
    p.revolve(p.sketch(0, rod))
    p.hole(0, 0, 5.0)
    mass["polzun"] = p.save(FILES["polzun"])[1]

    # кожух: коробка из листа 2 мм, открытая сзади (к стойке); паз под кулису в правой и верхней стенках и паз под шток в дне
    # открыты к задней кромке — кожух снимается сдвигом вперёд; начало — ось O на задней кромке
    p = Part("Кожух", "УКП.04.001", ("АБС-пластик", 1.05), "#b03a2e")
    p.box(CV_X0, CV_X1, CV_Y0, CV_Y1, 0, CV_Z)
    p.cut(lambda s: s.rect(CV_X0 + CV_T, CV_Y0 + CV_T, CV_X1 - CV_T, CV_Y1 - CV_T), 0, CV_Z - CV_T)   # полость
    p.cut(lambda s: s.poly_fixed(cover_slot()), 0, -13.5 - Z_ST + CV_GAP)       # паз под кулису: до передней грани полосы (z = −13,5) + 1 мм
    p.cut(lambda s: s.rect(E - 6, CV_Y0 - 1, E + 6, CV_Y0 + CV_T + 1), 0, -Z_ST + 6)   # паз под шток Ø8 в дне
    mass["cover"] = p.save(FILES["cover"])[1]
    # бутылка: полая, стекло; не часть изделия, ставится на основание по оси ползуна
    p = Part("Бутылка", "УКП.05.001", GLASS, "#8a4b16", opacity=0.6)
    p.revolve(p.sketch(0, lambda s: (s.contour(bottle_contour()), s.axis(0, -10, 0, BOTTLE_H + 10))))
    mass["bottle"] = p.save(FILES["bottle"])[1]
    json.dump(mass, open(os.path.join(HERE, "parts_mass.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    build()
