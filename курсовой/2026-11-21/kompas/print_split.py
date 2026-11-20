# -*- coding: utf-8 -*-
"""21.11 (замечание на защите прототипа, только под печать — расчёты не меняются): направляющая = «стул».
  Направляющая — внизу между планками полка 6 мм (y = Y_BOT…Y_BOT + 6) с отверстием Ø8,6 под шток ползуна (зазор 0,3 на
    сторону, как в остальных подвижных посадках печатных деталей): шток на всём ходе идёт в отверстии полки.
  Ползун — разрезан на верх (брусок + шток) и головку. У верха снято всё шире штока ниже Y_CUT (скругление R3 «шток —
    головка» начинается с y = −78), шток продолжается хвостовиком Ø8 до HEAD_TOP − SPIGOT; у головки срезано всё выше её
    верхнего торца HEAD_TOP (со скруглением R3 — иначе вокруг гнезда осталась бы острая кромка) и сделано гнездо Ø8,4
    (по 0,2 мм на клей) глубиной SPIGOT + 0,2.
    Головку приклеивают снизу, когда шток уже пропущен через полку.
Детали НЕ перестраиваются: операции добавляются в конец дерева уже готовых документов (линии разъёма APM и всё, что
пользователь задавал в направляющей, сохраняются). Головка — копия файла ползуна с вырезами.
    python print_split.py"""
import json, os, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import (A5, A7, C, C3, E, FILES, GD_X0, GD_X1, GD_Z1, PARTS_DIR, Part, Y_BOT, app, k5, qi, xz_plane)

SHELF_T, SHELF_HOLE_R = 6.0, 4.3                  # полка 6 мм, отверстие Ø8,6
Z_AXIS = 34.0                                     # ось ползуна в координатах направляющей (= стойки): 34 мм перед листом
Y_CUT, HEAD_TOP = -77.5, -82.5                   # у верха — всё шире штока ниже Y_CUT; верхний торец головки (координаты ползуна):
                                                  # «колокол» начинается конусом почти от штока — при торце на −81 стенка вокруг
                                                  # гнезда Ø8,4 была 0,74 мм, на −82,5 — 2,15 мм
SPIGOT, SOCKET_R = 10.0, 4.2                      # хвостовик в головке, гнездо Ø8,4
HEAD_FILE = "УКП.03.002 Головка ползуна.m3d"


def doc(path):
    for i in range(app.Documents.Count):
        x = app.Documents.Item(i)
        if x is not None and os.path.normcase(qi(x, A7.IKompasDocument).PathName) == os.path.normcase(path):
            qi(x, A7.IKompasDocument).Close(0)    # открытая копия могла остаться с несохранёнными правками — берём файл с диска
            break
    d = app.Documents.Open(path, True, False)
    d.Active = True
    d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
    top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
    return d5, d5.GetPart(C3.pTop_Part), top


class Live(Part):
    """операции Part в уже открытом документе"""
    def __init__(self, d5):
        self.doc, self.p, self.first, self.sketches = d5, d5.GetPart(C3.pTop_Part), False, []

    def cut_y(self, y_lo, y_hi, draw):
        """вырез вдоль y между плоскостями y_lo и y_hi: эскиз (u, v) = (x, −z) в средней плоскости, выдавливание в обе
        стороны (у выреза «прямое» направление от смещённой XOZ — к −y, у бобышки — к +y: в обе стороны надёжнее)"""
        self.extrude(self.sketch(0, draw, xz_plane(self, (y_lo + y_hi) / 2)), (y_hi - y_lo) / 2, cut=True, both=True)

    def hide_sketches(self):
        for sk in self.sketches:
            sk.hidden = True
            sk.Update()


def check(top):
    bad = [f.Name for f in (qi(x, A7.IFeature7) for x in qi(top, A7.IFeature7).SubFeatures(1, False, False)) if not f.Valid and not f.Excluded]
    assert not bad, bad


mass = lambda top: qi(top, A7.IMassInertiaParam7).Mass
gab = lambda p5: [round(v, 2) for v in p5.GetGabarit(True, True)[1:]]
faces = lambda top, x, y, z: [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ()))
                              if o.ModelObjectType == C3.o3d_face]
masses = {}

# ---------------------------------------------------------------- направляющая: полка с отверстием
path = os.path.join(PARTS_DIR, FILES["guide"])
d5, p5, top = doc(path)
m0 = mass(top)
sls = qi(top, A7.IAuxiliaryGeomContainer).SplitLines
names = [sls.Item(i).Name for i in range(sls.Count)]
lp = Live(d5)
x0, x1 = GD_X0 + 1.0, GD_X1 - 1.0                 # внутри наружных кромок планок — полка сливается с ними и с пластиной
lp.prism_xz([(x0, 0.0), (x1, 0.0), (x1, GD_Z1), (x0, GD_Z1)], Y_BOT, Y_BOT + SHELF_T)
lp.cut_y(Y_BOT - 1.0, Y_BOT + SHELF_T + 1.0, lambda s: s.circle(E, -Z_AXIS, SHELF_HOLE_R))
lp.hide_sketches()
p5.Update()
check(top)
assert [sls.Item(i).Name for i in range(sls.Count)] == names and all(sls.Item(i).Valid for i in range(sls.Count)), "линии разъёма"
assert faces(top, E + SHELF_HOLE_R, Y_BOT + SHELF_T / 2, Z_AXIS), "нет стенки отверстия в полке"
assert faces(top, E + 8.0, Y_BOT + SHELF_T, Z_AXIS), "нет верхней грани полки"
assert gab(p5) == [round(GD_X0, 2), round(Y_BOT, 2), -6.0, round(GD_X1, 2), 47.25, 55.0], gab(p5)
masses["guide"] = mass(top)
print(f"направляющая: полка {SHELF_T:g} мм с отверстием Ø{2 * SHELF_HOLE_R:g}; линии разъёма целы ({len(names)}); "
      f"масса {m0:.1f} → {masses['guide']:.1f} г")
d5.SaveAs(path)

# ---------------------------------------------------------------- ползун → верх + головка
path = os.path.join(PARTS_DIR, FILES["polzun"])
head_path = os.path.join(PARTS_DIR, HEAD_FILE)
for i in range(app.Documents.Count):              # копия файла — только с закрытым ползуном
    x = app.Documents.Item(i)
    if x is not None and os.path.normcase(qi(x, A7.IKompasDocument).PathName) == os.path.normcase(path):
        qi(x, A7.IKompasDocument).Close(0)
        break
shutil.copyfile(path, head_path)

d5, p5, top = doc(path)
m0 = mass(top)
lp = Live(d5)
# всё ниже разреза, кроме стержня r = 4 (хвостовик), затем стержень ниже хвостовика
lp.cut_y(Y_CUT - 60.0, Y_CUT, lambda s: (s.circle(0, 0, 30.0), s.circle(0, 0, 4.0)))
lp.cut_y(HEAD_TOP - SPIGOT - 60.0, HEAD_TOP - SPIGOT, lambda s: s.circle(0, 0, 10.0))
lp.hide_sketches()
p5.Update()
check(top)
g = gab(p5)
assert g[1] == round(HEAD_TOP - SPIGOT, 2) and g[4] == 20.0 and g[0] == -12.0, g
masses["polzun"] = mass(top)
print(f"ползун (верх): брусок + шток с хвостовиком Ø8 до y = {HEAD_TOP - SPIGOT:g}; габарит {g}; масса {m0:.1f} → {masses['polzun']:.1f} г")
d5.SaveAs(path)

d5, p5, top = doc(head_path)
lp = Live(d5)
lp.p.name, lp.p.marking = "Головка ползуна", "УКП.03.002"
lp.p.Update()
lp.cut_y(HEAD_TOP, HEAD_TOP + 120.0, lambda s: s.circle(0, 0, 30.0))              # всё выше верхнего торца головки
lp.cut_y(HEAD_TOP - SPIGOT - 0.2, HEAD_TOP + 1.0, lambda s: s.circle(0, 0, SOCKET_R))   # гнездо под хвостовик
lp.hide_sketches()
p5.Update()
check(top)
g = gab(p5)
assert g[4] == HEAD_TOP and g[0] == -20.0, g
assert faces(top, SOCKET_R, HEAD_TOP - SPIGOT / 2, 0.0) or faces(top, 0.0, HEAD_TOP - SPIGOT / 2, SOCKET_R), "нет гнезда"
masses["head"] = mass(top)
print(f"головка: от y = {HEAD_TOP:g} вниз, гнездо Ø{2 * SOCKET_R:g} × {SPIGOT + 0.2:g}; габарит {g}; масса {masses['head']:.1f} г")
d5.SaveAs(head_path)

mj = "parts_mass.json"
m = json.load(open(mj, encoding="utf-8"))
m.update(masses)
json.dump(m, open(mj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("массы записаны:", {k: round(v, 1) for k, v in masses.items()})
