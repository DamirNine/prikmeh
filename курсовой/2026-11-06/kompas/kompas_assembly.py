# -*- coding: utf-8 -*-
"""Сборка укупоривателя УКП.00.000 в КОМПАС-3D v25 из деталей папки «Детали» (kompas_build.py).
Стойка (лист с осью O, направляющей и упорами) крепится к стене — в сборке закреплена; остальные детали соединены
сопряжениями:
  кулиса — отверстием на оси O, ступица в 0,5 мм от стойки; угол кулисы — в диапазоне φк…φн (22,72…59,47°);
  камень — средней плоскостью по оси кулисы (скользит вдоль неё);
  ползун — задней гранью по планкам направляющей, ось ползуна — на e от оси O; палец D — соосно отверстию ползуна,
  торец пальца заподлицо с передней гранью ползуна (обойма — в 1 мм за ползуном, палец держит стопорное кольцо);
  кожух — средними плоскостями по плоскостям стойки, задняя кромка на передней грани стойки; сдвигается вперёд на 0…120 мм
  (сопряжение «На расстоянии» с диапазоном) — так он снимается, пазы под кулису и шток открыты назад.
Детали предварительно ставятся в положение φу; грани для сопряжений находятся по точкам, заданным в координатах детали
(пересчёт в сборку — по текущему положению детали). Проверка до сохранения: угол задаётся сопряжением (диапазон на время
выключен) — y ползуна = e·tg φ. Диапазон угла КОМПАС соблюдает при перемещении деталей мышью; через API он не принуждается
(перестроение не сдвигает кулису в диапазон), поэтому границы проверяются вручную. Повторное сохранение открытой сборки
через API не проходит, поэтому всё — в одном запуске."""
import json, os
from math import atan2, degrees, cos, sin, radians
from kompas_build import A7, B_ST, C, C3, E, FILES, HERE, PARTS_DIR, PH0, PH_K, PH_N, PH_Y, Y_BOT, Z_ST, app, qi, yD

ASM = os.path.join(HERE, "УКП.00.000 Укупориватель.a3d")
c0, s0 = cos(radians(PH0)), sin(radians(PH0))
R0 = lambda x, y: (x * c0 - y * s0, x * s0 + y * c0)              # поворот на φ0 вокруг оси O
D0 = (E, yD(PH0))

doc = qi(app.Documents.Add(C.ksDocumentAssembly, True), A7.IKompasDocument3D)
top = doc.TopPart
top.Name, top.Marking = "Укупориватель ручной", "УКП.00.000"
# ---------------- вставка деталей и начальное положение: (начало детали в сборке, поворот вокруг z)
PLACE = {"stand": ((0, 0, Z_ST), 0), "kulisa": ((0, 0, -21.5), PH0), "kamen": ((*D0, -9.0), PH0), "polzun": ((*D0, 0.0), 0),
         "cover": ((0, 0, Z_ST), 0)}
COVER_MAX = 120.0                                 # на сколько кожух можно сдвинуть вперёд, мм (120 — решение пользователя 05.11)
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
PARTS_MASS = json.load(open(os.path.join(HERE, "parts_mass.json"), encoding="utf-8"))
for k, c in comp.items():                         # КОМПАС держит в памяти прежнюю модель файла, даже когда документы закрыты:
    m = qi(c, A7.IMassInertiaParam7).Mass         # после перестройки деталей, открывавшихся в этом сеансе, его надо перезапустить
    assert abs(m - PARTS_MASS[k]) < 0.5, ("в сборку попала старая модель — перезапустите КОМПАС", k, m, PARTS_MASS[k])
comp["stand"].Fixed = True                                              # стойка крепится к стене
comp["stand"].Update()
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
mate("кулиса на оси O", CONC, face("kulisa", 0, 5, 4), face("stand", 5, 0, 16))
mate("ступица в 0,5 мм от стойки", DIST, face("kulisa", 0, 6.5, -12), F_ST, 0.5, OPP)
ang = mates.Add(C3.mc_Angle)                                            # угол кулисы с диапазоном
ang.BaseObject1, ang.BaseObject2 = plane("kulisa", XZ), plane("stand", XZ)
itv = qi(ang, A7.IMateInterval)
itv.UseInterval = True
itv.SetValueRange(PH_K, PH_N)
ang.ParamValue = PH0
print(f"  угол кулисы {PH_K:.2f}…{PH_N:.2f}°: {'да' if ang.Update() else 'НЕТ'}")
MC.append(("угол кулисы", ang))
mate("камень по оси кулисы", COIN, plane("kamen", XZ), plane("kulisa", XZ), align=CO)
mate("ползун по планкам направляющей", COIN, face("polzun", 0, 15, -8), face("stand", E + 15.5, 0, 26), align=CO)
mate("ось ползуна — на e от оси O", DIST, plane("polzun", YZ), plane("stand", YZ), E, CO)
mate("палец D в отверстии ползуна", CONC, face("kamen", 5, 0, 8), face("polzun", 5, 0, 0))
mate("торец пальца D заподлицо с передней гранью ползуна", COIN, face("kamen", 2, 0, 17), face("polzun", 0, 15, 8), align=CO)
mate("кожух по стойке: x", COIN, plane("cover", YZ), plane("stand", YZ), align=CO)
mate("кожух по стойке: y", COIN, plane("cover", XZ), plane("stand", XZ), align=CO)
cov = mates.Add(DIST)                                                   # сдвиг кожуха вперёд с диапазоном
cov.BaseObject1, cov.BaseObject2 = plane("stand", XY), plane("cover", XY)   # такой порядок — сдвиг вперёд (+z)
cov.Alignment = CO
cov_itv = qi(cov, A7.IMateInterval)
cov_itv.UseInterval = True
cov_itv.SetValueRange(0.0, COVER_MAX)
cov.ParamValue = 0.0
print(f"  кожух сдвигается вперёд на 0…{COVER_MAX:g} мм: {'да' if cov.Update() else 'НЕТ'}")
MC.append(("кожух", cov))
top.RebuildModel(True)
bad = [t for t, m in MC if not m.Valid]
print(f"сопряжений: {len(MC)}, не выполнено: {bad or 'нет'}")


def check_places():
    """каждая деталь — там, где задумано (сопряжения «На расстоянии» могут поставить деталь по другую сторону плоскости)"""
    for k, ((x, y, z), ph) in PLACE.items():
        o, v = comp[k].Placement.GetOrigin()[-3:], comp[k].Placement.GetVector(0)[-3:]
        vz = comp[k].Placement.GetVector(2)[-3:]
        err = max(abs(o[0] - x), abs(o[1] - y), abs(o[2] - z), abs(v[0] - cos(radians(ph))), abs(v[1] - sin(radians(ph))),
                  abs(vz[2] - 1))
        assert err < 1e-3, (k, [round(t, 3) for t in o], [round(t, 3) for t in v], [round(t, 3) for t in vz])
    print("положение всех деталей совпадает с задуманным")


check_places()

# ---------------- проверки
origin = lambda k: comp[k].Placement.GetOrigin()[-3:]
angle = lambda k: degrees(atan2(*comp[k].Placement.GetVector(0)[-3:][1::-1]))


def drive(ph):
    itv.UseInterval = False
    ang.ParamValue = ph; ang.Update(); top.RebuildModel(True)


out = {"kin": []}
print("Проверка 1 — кинематика (угол задан сопряжением):")
for ph in (PH_K, 30.0, PH_Y, 50.0, PH_N):
    drive(ph)
    y = origin("polzun")[1]; xk, yk = origin("kamen")[:2]
    out["kin"].append([ph, angle("kulisa"), y, yD(ph)])
    print(f"  φ = {ph:6.2f}° (кулиса {angle('kulisa'):6.2f}°): ползун y = {y:8.3f}, e·tg φ = {yD(ph):8.3f}; "
          f"камень ({xk:.3f}; {yk:.3f}), угол камня {angle('kamen'):6.2f}°")
print("Проверка 2 — кожух (сдвиг задан сопряжением):")
for dz in (COVER_MAX, 0.0):
    cov_itv.UseInterval = False
    cov.ParamValue = dz; cov.Update(); top.RebuildModel(True)
    print(f"  сдвиг {dz:g} мм: задняя кромка кожуха z = {origin('cover')[2]:.2f} (надо {Z_ST + dz:.2f})")
    assert abs(origin("cover")[2] - (Z_ST + dz)) < 1e-3
cov_itv.UseInterval = True; cov_itv.SetValueRange(0.0, COVER_MAX); cov.Update(); top.RebuildModel(True)
drive(PH0)
itv.UseInterval = True; itv.SetValueRange(PH_K, PH_N); ang.ParamValue = PH0; ang.Update(); top.RebuildModel(True)
check_places()
print(f"положение при сохранении: {angle('kulisa'):.2f}°, ползун y = {origin('polzun')[1]:.3f} (e·tg φ = {yD(angle('kulisa')):.3f}), "
      f"диапазон {itv.MinValue:.2f}…{itv.MaxValue:.2f}°, невыполненных сопряжений: {sum(not m.Valid for _, m in MC)}")
wall = origin("stand")[2] - B_ST                                        # стена — плоскость задней грани листа
print(f"от стены до кулисы: задняя грань {origin('kulisa')[2] - wall:.1f} мм, передняя {origin('kulisa')[2] + 8 - wall:.1f} мм; "
      f"ось ползуна {origin('polzun')[2] - wall:.1f} мм")
doc.SaveAs(ASM)
print("сохранено:", ASM, os.path.exists(ASM))
json.dump(out, open(os.path.join(HERE, "assembly_check.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
