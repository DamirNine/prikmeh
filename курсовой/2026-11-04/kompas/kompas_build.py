# -*- coding: utf-8 -*-
"""Модели звеньев и сборка укупоривателя в КОМПАС-3D v25 (Учебная) через API (COM): детали .m3d и сборка .a3d.

Система координат сборки: начало — ось O кулисы, x — вправо (к оси ползуна), y — вверх, z — к наблюдателю (ползун в
плоскости z = 0, как в 3D-модели v22). Неподвижные детали (основание, стойка, ось O, направляющая, упоры) построены сразу
в координатах сборки и закреплены. Подвижные: кулиса со ступицей и ручка — в системе «O, x вдоль кулисы»; камень с
пальцем D и ползун — в системе «D». Сопряжения: кулиса — совпадение плоскостей XY, соосность с осью Z, угол с осью x в
диапазоне φк…φн (22,72…59,47°); камень — плоскость XY, плоскость XZ совпадает с XZ кулисы (скользит вдоль неё);
ползун — плоскость XY, плоскость YZ на расстоянии e от YZ сборки (ходит по вертикали); палец D соосен отверстию ползуна.
Нижний и верхний упоры касаются рёбер кулисы в положениях φк и φн."""
import json, os, subprocess, time
from math import radians, tan, cos, sin
import pythoncom
from win32com.client import GetActiveObject, gencache

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = r"C:\Program Files\ASCON\KOMPAS-3D v25 Study\Bin"
RJ = json.load(open(os.path.join(HERE, "..", "calc_v21.json"), encoding="utf-8"))
E = 12.53
PH_N, PH_K, PH_Y = RJ["phi_n"], RJ["phi_k"], RJ["phi_y"]
PH0 = PH_Y                                        # начальное положение сборки — начало пластической деформации
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
    except pythoncom.com_error:
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
        """выдавливание по +z на depth; cut — вырез; both — вырез насквозь в обе стороны"""
        kind = C3.o3d_cutExtrusion if cut else (C3.o3d_baseExtrusion if self.first else C3.o3d_bossExtrusion)
        ex = self.p.NewEntity(kind)
        d = ex.GetDefinition()
        if both:
            d.directionType = C3.dtBoth
            d.SetSideParam(True, C3.etThroughAll, 0, 0, False)
            d.SetSideParam(False, C3.etThroughAll, 0, 0, False)
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

    # --- примитивы в координатах детали
    def poly(self, pts, z0, z1, cut=False):
        def draw(d2):
            for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
                d2.ksLineSeg(x1, y1, x2, y2, 1)
        self.extrude(self.sketch(z0, draw), z1 - z0, cut)

    def box(self, x0, x1, y0, y1, z0, z1, cut=False):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, cut)

    def cyl(self, xc, yc, r, z0, z1, r_in=None, cut=False):
        def draw(d2):
            d2.ksCircle(xc, yc, r, 1)
            if r_in:
                d2.ksCircle(xc, yc, r_in, 1)
        self.extrude(self.sketch(z0, draw), z1 - z0, cut)

    def hole(self, xc, yc, r):
        self.extrude(self.sketch(0, lambda d2: d2.ksCircle(xc, yc, r, 1)), 0, cut=True, both=True)

    def save(self, fname):
        self.p.SetAdvancedColor(rgb(self.color), 0.5, 0.6, 0.6, 0.6, 0.0, 0.0)
        self.p.Update()
        path = os.path.join(HERE, fname)
        d7 = qi(app.ActiveDocument, A7.IKompasDocument3D)
        g = d7.TopPart.GetGabarit(True, False)
        ok = self.doc.SaveAs(path)
        mass = None
        try:
            mi = self.p.CalcMassInertiaProperties(C3.ST_MIX_KG | C3.ST_MIX_MM)
            mass = mi.m
        except Exception:
            pass
        self.doc.close()
        print(f"  {fname}: сохранено {ok}, габарит {[round(v, 2) for v in g[1:]]}" + (f", масса {mass:.4f} кг" if mass else ""))
        return path, [round(v, 2) for v in g[1:]], mass


ST3, ST45 = ("Ст3сп ГОСТ 380-2005", 7.85), ("Сталь 45 ГОСТ 1050-2013", 7.85)
FILES, GAB, MASS = {}, {}, {}


def done(key, part, fname):
    FILES[key], GAB[key], MASS[key] = part.save(fname)


print("Детали:")
# ---------------- неподвижные детали — в координатах сборки
Z_ST0, Z_ST1 = -46.0, -34.0                         # стойка: лист 12 мм позади кулисы
X_ST0, X_ST1, Y_ST0, Y_ST1 = -49.47, 42.53, -325.25, 62.0
p = Part("Основание", "УКП.00.001", ST3, "#6f7884")
p.box(-67.47, 132.53, -345.25, Y_ST0, -56.0, 104.0)
done("base", p, "УКП.00.001 Основание.m3d")

p = Part("Стойка", "УКП.00.002", ST3, "#8a94a3")
p.box(X_ST0, X_ST1, Y_ST0, Y_ST1, Z_ST0, Z_ST1)
p.hole(0, 0, 5.0)
done("stand", p, "УКП.00.002 Стойка.m3d")

p = Part("Ось O", "УКП.00.003", ST45, "#b8c0c9")
p.cyl(0, 0, 5.0, Z_ST0, -13.5)
done("axle", p, "УКП.00.003 Ось O.m3d")

y_top, y_bot = yD(PH_N) + 20 + 6, yD(PH_K) - 20 - 35   # направляющая: на 6 мм выше и 35 мм ниже хода ползуна
p = Part("Направляющая", "УКП.00.004", ST3, "#8a94a3")
for xa, xb in ((E - 18.5, E - 12.5), (E + 12.5, E + 18.5)):
    p.box(xa, xb, y_bot, y_top, -8.0, 8.0)                    # планка у боковой грани ползуна, зазор 0,5 мм
    p.box(xa, xb, y_bot, y_bot + 12, Z_ST1, -8.0)            # кронштейн к стойке
done("guide", p, "УКП.00.004 Направляющая.m3d")


def edge(ph, r, side):
    """точка на ребре кулисы в положении ph: r — от оси O вдоль кулисы, side = −1 нижнее ребро, +1 верхнее"""
    c, s = cos(radians(ph)), sin(radians(ph))
    return (r * c - side * 9 * s, r * s + side * 9 * c)


a, b = edge(PH_K, 30, -1), edge(PH_K, 42, -1)                # нижний упор: грань по нижнему ребру кулисы при φк
p = Part("Упор нижний", "УКП.00.005", ST3, "#c43b3b")
p.poly([a, b, (b[0], -5.0), (a[0], -5.0)], Z_ST1, -13.5)
done("stop_lo", p, "УКП.00.005 Упор нижний.m3d")

a, b = edge(PH_N, 45, 1), edge(PH_N, 57, 1)                  # верхний упор: грань по верхнему ребру кулисы при φн
n = (-sin(radians(PH_N)), cos(radians(PH_N)))
p = Part("Упор верхний", "УКП.00.006", ST3, "#c43b3b")
p.poly([a, b, (b[0] + 8 * n[0], b[1] + 8 * n[1]), (a[0] + 8 * n[0], a[1] + 8 * n[1])], Z_ST1, -13.5)
done("stop_hi", p, "УКП.00.006 Упор верхний.m3d")

# ---------------- кулиса со ступицей: начало — ось O, x вдоль кулисы
L, H, R_ = 500.0, 18.0, 9.0
p = Part("Кулиса", "УКП.01.001", ST3, "#2d3540")


def strip(d2):
    d2.ksLineSeg(0, -R_, L - R_, -R_, 1)
    d2.ksArcByPoint(L - R_, 0, R_, L - R_, -R_, L - R_, R_, 1, 1)
    d2.ksLineSeg(L - R_, R_, 0, R_, 1)
    d2.ksArcByPoint(0, 0, R_, 0, R_, 0, -R_, 1, 1)


p.extrude(p.sketch(-21.5, strip), 8.0)                        # полоса 8 × 18, z −21,5…−13,5
p.cyl(0, 0, 8.0, -33.5, -21.5, r_in=5.0)                      # ступица Ø16 × 12 (приварена к полосе)
p.hole(0, 0, 5.0)                                             # отверстие под ось O Ø10
done("kulisa", p, "УКП.01.001 Кулиса.m3d")

p = Part("Ручка", "УКП.01.002", ("Резина", 1.2), "#15191f")


def grip(d2):
    for (x1, y1), (x2, y2) in (((402.5, 0), (497.5, 0)), ((497.5, 0), (497.5, 13)), ((497.5, 13), (402.5, 13)),
                               ((402.5, 13), (402.5, 0))):
        d2.ksLineSeg(x1, y1, x2, y2, 1)
    d2.ksLineSeg(390, 0, 510, 0, 3)                           # ось вращения


p.revolve(p.sketch(-17.5, grip))
p.box(402.5, 497.5, -9.0, 9.0, -21.5, -13.5, cut=True)        # прямоугольное отверстие под полосу
done("grip", p, "УКП.01.002 Ручка.m3d")

# ---------------- камень-обойма с пальцем D: начало — ось пальца D, x вдоль кулисы
p = Part("Камень с пальцем D", "УКП.02.001", ST45, "#e8c99a")
p.box(-10, 10, 9.5, 13.5, -24.5, -9.0)                        # верхняя стенка
p.box(-10, 10, -13.5, -9.5, -24.5, -9.0)                      # нижняя стенка
p.box(-10, 10, -9.5, 9.5, -13.0, -9.0)                        # передняя стенка
p.box(-7, 10, 6.8, 9.5, -24.5, -22.0)                         # губки за рёбрами полосы (у оси O укорочены на 3 мм)
p.box(-7, 10, -9.5, -6.8, -24.5, -22.0)
p.cyl(0, 0, 5.0, -9.0, 8.0)                                   # палец D Ø10 — сквозь ползун
done("kamen", p, "УКП.02.001 Камень с пальцем D.m3d")

# ---------------- ползун: начало — ось пальца D
p = Part("Ползун", "УКП.03.001", ST3, "#3a4049")
p.box(-12, 12, -20, 20, -8.0, 8.0)                            # направляемая часть 24 × 40 × 16


def rod(d2):
    pts = [(0, -20), (4, -20), (4, -80), (20, -80), (20, -104), (0, -104)]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        d2.ksLineSeg(x1, y1, x2, y2, 1)
    d2.ksLineSeg(0, 0, 0, -110, 3)


p.revolve(p.sketch(0, rod))                                   # шток Ø8 × 60 и головка Ø40 × 24
p.hole(0, 0, 5.0)                                             # отверстие под палец D
done("polzun", p, "УКП.03.001 Ползун.m3d")

json.dump(dict(gab=GAB, mass=MASS), open(os.path.join(HERE, "parts_check.json"), "w", encoding="utf-8"), ensure_ascii=False,
          indent=1)
print("детали готовы")
