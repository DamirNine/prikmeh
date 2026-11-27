# -*- coding: utf-8 -*-
"""27.11 (пользователь): головка ползуна — на резьбе вместо клея, шток с резьбой должен проходить в отверстие Ø8,6 полки
направляющей. Только под печать, расчёты не меняются.
  Верх ползуна: хвостовик y = HEAD_TOP − SPIGOT … HEAD_TOP обточен до Ø7,8 и нарезан Ø8,3 × 2 витками (впадина Ø6,44);
    шток выше (Ø8) не тронут.
  Головка: гнездо Ø8,4 под клей заполнено, вместо него отверстие Ø6,9 с витками Ø8,3 × 2 (впадина Ø8,2): зазор по
    профилю ~0,2 мм на сторону — под печать.
Операции — в конец дерева готовых деталей (print_split.py), файлы до правки — в 2026-11-27/Ползун на резьбе/до правки.
    python polzun_thread.py"""
import json, os, sys
from math import radians, tan
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A5, A7, C, C3, FILES, PARTS_DIR, Part, app, k5, qi, xz_plane
from print_split_consts import HEAD_TOP, SPIGOT, HEAD_FILE

P = 2.0                                            # шаг 2 мм — крупный виток под FDM-печать (пользователь: «максимально большая резьба»)
R_MAJ, R_ROOT = 4.15, 3.15                         # хвостовик: наружный Ø8,3 — наибольший, проходящий в Ø8,6 полки; вершина впадины Ø6,3
R_BORE, R_IROOT = 3.6, 5.18                        # головка: отверстие Ø7,2, вершина впадины на H = 0,866·P + 0,3 от вершины
                                                   # впадины штока (3,15 + 1,73 + 0,3) — иначе профили пересекаются
Y0, Y1 = HEAD_TOP - SPIGOT, HEAD_TOP               # хвостовик −92,5 … −82,5


def doc(path):
    for i in range(app.Documents.Count):
        x = app.Documents.Item(i)
        if x is not None and os.path.normcase(qi(x, A7.IKompasDocument).PathName) == os.path.normcase(path):
            qi(x, A7.IKompasDocument).Close(0); break
    d = app.Documents.Open(path, True, False); d.Active = True
    d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
    return d, d5, qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart


class Live(Part):
    def __init__(self, d5):
        self.doc, self.p, self.first, self.sketches = d5, d5.GetPart(C3.pTop_Part), False, []

    def ext_y(self, y_lo, y_hi, draw, cut):
        """тело/вырез вдоль y между y_lo и y_hi: эскиз на XOZ, смещённой к y_lo (u = x, v = −z), выдавливание к +y"""
        if cut:                                    # у выреза «прямое» направление от смещённой XOZ обратное — режем в обе стороны от середины
            sk = self.sketch(0, draw, xz_plane(self, (y_lo + y_hi) / 2))
            ex = self.p.NewEntity(C3.o3d_cutExtrusion); ed = ex.GetDefinition(); ed.directionType = C3.dtBoth
            ed.SetSideParam(True, C3.etBlind, (y_hi - y_lo) / 2, 0, False); ed.SetSideParam(False, C3.etBlind, (y_hi - y_lo) / 2, 0, False)
            ed.SetSketch(sk); assert ex.Create(), ("вырез", y_lo, y_hi); return
        sk = self.sketch(0, draw, xz_plane(self, y_lo))
        ex = self.p.NewEntity(C3.o3d_bossExtrusion)
        ed = ex.GetDefinition(); ed.directionType = C3.dtNormal
        ed.SetSideParam(True, C3.etBlind, y_hi - y_lo, 0, False); ed.SetSketch(sk)
        assert ex.Create(), ("выдавливание", y_lo, y_hi)

    def helix_y(self, y_lo, y_hi, r):
        """винтовая линия по оси y от y_lo вверх до y_hi, правая, начало — в направлении +x"""
        sp = self.p.NewEntity(C3.o3d_cylindricSpiral); sd = sp.GetDefinition()
        sd.SetPlane(xz_plane(self, y_lo)); sd.SetLocation(0.0, 0.0); sd.buildMode = 0
        sd.diam, sd.step, sd.height, sd.turn = 2 * r, P, y_hi - y_lo, (y_hi - y_lo) / P
        sd.buildDir, sd.turnDir, sd.firstAngle = True, True, 0.0
        assert sp.Create(), "винтовая линия"
        sp.hidden = True; sp.Update()
        return sp

    def thread(self, sp, tri_xy):
        """вырез треугольного профиля (x, y) из плоскости XOY по винтовой линии"""
        sk = self.sketch(0, lambda s: s.poly_fixed(tri_xy))
        ce = self.p.NewEntity(C3.o3d_cutEvolution); cd = ce.GetDefinition()
        cd.sketchShiftType = 1; cd.SetSketch(sk); cd.PathPartArray().Add(sp)
        assert ce.Create(), "резьба не вырезана"

    def done(self, top):
        for sk in self.sketches: sk.hidden = True; sk.Update()
        self.p.Update()
        bad = [f.Name for f in (qi(x, A7.IFeature7) for x in qi(top, A7.IFeature7).SubFeatures(1, False, False)) if not f.Valid and not f.Excluded]
        assert not bad, bad


inside = lambda top, x, y, z: top.IsPointInside(x, y, z) if hasattr(top, "IsPointInside") else None
faces = lambda top, x, y, z: [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ()))
                              if o.ModelObjectType == C3.o3d_face]
mass = lambda top: qi(top, A7.IMassInertiaParam7).Mass
out = {}

# ---------------------------------------------------------------- верх ползуна: наружная резьба на хвостовике
ONLY = sys.argv[1:]
if not ONLY or "polzun" in ONLY:
    path = os.path.join(PARTS_DIR, FILES["polzun"])
    d, d5, top = doc(path); lp = Live(d5); m0 = mass(top)
    lp.ext_y(Y0, Y1, lambda s: s.circle(0, 0, R_MAJ), cut=False)        # хвостовик Ø8 → Ø8,3 (шток выше — Ø8)
    yh0 = Y0 - 2 * P                                                                               # линия — от ниже торца
    sp = lp.helix_y(yh0, Y1 - 0.5, R_MAJ)
    hw = (R_MAJ + 0.3 - R_ROOT) * tan(radians(30))
    lp.thread(sp, [(R_ROOT, yh0), (R_MAJ + 0.3, yh0 - hw), (R_MAJ + 0.3, yh0 + hw)])
    lp.done(top)
    g = [round(v, 2) for v in d5.GetPart(C3.pTop_Part).GetGabarit(True, True)[1:]]
    # проверка: на хвостовике чередуются металл и впадина, шток выше не тронут
    probe = [(y, bool(faces(top, R_MAJ, y, 0.0)) or bool(faces(top, 0.0, y, R_MAJ))) for y in [Y0 + 0.5 + k * P / 4 for k in range(8)]]
    assert faces(top, 4.0, Y1 + 2.0, 0.0) or faces(top, 0.0, Y1 + 2.0, 4.0), "шток Ø8 выше хвостовика испорчен"
    assert max(abs(g[0]), abs(g[3])) == 12.0 and g[1] >= Y0 - 0.01, g
    out["polzun"] = mass(top)
    print(f"ползун: хвостовик Ø8,3 × 2 (Ø{2 * R_MAJ:g}), y {Y0:g}…{Y1:g}; масса {m0:.1f} → {out['polzun']:.1f} г; габарит {g}; витки: {probe}")
    d5.SaveAs(path); d.Close(0)

# ---------------------------------------------------------------- головка: внутренняя резьба вместо гнезда под клей
path = os.path.join(PARTS_DIR, HEAD_FILE)
d, d5, top = doc(path); lp = Live(d5); m0 = mass(top)
lp.ext_y(Y0 - 0.2, Y1, lambda s: s.circle(0, 0, 4.3), cut=False)                               # заполнить гнездо Ø8,4
lp.ext_y(Y0 - 3.0, Y1 + 1.0, lambda s: s.circle(0, 0, R_BORE), cut=True)                         # отверстие Ø7,2
yh0 = Y0 - P / 2                            # впадина головки — против витка штока (полшага); начинается выше дна отверстия
                                            # (−95,5; металл по оси головки — до −102,5): иначе её кромка ложится на дно и STL выходит незамкнутым
sp = lp.helix_y(yh0, Y1 + P, R_IROOT)
hw = (R_IROOT - (R_BORE - 0.2)) * tan(radians(30))
lp.thread(sp, [(R_IROOT, yh0), (R_BORE - 0.2, yh0 - hw), (R_BORE - 0.2, yh0 + hw)])
lp.ext_y(Y1 - 2.0, Y1 + 1.0, lambda s: s.circle(0, 0, 4.3), cut=True)    # проточка Ø8,6 × 2 у торца: там виток штока сбегает на полный Ø8,3
lp.done(top)
g = [round(v, 2) for v in d5.GetPart(C3.pTop_Part).GetGabarit(True, True)[1:]]
assert g[4] == HEAD_TOP and g[0] == -20.0, g
out["head"] = mass(top)
probe = [(y, bool(faces(top, R_IROOT - 0.05, y, 0.0)) or bool(faces(top, 0.0, y, R_IROOT - 0.05))) for y in [Y0 + 0.5 + k * P / 4 for k in range(8)]]
print(f"головка: отверстие Ø{2 * R_BORE:g} с витками Ø8,3 × 2, глубина {Y1 - Y0 + 0.5:g}; масса {m0:.1f} → {out['head']:.1f} г; витки: {probe}")
d5.SaveAs(path); d.Close(0)

mj = "parts_mass.json"
m = json.load(open(mj, encoding="utf-8")); m.update(out)
json.dump(m, open(mj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
