# -*- coding: utf-8 -*-
"""21.11 (пользователь): второй вариант направляющей — как «стул» на доске: у направляющей сверху отпилены обе планки —
всё выше верха пластины (y = GD_PL_Y1 = −17) снято; остаются пластина в выемке стойки, нижние боковые стенки и полка с
отверстием под шток. Ползун ведут шток в отверстии полки и палец в камне. Брусок ползуна в нижнем положении — выше −17
(−14,75), в стенки не заходит. Деталь — копия готовой направляющей (вариант A) с вырезом в конце дерева.
    python variant_b.py   → Детали/УКП.00.002-01 Направляющая (без планок).m3d, масса — parts_mass.json["guide_b"]"""
import json, os, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A5, A7, C, C3, FILES, GD_PL_Y1, GD_X0, GD_X1, PARTS_DIR, Part, app, k5, qi

GUIDE_B = "УКП.00.002-01 Направляющая (без планок).m3d"
src, dst = os.path.join(PARTS_DIR, FILES["guide"]), os.path.join(PARTS_DIR, GUIDE_B)
for i in range(app.Documents.Count):
    x = app.Documents.Item(i)
    if x is not None and os.path.normcase(qi(x, A7.IKompasDocument).PathName) in (os.path.normcase(src), os.path.normcase(dst)):
        qi(x, A7.IKompasDocument).Close(0)
shutil.copyfile(src, dst)
d = app.Documents.Open(dst, True, False)
d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart


class Live(Part):
    def __init__(self, d5):
        self.doc, self.p, self.first, self.sketches = d5, d5.GetPart(C3.pTop_Part), False, []


lp = Live(d5)
mass0 = qi(top, A7.IMassInertiaParam7).Mass
lp.p.name, lp.p.marking = "Направляющая (без планок)", "УКП.00.002-01"
lp.p.Update()
lp.cut(lambda s: s.rect(GD_X0 - 5, GD_PL_Y1, GD_X1 + 5, 60.0), -7.0, 62.0)      # всё выше верха пластины
for sk in lp.sketches:
    sk.hidden = True; sk.Update()
lp.p.Update()
# линии разъёма APM на планках (зоны ползуна) теряют грани — во втором варианте они не нужны: удаляются ошибочные
sls = qi(top, A7.IAuxiliaryGeomContainer).SplitLines
gone = []
for i in reversed(range(sls.Count)):
    sl = sls.Item(i)
    if not sl.Valid:
        gone.append(sl.Name)
        qi(sl, A7.IFeature7).Delete()
lp.p.Update()
bad = [f.Name for f in (qi(x, A7.IFeature7) for x in qi(top, A7.IFeature7).SubFeatures(1, False, False)) if not f.Valid and not f.Excluded]
assert not bad, bad
g = [round(v, 2) for v in lp.p.GetGabarit(True, True)[1:]]
assert abs(g[4] - GD_PL_Y1) < 0.01, g                       # верх — по верху пластины
m = qi(top, A7.IMassInertiaParam7).Mass
d5.SaveAs(dst)
d.Close(0)
mj = "parts_mass.json"
mm = json.load(open(mj, encoding="utf-8")); mm["guide_b"] = m
json.dump(mm, open(mj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"вариант B: {GUIDE_B}; габарит {g}; масса {mass0:.1f} → {m:.1f} г; удалены линии разъёма: {gone or 'нет'}")
