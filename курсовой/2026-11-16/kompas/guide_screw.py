# -*- coding: utf-8 -*-
"""Рабочая направляющая УКП.00.002 (файл пользователя — не перестраивается скриптом, только дорабатывается), 16.11:
  — фаски 1 × 45° на четырёх вертикальных углах пластины (z −6…0): в углах выемки стойки теперь скругления R1;
    с фасками пластина входит в выемку (у нижних углов — зазор по x 0,2, по y 0: пластина стоит на дне выемки);
  — площадка Ø12,4 на дне «ванны» (z = 0) и зенковка 90° под потайную головку винта М6, отверстие Ø6,6 насквозь.
Разметка под силу APM (guide_force_zone.py) сохраняется. Направляющая и сборка в КОМПАСе должны быть закрыты.
    python guide_screw.py"""
import os
from kompas_build import (A7, C, C3, FILES, GD_HOLE_R, GD_PL_T, GD_PL_Y1, GD_SPOT_R, GD_X0, GD_X1, GD_CH, GUIDE_COLOR, PARTS_DIR,
                          SCR_HEAD_C, SCR_HEAD_R, SCR_X, SCR_Y, Y_BOT, Part, app, k5, qi, xz_plane)

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

# фаски углов пластины: треугольник с гипотенузой x' + y' = GD_CH от угла, выведенный за контур
for cx, cy, sx, sy in ((GD_X0, Y_BOT, 1, 1), (GD_X1, Y_BOT, -1, 1), (GD_X0, GD_PL_Y1, 1, -1), (GD_X1, GD_PL_Y1, -1, -1)):
    a, b = GD_CH, GD_CH + 1.0
    tri = [(cx - sx * 1.0, cy + sy * a + sy * 1.0), (cx + sx * a + sx * 1.0, cy - sy * 1.0), (cx - sx * 1.0, cy - sy * 1.0)]
    p.cut(lambda s, t=tri: s.poly_fixed(t), -GD_PL_T, 0.0)
# площадка под головку: всё, что выше z = 0 (скругления «ванны»), в круге Ø12,4
p.cut(lambda s: s.circle(SCR_X, SCR_Y, GD_SPOT_R), 0.0, 10.5)
# зенковка по конусу головки (+0,1 мм) и отверстие Ø6,6 насквозь — вырез вращением; эскиз — в плоскости y = SCR_Y (u = x, v = −z)
r_top = SCR_HEAD_R + SCR_HEAD_C + 0.1             # конус головки r = 5,95 + z → зенковка r = 6,05 + z
z_bot = -(r_top - GD_HOLE_R)
prof = [(0, 0.1), (r_top + 0.1, 0.1), (GD_HOLE_R, z_bot), (GD_HOLE_R, -GD_PL_T - 0.5), (0, -GD_PL_T - 0.5)]
sk = p.sketch(0, lambda s: (s.poly_fixed([(SCR_X + r, -z) for r, z in prof]), s.axis(SCR_X, -1.0, SCR_X, GD_PL_T + 1.5)),
              xz_plane(p, SCR_Y))
p.revolve(sk, cut=True)

bad = [f.Name for f in (qi(x, A7.IFeature7) for x in qi(top, A7.IFeature7).SubFeatures(1, False, False)) if not f.Valid and not f.Excluded]
assert not bad, bad
fc = lambda x, y, z: [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ())) if o.ModelObjectType == C3.o3d_face]
assert fc(GD_X0 + GD_CH / 2, Y_BOT + GD_CH / 2, -3.0), "нет фаски на углу пластины"
assert fc(SCR_X + GD_HOLE_R, SCR_Y, -4.5), "нет отверстия Ø6,6"
assert fc(SCR_X + 4.6, SCR_Y, -1.45), "нет зенковки"                 # на конусе: r = 6,05 + z → z = −1,45 при r = 4,6
print(f"направляющая: масса {m0:.1f} → {qi(top, A7.IMassInertiaParam7).Mass:.1f} г")
p.save(FILES["guide"])
