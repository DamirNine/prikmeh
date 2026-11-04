# -*- coding: utf-8 -*-
"""Сборка укупоривателя УКП.00.000 в КОМПАС-3D v25 из отдельных деталей папки «Детали» (kompas_build.py).
Закреплено только основание; остальные детали соединены сопряжениями по граням и осям:
  стойка — на основании (совпадение граней, расстояния от задней и левой кромок 10 и 18 мм);
  ось O — в отверстии стойки (соосность), задний торец заподлицо с задней гранью стойки;
  направляющая и упоры — задними гранями на передней грани стойки, положение — расстояниями от плоскостей стойки;
  кулиса — отверстием на оси O, ступица в 0,5 мм от стойки; угол кулисы — в диапазоне φк…φн (22,72…59,47°);
  ручка — на конце кулисы; камень — средней плоскостью по оси кулисы (скользит вдоль неё);
  ползун — задней гранью по планкам направляющей, средней плоскостью по оси направляющей; палец D — соосно отверстию ползуна,
  камень в 1 мм от ползуна (палец удерживается в ползуне стопорным кольцом).
Детали предварительно ставятся в положение φу; грани для сопряжений находятся по точкам, заданным в координатах детали
(пересчёт в сборку — по текущему положению детали). Проверка до сохранения: угол задаётся сопряжением (диапазон на время
выключен) — y ползуна = e·tg φ. Диапазон угла КОМПАС соблюдает при перемещении деталей мышью; через API он не принуждается
(перестроение не сдвигает кулису в диапазон), поэтому границы проверяются вручную. Повторное сохранение открытой сборки
через API не проходит, поэтому всё — в одном запуске."""
import json, os
from math import atan2, degrees, cos, sin, radians
from kompas_build import (A7, C, C3, E, FILES, HERE, PARTS_DIR, PH0, PH_K, PH_N, PH_Y, X_ST0, Y_ST0, Y_BOT, Z_ST, LO_X0,
                          LO_Y0, HI_X0, HI_Y1, app, qi, yD)

ASM = os.path.join(HERE, "УКП.00.000 Укупориватель.a3d")
c0, s0 = cos(radians(PH0)), sin(radians(PH0))
R0 = lambda x, y: (x * c0 - y * s0, x * s0 + y * c0)              # поворот на φ0 вокруг оси O
D0 = (E, yD(PH0))

doc = qi(app.Documents.Add(C.ksDocumentAssembly, True), A7.IKompasDocument3D)
top = doc.TopPart
top.Name, top.Marking = "Укупориватель ручной", "УКП.00.000"
# ---------------- вставка деталей и начальное положение: (начало детали в сборке, поворот вокруг z)
PLACE = {"base": ((32.5, Y_ST0, 24.0), 0), "stand": ((0, 0, Z_ST), 0), "axle": ((0, 0, Z_ST - 12), 0),
         "guide": ((E, Y_BOT, Z_ST), 0), "stop_lo": ((LO_X0, LO_Y0, Z_ST), 0), "stop_hi": ((HI_X0, HI_Y1, Z_ST), 0),
         "kulisa": ((0, 0, -21.5), PH0), "grip": ((*R0(402.5, 0), -17.5), PH0), "kamen": ((*D0, -9.0), PH0),
         "polzun": ((*D0, 0.0), 0)}
comp = {}
for k, f in FILES.items():
    c = top.Parts.AddFromFile(os.path.join(PARTS_DIR, f), True, False)
    (x, y, z), ang = PLACE[k]
    pl = c.Placement
    pl.SetOrigin(x, y, z)
    if ang:
        pl.Rotate(0.0, 0.0, 0.0, 0.0, 0.0, 1.0, ang)               # центр поворота — в координатах самой детали
    c.UpdatePlacement(False)
    comp[k] = c
comp["base"].Fixed = True
comp["base"].Update()
top.RebuildModel(True)


def face(k, lx, ly, lz):
    """грань детали k через точку (lx, ly, lz) в координатах самой детали — пересчёт в сборку по текущему положению детали"""
    pl = comp[k].Placement
    o, ax, ay, az = pl.GetOrigin()[-3:], pl.GetVector(0)[-3:], pl.GetVector(1)[-3:], pl.GetVector(2)[-3:]
    x, y, z = (o[i] + lx * ax[i] + ly * ay[i] + lz * az[i] for i in range(3))
    r = comp[k].FindObjectsByPoint(x, y, z, True)
    fs = [qi(o, A7.IModelObject) for o in (r or ())]
    fs = [o for o in fs if o.ModelObjectType == C3.o3d_face]
    assert len(fs) == 1, (k, (lx, ly, lz), len(fs))
    return fs[0]


plane = lambda k, t: comp[k].DefaultObject(t)
XY, XZ, YZ = C3.o3d_planeXOY, C3.o3d_planeXOZ, C3.o3d_planeYOZ
mates = top.MateConstraints
MC = []


def mate(title, kind, o1, o2, value=None, align=None):
    """align: OPP — грани прижаты друг к другу (нормали встречные), CO — заподлицо или параллельные плоскости"""
    m = mates.Add(kind)
    m.BaseObject1, m.BaseObject2 = o1, o2
    m.Alignment = C3.ksMCAlignmentClosest if align is None else align
    if value is not None:
        m.ParamValue = value
    ok = m.Update()
    MC.append((title, m))
    print(f"  {title}: {'да' if ok else 'НЕТ'}")
    return m


COIN, DIST, CONC = C3.mc_Coincidence, C3.mc_Distance, C3.mc_Concentric
OPP, CO = C3.ksMCAlignmentOpposite, C3.ksMCAlignmentCooriented
F_ST = face("stand", -20, -200, 0)                                      # передняя грань стойки
print("Сопряжения:")
mate("стойка на основании", COIN, face("stand", 0, Y_ST0, -6), face("base", 0, 0, 50), align=OPP)
mate("стойка — 10 мм от задней кромки основания", DIST, face("stand", -20, -200, -12), face("base", 0, -10, -80), 10.0, CO)
mate("стойка — 18 мм от левой кромки основания", DIST, face("stand", X_ST0, -200, -6), face("base", -100, -10, 0), 18.0, CO)
mate("ось O в отверстии стойки", CONC, face("axle", 5, 0, 6), face("stand", 5, 0, -6))
mate("ось O заподлицо с задней гранью стойки", COIN, face("axle", 2, 2, 0), face("stand", -20, -200, -12), align=CO)
mate("направляющая на стойке", COIN, face("guide", 15.5, 6, 0), F_ST, align=OPP)
mate("ось направляющей — на e от оси O", DIST, plane("guide", YZ), plane("stand", YZ), E, CO)
mate("низ направляющей", DIST, plane("guide", XZ), plane("stand", XZ), -Y_BOT, CO)
mate("нижний упор на стойке", COIN, face("stop_lo", 5, 2, 0), F_ST, align=OPP)
mate("нижний упор — по x", DIST, plane("stop_lo", YZ), plane("stand", YZ), LO_X0, CO)
mate("нижний упор — по y", DIST, plane("stop_lo", XZ), plane("stand", XZ), -LO_Y0, CO)
mate("верхний упор на стойке", COIN, face("stop_hi", 3, -2, 0), F_ST, align=OPP)
mate("верхний упор — по x", DIST, plane("stop_hi", YZ), plane("stand", YZ), HI_X0, CO)
mate("верхний упор — по y", DIST, plane("stand", XZ), plane("stop_hi", XZ), HI_Y1, CO)   # расстояние — по нормали 2-й плоскости (−y)
mate("кулиса на оси O", CONC, face("kulisa", 0, 5, 4), face("axle", 5, 0, 20))
mate("ступица в 0,5 мм от стойки", DIST, face("kulisa", 0, 6.5, -12), F_ST, 0.5, OPP)
ang = mates.Add(C3.mc_Angle)                                            # угол кулисы с диапазоном
ang.BaseObject1, ang.BaseObject2 = plane("kulisa", XZ), plane("stand", XZ)
itv = qi(ang, A7.IMateInterval)
itv.UseInterval = True
itv.SetValueRange(PH_K, PH_N)
ang.ParamValue = PH0
print(f"  угол кулисы {PH_K:.2f}…{PH_N:.2f}°: {'да' if ang.Update() else 'НЕТ'}")
MC.append(("угол кулисы", ang))
mate("ручка — по задней грани полосы", COIN, face("grip", 47.5, 0, -4), face("kulisa", 450, 0, 0), align=OPP)
mate("ручка — по нижнему ребру полосы", COIN, face("grip", 47.5, -9, 0), face("kulisa", 450, -9, 4), align=OPP)
mate("ручка — 402,5 мм от оси O", DIST, plane("grip", YZ), plane("kulisa", YZ), 402.5, CO)
mate("камень по оси кулисы", COIN, plane("kamen", XZ), plane("kulisa", XZ), align=CO)
mate("ползун по планкам направляющей", COIN, face("polzun", 0, 15, -8), face("guide", 15.5, 50, 26), align=CO)
mate("ползун по оси направляющей", COIN, plane("polzun", YZ), plane("guide", YZ), align=CO)
mate("палец D в отверстии ползуна", CONC, face("kamen", 5, 0, 8), face("polzun", 5, 0, 0))
mate("камень в 1 мм от ползуна (палец держит стопорное кольцо)", DIST, plane("polzun", XY), plane("kamen", XY), 9.0, CO)
top.RebuildModel(True)
bad = [t for t, m in MC if not m.Valid]
print(f"сопряжений: {len(MC)}, не выполнено: {bad or 'нет'}")

# ---------------- проверки
origin = lambda k: comp[k].Placement.GetOrigin()[-3:]
angle = lambda k: degrees(atan2(*comp[k].Placement.GetVector(0)[-3:][1::-1]))


def drive(ph):
    itv.UseInterval = False
    ang.ParamValue = ph; ang.Update(); top.RebuildModel(True)


out = {"fixed": {k: origin(k) for k in ("stand", "axle", "guide", "stop_lo", "stop_hi")}, "kin": []}
print("Неподвижные детали после сопряжений (начало в координатах сборки):",
      {k: [round(v, 2) for v in o] for k, o in out["fixed"].items()})
print("Проверка 1 — кинематика (угол задан сопряжением):")
for ph in (PH_K, 30.0, PH_Y, 50.0, PH_N):
    drive(ph)
    y = origin("polzun")[1]; xk, yk = origin("kamen")[:2]
    out["kin"].append([ph, angle("kulisa"), y, yD(ph)])
    print(f"  φ = {ph:6.2f}° (кулиса {angle('kulisa'):6.2f}°): ползун y = {y:8.3f}, e·tg φ = {yD(ph):8.3f}; "
          f"камень ({xk:.3f}; {yk:.3f}); ручка {angle('grip'):6.2f}°")
drive(PH0)
itv.UseInterval = True; itv.SetValueRange(PH_K, PH_N); ang.ParamValue = PH0; ang.Update(); top.RebuildModel(True)
print(f"положение при сохранении: {angle('kulisa'):.2f}°, ползун y = {origin('polzun')[1]:.3f} (e·tg φ = {yD(angle('kulisa')):.3f}), "
      f"диапазон {itv.MinValue:.2f}…{itv.MaxValue:.2f}°, невыполненных сопряжений: {sum(not m.Valid for _, m in MC)}")
print("упоры:", [round(v, 2) for v in origin("stop_lo")], [round(v, 2) for v in origin("stop_hi")])
doc.SaveAs(ASM)
print("сохранено:", ASM, os.path.exists(ASM))
json.dump(out, open(os.path.join(HERE, "assembly_check.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
