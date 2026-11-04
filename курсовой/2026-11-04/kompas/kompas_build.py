# -*- coding: utf-8 -*-
"""Детали укупоривателя в КОМПАС-3D v25 (Учебная) через API (COM) — каждая деталь отдельно, в своей системе координат
от своей базы; файлы — в папке «Детали». Сборка — kompas_assembly.py (детали соединяются сопряжениями).

Базы деталей (ось z всех деталей при сборке направлена к наблюдателю, ползун — в плоскости z = 0 сборки):
  Основание — центр верхней грани; Стойка — ось отверстия O на передней грани; Ось O — центр заднего торца;
  Направляющая — ось ползуна на нижней кромке кронштейнов, задняя грань кронштейнов z = 0; упоры — угол на задней грани;
  Кулиса — ось отверстия O на задней грани полосы, x — вдоль кулисы; Ручка — начало ручки на её оси;
  Камень с пальцем D — ось пальца на передней грани обоймы; Ползун — ось отверстия под палец в средней плоскости."""
import json, os, subprocess, time
from math import radians, tan, cos, sin
import pythoncom
from win32com.client import GetActiveObject, gencache

HERE = os.path.dirname(os.path.abspath(__file__))
PARTS_DIR = os.path.join(HERE, "Детали")
BIN = r"C:\Program Files\ASCON\KOMPAS-3D v25 Study\Bin"
RJ = json.load(open(os.path.join(HERE, "..", "calc_v21.json"), encoding="utf-8"))
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
X_ST0, X_ST1 = -49.5, 42.5                        # кромки стойки от оси O
Y_ST0 = -325.25                                   # низ стойки (верх основания) от оси O: высота оси над основанием
Z_ST = -34.0                                      # передняя грань стойки в сборке
Y_BOT, Y_TOP = yD(PH_K) - 55, yD(PH_N) + 26       # направляющая: на 35 мм ниже и на 6 мм выше хода ползуна


def lower_edge_y(ph, x):
    """y нижнего ребра кулисы (полоса 18 мм) при угле ph над точкой x"""
    return (x * sin(radians(ph)) - 9) / cos(radians(ph))


def upper_edge_y(ph, x):
    return (x * sin(radians(ph)) + 9) / cos(radians(ph))


LO_X0, LO_X1, LO_Y0 = 31.0, 42.0, -5.0            # нижний упор: x 31…42, низ на 5 мм ниже оси O
HI_X0, HI_X1, HI_Y1 = 15.0, 21.0, 60.0            # верхний упор: x 15…21, верх на 60 мм выше оси O


# ================================================================ построение детали (API5)
class Part:
    def __init__(self, name, marking, material, color):
        self.doc = k5.Document3D()
        self.doc.Create(False, True)
        self.p = self.doc.GetPart(C3.pTop_Part)
        self.p.name, self.p.marking = name, marking
        self.p.SetMaterial(*material)
        self.color = color
        self.first = True

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
        d2 = d.BeginEdit()
        draw(d2)
        d.EndEdit()
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

    def poly(self, pts, z0, z1, cut=False):
        def draw(d2):
            for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
                d2.ksLineSeg(x1, y1, x2, y2, 1)
        self.extrude(self.sketch(z0, draw), z1 - z0, cut)

    def box(self, x0, x1, y0, y1, z0, z1, cut=False):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, cut)

    def cyl(self, xc, yc, r, z0, z1, r_in=None):
        def draw(d2):
            d2.ksCircle(xc, yc, r, 1)
            if r_in:
                d2.ksCircle(xc, yc, r_in, 1)
        self.extrude(self.sketch(z0, draw), z1 - z0)

    def hole(self, xc, yc, r):
        self.extrude(self.sketch(0, lambda d2: d2.ksCircle(xc, yc, r, 1)), 0, cut=True, both=True)

    def save(self, fname):
        self.p.SetAdvancedColor(rgb(self.color), 0.5, 0.6, 0.8, 0.8, 1.0, 0.5)   # transparency = 1 — непрозрачная
        for t in (C3.o3d_planeXOY, C3.o3d_planeXOZ, C3.o3d_planeYOZ):  # системные плоскости не показывать в сборке
            pl = self.p.GetDefaultEntity(t)
            pl.hidden = True
            pl.Update()
        self.p.Update()
        path = os.path.join(PARTS_DIR, fname)
        self.doc.SaveAs(path)
        mi = qi(qi(app.ActiveDocument, A7.IKompasDocument3D).TopPart, A7.IMassInertiaParam7)
        mass = mi.Mass
        self.doc.close()
        print(f"  {fname}: масса {mass:.1f} г")
        return path, mass


ST3, ST45 = ("Ст3сп ГОСТ 380-2005", 7.85), ("Сталь 45 ГОСТ 1050-2013", 7.85)
FILES = {
    "base": "УКП.00.001 Основание.m3d", "stand": "УКП.00.002 Стойка.m3d", "axle": "УКП.00.003 Ось O.m3d",
    "guide": "УКП.00.004 Направляющая.m3d", "stop_lo": "УКП.00.005 Упор нижний.m3d", "stop_hi": "УКП.00.006 Упор верхний.m3d",
    "kulisa": "УКП.01.001 Кулиса.m3d", "grip": "УКП.01.002 Ручка.m3d", "kamen": "УКП.02.001 Камень с пальцем D.m3d",
    "polzun": "УКП.03.001 Ползун.m3d"}


def build():
    os.makedirs(PARTS_DIR, exist_ok=True)
    mass = {}
    print("Детали:")
    p = Part("Основание", "УКП.00.001", ST3, "#6f7884")             # плита 200 × 160 × 20, начало — центр верхней грани
    p.box(-100, 100, -20, 0, -80, 80)
    mass["base"] = p.save(FILES["base"])[1]

    p = Part("Стойка", "УКП.00.002", ST3, "#8a94a3")                 # лист 92 × 390 × 12, начало — ось O на передней грани
    p.box(X_ST0, X_ST1, Y_ST0, Y_ST0 + H_ST, -B_ST, 0)
    p.hole(0, 0, 5.0)
    mass["stand"] = p.save(FILES["stand"])[1]

    p = Part("Ось O", "УКП.00.003", ST45, "#b8c0c9")                 # Ø10 × 32,5, начало — центр заднего торца
    p.cyl(0, 0, 5.0, 0, 32.5)
    mass["axle"] = p.save(FILES["axle"])[1]

    p = Part("Направляющая", "УКП.00.004", ST3, "#8a94a3")          # планки 6 × 97 × 16 у боковых граней ползуна + кронштейны
    for xa, xb in ((-18.5, -12.5), (12.5, 18.5)):
        p.box(xa, xb, 0, Y_TOP - Y_BOT, 26.0, 42.0)
        p.box(xa, xb, 0, 12.0, 0, 26.0)
    mass["guide"] = p.save(FILES["guide"])[1]

    # нижний упор: верхняя грань — по нижнему ребру кулисы в положении φк; начало — нижний левый угол задней грани
    p = Part("Упор нижний", "УКП.00.005", ST3, "#c43b3b")
    ya, yb = lower_edge_y(PH_K, LO_X0) - LO_Y0, lower_edge_y(PH_K, LO_X1) - LO_Y0
    p.poly([(0, 0), (LO_X1 - LO_X0, 0), (LO_X1 - LO_X0, yb), (0, ya)], 0, 20.5)
    mass["stop_lo"] = p.save(FILES["stop_lo"])[1]

    # верхний упор: нижняя грань — по верхнему ребру кулисы в положении φн; начало — верхний левый угол задней грани
    p = Part("Упор верхний", "УКП.00.006", ST3, "#c43b3b")
    ya, yb = upper_edge_y(PH_N, HI_X0) - HI_Y1, upper_edge_y(PH_N, HI_X1) - HI_Y1
    p.poly([(0, ya), (HI_X1 - HI_X0, yb), (HI_X1 - HI_X0, 0), (0, 0)], 0, 20.5)
    mass["stop_hi"] = p.save(FILES["stop_hi"])[1]

    L, R_ = 500.0, 9.0                                                # кулиса: полоса 8 × 18 × 500 + ступица Ø16 × 12

    def strip(d2):
        d2.ksLineSeg(0, -R_, L - R_, -R_, 1)
        d2.ksArcByPoint(L - R_, 0, R_, L - R_, -R_, L - R_, R_, 1, 1)
        d2.ksLineSeg(L - R_, R_, 0, R_, 1)
        d2.ksArcByPoint(0, 0, R_, 0, R_, 0, -R_, 1, 1)
    p = Part("Кулиса", "УКП.01.001", ST3, "#2d3540")
    p.extrude(p.sketch(0, strip), 8.0)
    p.cyl(0, 0, 8.0, -12.0, 0, r_in=5.0)
    p.hole(0, 0, 5.0)
    mass["kulisa"] = p.save(FILES["kulisa"])[1]

    def grip(d2):                                                     # ручка Ø26 × 95 вращением, ось — x
        pts = [(0, 0), (95, 0), (95, 13), (0, 13)]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
            d2.ksLineSeg(x1, y1, x2, y2, 1)
        d2.ksLineSeg(-10, 0, 105, 0, 3)
    p = Part("Ручка", "УКП.01.002", ("Резина", 1.2), "#15191f")
    p.revolve(p.sketch(0, grip))
    slot = [(0, -9.0), (95, -9.0), (95, 9.0), (0, 9.0)]              # отверстие 18 × 8 под полосу: ±4 мм от оси ручки
    p.extrude(p.sketch(0, lambda d2: [d2.ksLineSeg(*a, *b, 1) for a, b in zip(slot, slot[1:] + slot[:1])]), 4.0, cut=True,
              both=True)
    mass["grip"] = p.save(FILES["grip"])[1]

    p = Part("Камень с пальцем D", "УКП.02.001", ST45, "#e8c99a")   # обойма 20 мм, стенки 4, губки, палец Ø10 × 17
    p.box(-10, 10, 9.5, 13.5, -15.5, 0)
    p.box(-10, 10, -13.5, -9.5, -15.5, 0)
    p.box(-10, 10, -9.5, 9.5, -4.0, 0)
    p.box(-7, 10, 6.8, 9.5, -15.5, -13.0)                            # губки за рёбрами полосы, у оси O укорочены на 3 мм
    p.box(-7, 10, -9.5, -6.8, -15.5, -13.0)
    p.cyl(0, 0, 5.0, 0, 17.0)
    mass["kamen"] = p.save(FILES["kamen"])[1]

    def rod(d2):                                                      # шток Ø8 × 60 и головка Ø40 × 24 вращением вокруг y
        pts = [(0, -20), (4, -20), (4, -80), (20, -80), (20, -104), (0, -104)]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
            d2.ksLineSeg(x1, y1, x2, y2, 1)
        d2.ksLineSeg(0, 0, 0, -110, 3)
    p = Part("Ползун", "УКП.03.001", ST3, "#3a4049")
    p.box(-12, 12, -20, 20, -8.0, 8.0)
    p.revolve(p.sketch(0, rod))
    p.hole(0, 0, 5.0)
    mass["polzun"] = p.save(FILES["polzun"])[1]
    json.dump(mass, open(os.path.join(HERE, "parts_mass.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    build()
