# -*- coding: utf-8 -*-
"""16.11 (просьба пользователя): скругления углов выемки стойки R1 → R4, фаски углов пластины направляющей 1 → 2,5 мм
и выше выемки на 2 мм (z −6…0 → −6…+2). Детали НЕ перестраиваются — правятся параметры уже существующих операций
в открытых (или открываемых) документах, чтобы сохранились линии разъёма и всё, что пользователь задал в направляющей:
  стойка — «Скругление» R1 по 4 рёбрам: радиус → POCKET_R;
  направляющая — 4 старых выреза-фаски (z −6…0 из guide_screw.py или уже новые) удаляются, 4 новых (GD_CH, z −6…+GD_CH_Z1)
    добавляются в конец дерева; линии разъёма (сила, закрепление) остаются и проверяются.
    python pocket_r4.py"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import (A5, A7, C, C3, FILES, GD_CH, GD_CH_Z1, GD_PL_T, GD_PL_Y1, GD_X0, GD_X1, PARTS_DIR, POCKET_R,
                          Y_BOT, Part, app, k5, qi)


def doc(key):
    path = os.path.join(PARTS_DIR, FILES[key])
    for i in range(app.Documents.Count):
        x = app.Documents.Item(i)
        if x is not None and os.path.normcase(qi(x, A7.IKompasDocument).PathName) == os.path.normcase(path):
            d = qi(x, A7.IKompasDocument)
            break
    else:
        d = app.Documents.Open(path, True, False)
    d.Active = True
    d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
    top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
    return path, d5, d5.GetPart(C3.pTop_Part), top


def check(top):
    bad = [f.Name for f in (qi(x, A7.IFeature7) for x in qi(top, A7.IFeature7).SubFeatures(1, False, False)) if not f.Valid and not f.Excluded]
    assert not bad, bad


mass = lambda top: qi(top, A7.IMassInertiaParam7).Mass
faces = lambda top, x, y, z: [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ()))
                              if o.ModelObjectType == C3.o3d_face]

# ---------------------------------------------------------------- стойка
path, d5, p5, top = doc("stand")
m0 = mass(top)
col = p5.EntityCollection(C3.o3d_fillet)
fl = [e for e in (col.GetByIndex(j) for j in range(col.GetCount())) if e.GetDefinition().array().GetCount() == 4]
assert len(fl) == 1, "ожидалось одно скругление по 4 рёбрам (углы выемки)"
fd = fl[0].GetDefinition()
if abs(fd.radius - POCKET_R) > 1e-6:
    r0, fd.radius = fd.radius, POCKET_R
    assert fl[0].Update(), "скругление R4 не построено"
    p5.Update()
    check(top)
    print(f"стойка: углы выемки R{r0:g} → R{POCKET_R:g}; масса {m0:.1f} → {mass(top):.1f} г")
    d5.SaveAs(path)
else:
    print(f"стойка: углы выемки уже R{POCKET_R:g}")

# ---------------------------------------------------------------- направляющая
path, d5, p5, top = doc("guide")
m0 = mass(top)
sls = qi(top, A7.IAuxiliaryGeomContainer).SplitLines
names = [sls.Item(i).Name for i in range(sls.Count)]
z_mid, half = (-GD_PL_T + GD_CH_Z1) / 2, (GD_PL_T + GD_CH_Z1) / 2
col = p5.EntityCollection(C3.o3d_cutExtrusion)
old = []
for e in (col.GetByIndex(j) for j in range(col.GetCount())):
    d = e.GetDefinition()
    pl = d.GetSketch().GetDefinition().GetPlane()
    sp = d.ExtrusionParam()
    for off, dep in ((3.0, 3.0), (abs(z_mid), half)):        # фаски z −6…0 (guide_screw.py) или уже z −6…+GD_CH_Z1
        if (pl.type == C3.o3d_planeOffset and abs(pl.GetDefinition().offset - off) < 1e-6 and not pl.GetDefinition().direction
                and abs(sp.depthNormal - dep) < 1e-6 and abs(sp.depthReverse - dep) < 1e-6):
            old.append(e)
assert len(old) == 4, ("фаски пластины: ожидалось 4 выреза", len(old))
# правка эскизов старых вырезов не сработала (16.11: вырез остался «верным», но ничего не снимал) —
# старые фаски удаляются вместе с эскизами и плоскостями, новые добавляются в конец дерева (после линий разъёма)
for e in old:
    sk = e.GetDefinition().GetSketch()
    for o in (e, sk, sk.GetDefinition().GetPlane()):
        assert qi(k5.TransferInterface(o, C.ksAPI7Dual, 0), A7.IFeature7).Delete()
p5.Update()


class Live(Part):
    """операции Part в уже открытом документе"""
    def __init__(self, d5):
        self.doc, self.p, self.first, self.sketches = d5, d5.GetPart(C3.pTop_Part), False, []


lp = Live(d5)
corners = ((GD_X0, Y_BOT, 1, 1), (GD_X1, Y_BOT, -1, 1), (GD_X0, GD_PL_Y1, 1, -1), (GD_X1, GD_PL_Y1, -1, -1))
for cx, cy, sx, sy in corners:                   # треугольник с гипотенузой x' + y' = GD_CH от угла, выведенный за контур
    a = GD_CH
    tri = [(cx - sx * 1.0, cy + sy * (a + 1.0)), (cx + sx * (a + 1.0), cy - sy * 1.0), (cx - sx * 1.0, cy - sy * 1.0)]
    lp.cut(lambda s, t=tri: s.poly_fixed(t), -GD_PL_T, GD_CH_Z1)
for sk in lp.sketches:
    sk.hidden = True
    sk.Update()
p5.Update()
check(top)
assert [sls.Item(i).Name for i in range(sls.Count)] == names
for i in range(sls.Count):
    assert sls.Item(i).Valid, ("линия разъёма сломалась", sls.Item(i).Name)
# фаска на углу — и в пластине, и на 1 мм выше выемки; грань под закрепление — 38 × 6
for cx, cy, sx, sy in corners:
    for z in (-3.0, GD_CH_Z1 / 2):
        assert faces(top, cx + sx * GD_CH / 2, cy + sy * GD_CH / 2, z), ("нет фаски", (cx, cy), z)
        assert not faces(top, cx + sx * 0.5, cy + sy * 0.5, z), ("угол не срезан", (cx, cy), z)
fix = faces(top, (GD_X0 + GD_X1) / 2, Y_BOT, -GD_PL_T / 2)
a_fix = qi(fix[0], A7.IFace).GetArea(1)
assert abs(a_fix - (GD_X1 - GD_X0 - 2 * GD_CH) * GD_PL_T) < 0.5, a_fix
print(f"направляющая: фаски 1 → {GD_CH:g} мм, z −6…{GD_CH_Z1:+g}; грань закрепления {a_fix:.1f} мм²; "
      f"линии разъёма целы ({len(names)}); масса {m0:.1f} → {mass(top):.1f} г")
d5.SaveAs(path)
