# -*- coding: utf-8 -*-
"""Рабочая направляющая УКП.00.002 (файл пользователя — не перестраивается скриптом, только дорабатывается), 16.11.
Исходная версия — с разметкой под силу APM (guide_force_zone.py, коммит 1dce4c9); к ней:
  — фаски GD_CH × 45° на четырёх вертикальных углах пластины (z −6…+2): в углах выемки стойки — скругления POCKET_R; с фасками
    пластина входит в выемку (у нижних углов — зазор по x 0,2, по y 0: пластина стоит на дне выемки);
  — площадка Ø11,2 на дне «ванны» (срезаны скругления выше z = 0) и отверстие М10 × 1,5 с витками насквозь через пластину —
    под установочный винт М10 × 10, который входит и в стойку (резьба: 6 мм в пластине + 4 мм в стойке).
Направляющая и сборка в КОМПАСе должны быть закрыты.
    python guide_screw.py"""
import os
from math import radians, tan
from kompas_build import (A7, C, C3, FILES, GD_CH, GD_CH_Z1, GD_PL_T, GD_PL_Y1, GD_SPOT_R, GD_X0, GD_X1, GD_Z_HELIX, GUIDE_COLOR,
                          HOLE_R_BORE, HOLE_R_ROOT, PARTS_DIR, SCR_P, SCR_RMAJ, SCR_X, SCR_Y, Y_BOT, Part, app, helix, k5, qi,
                          thread_cut)

PATH = os.path.join(PARTS_DIR, FILES["guide"])


class Existing(Part):
    """доработка готовой детали теми же операциями, что у Part"""
    def __init__(self, path, color):
        self.doc = k5.Document3D()
        assert self.doc.Open(path, False), path
        self.p = self.doc.GetPart(C3.pTop_Part)
        self.color, self.opacity, self.first, self.sketches = color, 1.0, False, []


for i in range(app.Documents.Count):
    x = app.Documents.Item(i)
    assert x is None or os.path.normcase(qi(x, A7.IKompasDocument).PathName) != os.path.normcase(PATH), "направляющая открыта — закройте"
p = Existing(PATH, GUIDE_COLOR)
top = qi(k5.TransferInterface(p.doc, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
m0 = qi(top, A7.IMassInertiaParam7).Mass
assert qi(top, A7.IAuxiliaryGeomContainer).SplitLines.Count == 3, "ожидалась разметка под силу (3 линии разъёма)"
assert abs(m0 - 603.5) < 0.1, ("направляющая уже доработана — возьмите версию 1dce4c9 из git", m0)

# фаски углов пластины: треугольник с гипотенузой x' + y' = GD_CH от угла, выведенный за контур
for cx, cy, sx, sy in ((GD_X0, Y_BOT, 1, 1), (GD_X1, Y_BOT, -1, 1), (GD_X0, GD_PL_Y1, 1, -1), (GD_X1, GD_PL_Y1, -1, -1)):
    a = GD_CH
    tri = [(cx - sx * 1.0, cy + sy * (a + 1.0)), (cx + sx * (a + 1.0), cy - sy * 1.0), (cx - sx * 1.0, cy - sy * 1.0)]
    p.cut(lambda s, t=tri: s.poly_fixed(t), -GD_PL_T, GD_CH_Z1)
# площадка: всё, что выше z = 0 (скругления «ванны»), в круге Ø11,2; отверстие Ø8,78 насквозь через пластину
p.cut(lambda s: s.circle(SCR_X, SCR_Y, GD_SPOT_R), 0.0, 10.5)
p.cut(lambda s: s.circle(SCR_X, SCR_Y, HOLE_R_BORE), -GD_PL_T - 0.5, 0.5)
# витки М10 × 1,5: впадины направляющей — на полшага от впадин винта (как у стойки), линия от −6,75 до +1,5
sp = helix(p, GD_Z_HELIX, SCR_P, SCR_RMAJ, SCR_P, SCR_X, SCR_Y)
r_in = HOLE_R_BORE - 0.2
hw = (HOLE_R_ROOT - r_in) * tan(radians(30))
thread_cut(p, [(SCR_X + HOLE_R_ROOT, GD_Z_HELIX), (SCR_X + r_in, GD_Z_HELIX - hw), (SCR_X + r_in, GD_Z_HELIX + hw)], sp, SCR_Y)

bad = [f.Name for f in (qi(x, A7.IFeature7) for x in qi(top, A7.IFeature7).SubFeatures(1, False, False)) if not f.Valid and not f.Excluded]
assert not bad, bad
fc = lambda x, y, z: [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ())) if o.ModelObjectType == C3.o3d_face]
assert fc(GD_X0 + GD_CH / 2, Y_BOT + GD_CH / 2, -3.0), "нет фаски на углу пластины"
assert not fc(SCR_X, SCR_Y, -3.0) and not fc(SCR_X + 4.0, SCR_Y, -3.0), "отверстие не насквозь"
print(f"направляющая: масса {m0:.1f} → {qi(top, A7.IMassInertiaParam7).Mass:.1f} г")
p.save(FILES["guide"])
