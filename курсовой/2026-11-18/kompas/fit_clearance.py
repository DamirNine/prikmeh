# -*- coding: utf-8 -*-
"""Зазоры в подвижных посадках под 3D-печать (18.11). Напечатанная кулиса на оси O не проворачивалась — в модели отверстие Ø10
сидело на оси Ø10 без зазора, а принтер делает отверстия меньше; кулиса сломалась при повороте. Доработка готовых деталей
(в дереве добавляются вырезы, остальное не трогается):
  — кулиса: отверстие под ось O Ø10 → Ø10,6 (по 0,3 мм на сторону) через ступицу и полосу;
  — ползун: отверстие под палец D Ø10 → Ø10,6 (ползун поворачивается на пальце);
  — кожух: утолщение левой стенки отодвинуто от планки направляющей на 0,3 мм (было касание — при надевании кожух тёрся
    по планке).
Не меняются: палец в камне (запрессовка — должен сидеть туго), шайба на пальце (Ø10,5, неподвижна), резьбы (зазоры под печать
уже есть), камень на кулисе и ползун между планками (по 0,5 мм), пластина направляющей в выемке (0,2 мм — подшкурить при
необходимости). Детали и сборка в КОМПАСе должны быть закрыты; после — python kompas_assembly.py (грани сопряжений новые).
    python fit_clearance.py"""
import json, os
from kompas_build import (A7, C, C3, CV_PAD_Y1, CV_T, CV_Y0, CV_Z, E, FILES, HERE, PARTS_DIR, Part, app, k5, qi)

GAP = 0.3                                         # радиальный зазор, мм
R_HOLE = 5.0 + GAP                                # Ø10,6
X_PAD = E - 18.5                                  # грань утолщения кожуха, касавшаяся планки направляющей


class Existing(Part):
    """доработка готовой детали теми же операциями, что у Part"""
    def __init__(self, path, color):
        self.doc = k5.Document3D()
        assert self.doc.Open(path, False), path
        self.p = self.doc.GetPart(C3.pTop_Part)
        self.color, self.opacity, self.first, self.sketches = color, 1.0, False, []


def faces(top, x, y, z):
    return [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ())) if o.ModelObjectType == C3.o3d_face]


opened = [os.path.normcase(qi(app.Documents.Item(i), A7.IKompasDocument).PathName) for i in range(app.Documents.Count)
          if app.Documents.Item(i) is not None]
for k in ("kulisa", "polzun", "cover"):
    assert os.path.normcase(os.path.join(PARTS_DIR, FILES[k])) not in opened, (FILES[k], "открыта в КОМПАСе — закройте")
assert not any(o.endswith(".a3d") for o in opened), "сборка открыта в КОМПАСе — закройте"
mj = os.path.join(HERE, "parts_mass.json")
mass = json.load(open(mj, encoding="utf-8"))
JOBS = {  # деталь: (цвет, вырезы, проверка «грань есть», проверка «грани нет»)
    "kulisa": ("#2d3540", [(lambda s: s.circle(0, 0, R_HOLE), -13.0, 9.0)], (0, R_HOLE, 4), (0, 5.0, 4)),
    "polzun": ("#3a4049", [(lambda s: s.circle(0, 0, R_HOLE), -9.0, 9.0)], (R_HOLE, 0, 0), (5.0, 0, 0)),
    "cover": ("#b03a2e", [(lambda s: s.rect(X_PAD - GAP, CV_Y0 + CV_T, X_PAD + 0.5, CV_PAD_Y1), -1.0, CV_Z - CV_T)],
              (X_PAD - GAP, -20.0, 20.0), (X_PAD, -20.0, 20.0)),
}
for k, (color, cuts, must, gone) in JOBS.items():
    path = os.path.join(PARTS_DIR, FILES[k])
    p = Existing(path, color)
    top = qi(k5.TransferInterface(p.doc, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
    m0 = qi(top, A7.IMassInertiaParam7).Mass
    assert abs(m0 - mass[k]) < 0.05, (k, "деталь уже доработана или не та", m0, mass[k])
    assert faces(top, *gone), (k, "нет исходной грани", gone)
    for draw, z0, z1 in cuts:
        p.cut(draw, z0, z1)
    bad = [f.Name for f in (qi(x, A7.IFeature7) for x in qi(top, A7.IFeature7).SubFeatures(1, False, False)) if not f.Valid and not f.Excluded]
    assert not bad, (k, bad)
    assert faces(top, *must) and not faces(top, *gone), (k, "вырез не там")
    mass[k] = p.save(FILES[k])[1]
    print(f"    {k}: {m0:.1f} → {mass[k]:.1f} г")
json.dump(mass, open(mj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ВАЖНО: пересоберите сборку: python kompas_assembly.py")
