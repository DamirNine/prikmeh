# -*- coding: utf-8 -*-
"""22.11 (пользователь, по фото Корнеева): на нижних углах направляющей ступенька — полка под шток (print_split.py) легла в конец
дерева и заново заполнила угол, срезанный фаской пластины 4×45°, на z 0…2. Фаска нижних углов вырезается заново на ту же длину,
что у верхних углов (z −6…+2). Верхние углы не меняются. Обе направляющие (А и Б),
правка готовых деталей — вырез в конце дерева, линии разъёма APM сохраняются.
    python fix_bottom_chamfer.py"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A5, A7, C, C3, GD_CH, GD_CH_Z1, GD_PL_T, GD_X0, GD_X1, GD_Z1, PARTS_DIR, Part, Y_BOT, app, k5, qi

FILES = {"guide": "УКП.00.002 Направляющая.m3d", "guide_b": "УКП.00.002-01 Направляющая (без планок).m3d"}


class Live(Part):
    def __init__(self, d5):
        self.doc, self.p, self.first, self.sketches = d5, d5.GetPart(C3.pTop_Part), False, []


faces = lambda top, x, y, z: [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ()))
                              if o.ModelObjectType == C3.o3d_face]
masses = {}
for key, fn in FILES.items():
    path = os.path.join(PARTS_DIR, fn)
    for i in range(app.Documents.Count):
        x = app.Documents.Item(i)
        if x is not None and os.path.normcase(qi(x, A7.IKompasDocument).PathName) == os.path.normcase(path):
            qi(x, A7.IKompasDocument).Close(0)
    d = app.Documents.Open(path, True, False)
    d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
    top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
    sls = qi(top, A7.IAuxiliaryGeomContainer).SplitLines
    m0 = qi(top, A7.IMassInertiaParam7).Mass
    lp = Live(d5)
    for cx, sx in ((GD_X0, 1), (GD_X1, -1)):              # нижние углы: (x угла, направление внутрь по x)
        cy, sy, a = Y_BOT, 1, GD_CH
        tri = [(cx - sx * 1.0, cy + sy * (a + 1.0)), (cx + sx * (a + 1.0), cy - sy * 1.0), (cx - sx * 1.0, cy - sy * 1.0)]
        lp.cut(lambda s, t=tri: s.poly_fixed(t), -GD_PL_T - 1.0, GD_CH_Z1)   # как у верхних углов: z −6…+2 (пользователь 22.11:
                                                                              # «на такую же длину, как с другой стороны»); полка
                                                                              # (print_split) легла в конец дерева и заполнила угол на z 0…2
    for sk in lp.sketches:
        sk.hidden = True; sk.Update()
    lp.p.Update()
    bad = [f.Name for f in (qi(x, A7.IFeature7) for x in qi(top, A7.IFeature7).SubFeatures(1, False, False)) if not f.Valid and not f.Excluded]
    assert not bad, bad
    assert all(sls.Item(i).Valid for i in range(sls.Count)), "линия разъёма"
    for cx, sx in ((GD_X0, 1), (GD_X1, -1)):              # фаска есть и в пластине, и у передней грани; угол срезан
        for z in [k * 0.5 for k in range(-11, 4)]:         # каждые 0,5 мм на длине фаски z −5,5…+1,5
            assert faces(top, cx + sx * GD_CH / 2, Y_BOT + GD_CH / 2, z), ("нет фаски", cx, z)
            assert not faces(top, cx + sx * 0.5, Y_BOT + 0.5, z), ("угол не срезан", cx, z)
    masses[key] = qi(top, A7.IMassInertiaParam7).Mass
    print(f"{fn}: фаска нижних углов — z −6…+2, как у верхних; масса {m0:.1f} → {masses[key]:.1f} г; линии разъёма целы ({sls.Count})")
    d5.SaveAs(path)
    d.Close(0)
mj = "parts_mass.json"
mm = json.load(open(mj, encoding="utf-8")); mm.update(masses)
json.dump(mm, open(mj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
