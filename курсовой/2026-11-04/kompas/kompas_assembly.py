# -*- coding: utf-8 -*-
"""Сборка укупоривателя в КОМПАС-3D v25 из деталей kompas_build.py: неподвижные детали закреплены в начале координат,
подвижные связаны сопряжениями; угол кулисы ограничен диапазоном φк…φн. Проверки до сохранения: угол задаётся
сопряжением — положение ползуна сравнивается с yD = e·tg φ; кулиса за пределами диапазона после включения диапазона
возвращается в φк…φн. Сохраняется положение φу (повторное сохранение открытой сборки через API КОМПАС не проходит)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "kompas_build.py"), encoding="utf-8").read()     # подключение к КОМПАС и исходные данные
exec(compile(src[:src.index("# ================================================================ построение детали")], "kompas_build", "exec"))

FILES = {k: os.path.join(HERE, v) for k, v in {
    "base": "УКП.00.001 Основание.m3d", "stand": "УКП.00.002 Стойка.m3d", "axle": "УКП.00.003 Ось O.m3d",
    "guide": "УКП.00.004 Направляющая.m3d", "stop_lo": "УКП.00.005 Упор нижний.m3d", "stop_hi": "УКП.00.006 Упор верхний.m3d",
    "kulisa": "УКП.01.001 Кулиса.m3d", "grip": "УКП.01.002 Ручка.m3d", "kamen": "УКП.02.001 Камень с пальцем D.m3d",
    "polzun": "УКП.03.001 Ползун.m3d"}.items()}
ASM = os.path.join(HERE, "УКП.00.000 Укупориватель.a3d")

doc = qi(app.Documents.Add(C.ksDocumentAssembly, True), A7.IKompasDocument3D)
top = doc.TopPart
top.Name, top.Marking = "Укупориватель ручной", "УКП.00.000"
parts = top.Parts
comp = {}
for k, f in FILES.items():
    comp[k] = parts.AddFromFile(f, True, False)
    assert comp[k] is not None, f


def place(c, x, y, ang):
    pl = c.Placement
    pl.SetOrigin(x, y, 0.0)
    if ang:
        pl.Rotate(x, y, 0.0, 0.0, 0.0, 1.0, ang)                 # поворот вокруг собственного начала
    c.UpdatePlacement(False)                                     # Placement только для чтения: меняется сам объект


for k in ("base", "stand", "axle", "guide", "stop_lo", "stop_hi"):
    place(comp[k], 0, 0, 0)
    comp[k].Fixed = True
    comp[k].Update()
place(comp["kulisa"], 0, 0, PH0)
place(comp["grip"], 0, 0, PH0)
place(comp["kamen"], E, yD(PH0), PH0)
place(comp["polzun"], E, yD(PH0), 0)

PL = lambda c, t: (c if c is not None else top).DefaultObject(t)
mates = top.MateConstraints
MC = {}


def mate(key, kind, o1, o2, value=None, align=None):
    m = mates.Add(kind)
    m.BaseObject1, m.BaseObject2 = o1, o2
    if align is not None:
        m.Alignment = align
    if value is not None:
        m.ParamValue = value
    ok = m.Update()
    MC[key] = m
    print(f"  сопряжение {key}: {ok}")
    return m


XY, XZ, YZ, OZ = C3.o3d_planeXOY, C3.o3d_planeXOZ, C3.o3d_planeYOZ, C3.o3d_axisOZ
CO, PAR = C3.ksMCAlignmentCooriented, C3.ksMCAlignmentClosest
print("Сопряжения:")
kul, kam, pol, grp = comp["kulisa"], comp["kamen"], comp["polzun"], comp["grip"]
mate("кулиса XY", C3.mc_Coincidence, PL(kul, XY), PL(None, XY), align=CO)
mate("кулиса — ось O", C3.mc_Concentric, PL(kul, OZ), PL(None, OZ), align=CO)
ang = mates.Add(C3.mc_Angle)
ang.BaseObject1, ang.BaseObject2 = PL(kul, XZ), PL(None, XZ)
itv = qi(ang, A7.IMateInterval)
itv.UseInterval = True
itv.SetValueRange(PH_K, PH_N)
ang.ParamValue = PH0
print("  сопряжение угол кулисы (диапазон):", ang.Update(), itv.UseInterval, itv.MinValue, itv.MaxValue)
MC["угол"] = ang
for t in (XY, XZ, YZ):
    mate(f"ручка {t}", C3.mc_Coincidence, PL(grp, t), PL(kul, t), align=CO)
mate("камень XY", C3.mc_Coincidence, PL(kam, XY), PL(None, XY), align=CO)
mate("камень по кулисе", C3.mc_Coincidence, PL(kam, XZ), PL(kul, XZ), align=CO)
mate("ползун XY", C3.mc_Coincidence, PL(pol, XY), PL(None, XY), align=CO)
mate("ползун по направляющей", C3.mc_Distance, PL(pol, YZ), PL(None, YZ), value=E, align=CO)
mate("палец D", C3.mc_Concentric, PL(kam, OZ), PL(pol, OZ), align=CO)
top.RebuildModel(True)
for k, m in MC.items():
    if not m.Valid:
        print("  !! не выполнено:", k)


from math import atan2, degrees
origin = lambda c: c.Placement.GetOrigin()[-3:]
angle = lambda c: degrees(atan2(*c.Placement.GetVector(0)[-3:][1::-1]))       # угол оси x кулисы


def drive(ph):
    """угол кулисы задаётся сопряжением — диапазон на время проверки выключается"""
    itv.UseInterval = False
    ang.ParamValue = ph; ang.Update(); top.RebuildModel(True)


out = {"kin": [], "limit": []}
print("Проверка 1 — кинематика (угол задан сопряжением):")
for ph in (PH_K, 30.0, PH_Y, 50.0, PH_N):
    drive(ph)
    y = origin(pol)[1]; xk, yk = origin(kam)[:2]
    out["kin"].append([ph, angle(kul), y, yD(ph)])
    print(f"  φ = {ph:6.2f}° (кулиса {angle(kul):6.2f}°): ползун y = {y:8.3f}, e·tg φ = {yD(ph):8.3f}; камень ({xk:.3f}; {yk:.3f})")
print("Проверка 2 — диапазон: кулиса за пределами φк…φн, затем диапазон включается:")
for tgt in (15.0, 30.0, 70.0):
    drive(tgt)
    a0 = angle(kul)
    itv.UseInterval = True; itv.SetValueRange(PH_K, PH_N); ang.Update(); top.RebuildModel(True)
    out["limit"].append([tgt, a0, angle(kul), origin(pol)[1], bool(ang.Valid)])
    print(f"  кулиса на {a0:6.2f}° → {angle(kul):6.2f}°, ползун y = {origin(pol)[1]:8.3f}, сопряжение выполнено: {ang.Valid}")
drive(PH0)                                                     # сохраняется положение φу с включённым диапазоном
itv.UseInterval = True; itv.SetValueRange(PH_K, PH_N); ang.ParamValue = PH0; ang.Update(); top.RebuildModel(True)
print(f"положение при сохранении: {angle(kul):.2f}°, диапазон {itv.MinValue:.2f}…{itv.MaxValue:.2f}°")
doc.SaveAs(ASM)
print("сохранено:", ASM, os.path.getmtime(ASM))
json.dump(out, open(os.path.join(HERE, "assembly_check.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
