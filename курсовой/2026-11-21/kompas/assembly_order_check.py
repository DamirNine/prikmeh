# -*- coding: utf-8 -*-
"""21.11: можно ли собрать механизм с направляющей-«стулом» (полка с отверстием под шток) и разрезанным ползуном —
проверка путей установки деталей в новом порядке (IBody7.CheckIntersectionWithBody, касания не считаются):
  1) ползун (верх) опускается сверху между планками, шток проходит в отверстие полки — к этому моменту стоят стойка,
     кулиса с камнем (без пальца), направляющая и винт М10;
  2) палец D вставляется спереди через отверстие ползуна в камень;
  3) головка подводится снизу на хвостовик штока.
Деталь «отпускается» исключением одного своего сопряжения (остальные держат её на пути), положение задаётся сдвигом
начала координат. Сборка закрывается без сохранения.
    python assembly_order_check.py"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A7, C3, PH_Y, app, qi

ASM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "УКП.00.000-01 Укупориватель (направляющая без планок).a3d"
                   if os.environ.get("UKP_VAR") == "B" else "УКП.00.000 Укупориватель.a3d")      # 21.11: вариант B
doc = qi(app.Documents.Open(ASM, True, False), A7.IKompasDocument3D)
top = doc.TopPart
parts = {qi(top.Parts.Part(i), A7.IPart7).Name: qi(top.Parts.Part(i), A7.IPart7) for i in range(top.Parts.Count)}
P = lambda prefix: next(p for n, p in parts.items() if n.startswith(prefix))
bodies = lambda p: [qi(x, A7.IBody7) for x in (lambda b: () if b is None else (b if isinstance(b, tuple) else (b,)))(qi(p, A7.IFeature7).ResultBodies)]
mates = top.MateConstraints
ms = [qi(mates.MateConstraint3D(i), A7.IMateConstraint3D) for i in range(mates.Count)]


def owner(o):
    try:
        return qi(o, A7.IModelObject).Part.Name
    except Exception:
        return None


def between(a, b, kind):
    """единственное сопряжение типа kind между деталями a и b (IPart7)"""
    r = [m for m in ms if m.ConstraintType == kind and {str(owner(m.BaseObject1)), str(owner(m.BaseObject2))} == {a.Name, b.Name}]
    assert len(r) == 1, (a.Name, b.Name, len(r))
    return r[0]


def release(m):
    f = qi(m, A7.IFeature7)
    f.Excluded = True
    m.Update()


def path(name, part, axis, shifts, obstacles):
    """part сдвигается вдоль оси axis (0 — x, 1 — y, 2 — z) на shifts от собранного положения; пересечения с obstacles"""
    pl = part.Placement
    o0 = list(pl.GetOrigin()[-3:])
    hits = []
    for s in shifts:
        o = list(o0)
        o[axis] += s
        pl.SetOrigin(*o)
        part.UpdatePlacement(True)
        part.Update()
        for ob in obstacles:
            if any(a.CheckIntersectionWithBody(b, False) for a in bodies(part) for b in bodies(ob)):
                hits.append((s, ob.Name))
    pl.SetOrigin(*o0)
    part.UpdatePlacement(True)
    print(f"{name}: сдвиги {shifts[0]:g}…{shifts[-1]:g} мм — " + ("пересечений нет" if not hits else f"ПЕРЕСЕЧЕНИЯ {hits[:12]}"))
    return hits


ang = next(m for m in ms if m.ConstraintType == C3.mc_Angle)
qi(ang, A7.IMateInterval).UseInterval = False
ang.ParamValue = PH_Y
ang.Update()
top.RebuildModel(True)

stand, kulisa, kamen, guide, screw = P("Стойка"), P("Кулиса"), P("Камень"), P("Направляющая"), P("Винт")
polzun, head, pin = P("Ползун"), P("Головка"), P("Палец")
bad = []
# 1) ползун сверху: отпускаем «ползун на пальце D» (концентричность) — по планкам и по x его держат остальные сопряжения;
#    головка, шайба, гайка, палец ещё не стоят — головка пока «едет» с ползуном, но в проверке не участвует
release(between(polzun, pin, C3.mc_Concentric))
top.RebuildModel(True)
# контроль проверки: ползун на 40 мм ниже рабочего положения обязан упереться брусом в полку направляющей
ctrl = path("контроль: ползун на 40 мм ниже (должен упереться в полку)", polzun, 1, [-40.0], [guide])
assert ctrl, "сдвиг детали не работает — проверка недостоверна"
bad += path("1) ползун сверху между планками, шток в полку", polzun, 1, [float(s) for s in range(0, 142, 2)],
            [stand, kulisa, kamen, guide, screw])
# 2) палец D спереди: отпускаем «заподлицо с задней гранью обоймы» — ось держит концентричность с камнем
pin_flush = next(m for m in ms if m.ConstraintType == C3.mc_Coincidence and
                 {str(owner(m.BaseObject1)), str(owner(m.BaseObject2))} == {pin.Name, kamen.Name} and
                 qi(m.BaseObject1, A7.IModelObject).ModelObjectType == C3.o3d_face)
release(pin_flush)
top.RebuildModel(True)
bad += path("2) палец D спереди через ползун в камень", pin, 2, [float(s) for s in range(0, 72, 2)],
            [stand, kulisa, kamen, guide, screw, polzun])
# 3) головка снизу: отпускаем её сопряжение по y с ползуном
head_y = next(m for m in ms if m.ConstraintType == C3.mc_Coincidence and
              {str(owner(m.BaseObject1)), str(owner(m.BaseObject2))} == {head.Name, polzun.Name} and
              qi(m.BaseObject1, A7.IModelObject).ModelObjectType == C3.o3d_planeXOZ)
release(head_y)
top.RebuildModel(True)
bad += path("3) головка снизу на хвостовик", head, 1, [-float(s) for s in range(0, 62, 2)],
            [stand, kulisa, kamen, guide, screw, polzun, pin])
print("Собирается:", "да" if not bad else "НЕТ")
doc.Close(0)
