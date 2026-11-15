# -*- coding: utf-8 -*-
"""Подготовка направляющей УКП.00.002 к расчёту в APM FEM (как apm_prep.py 09.11; клики в APM делает пользователь):
  — зона контакта с бруском ползуна на внутренней грани правой планки при φу: y = yD(φу) ± 20, z 26…42 (брусок 40 × 16) —
    отделена линиями разъёма плоскостями y = yD − 20, y = yD + 20, z = 42; на неё прикладывается сила R30N = 1671 Н (+x);
  — грани пластины, лежащие в выемке стойки (левая, правая, нижняя), отделены от граней кронштейнов и планок плоскостью
    z = 0 (они в одной плоскости и сливались в одну грань) — на них и на заднюю грань пластины ставится закрепление;
  — копия светлая, эскизы и начало координат скрыты; картинка apm/Картинки/направляющая_1_деталь.png.
    python apm_prep_guide.py ["УКП.00.002 Направляющая 2 (APM).m3d" направляющая_2_деталь.png]
Свежая копия делается из kompas/Детали, если файла ещё нет."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kompas"))
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A5, A7, C, C3, E, GD_PL_T, GD_X0, GD_X1, GD_Z0, PH_Y, Y_BOT, GD_PL_Y1, app, k5, qi, yD

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else "УКП.00.002 Направляющая (APM).m3d")
PNG = sys.argv[2] if len(sys.argv) > 2 else "направляющая_1_деталь.png"
if not os.path.exists(PATH):
    import shutil
    shutil.copy2(os.path.join(HERE, "..", "kompas", "Детали", "УКП.00.002 Направляющая.m3d"), PATH)
PIC = os.path.join(HERE, "Картинки"); os.makedirs(PIC, exist_ok=True)
X_IN = E + 12.5                                   # внутренняя грань правой планки (к ползуну)
Y0, Y1, Z1 = yD(PH_Y) - 20, yD(PH_Y) + 20, GD_Z0 + 16     # брусок ползуна 40 × 16 при φу
LIGHT = 0xccc1b7


def find_doc(path):
    for i in range(app.Documents.Count):
        d = qi(app.Documents.Item(i), A7.IKompasDocument)
        if os.path.normcase(d.PathName) == os.path.normcase(path):
            return d
    return None


d = find_doc(PATH) or app.Documents.Open(PATH, True, False)
d.Active = True
d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
p5 = d5.GetPart(C3.pTop_Part)
top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
N_SPLIT = qi(top, A7.IAuxiliaryGeomContainer).SplitLines.Count   # 0 — свежая копия; 6 — разъёмы уже построены (повторный запуск)
assert N_SPLIT in (0, 6), ("часть линий разъёма уже есть — берите свежую копию детали", N_SPLIT)


def face_at(x, y, z):
    objs = [qi(o, A7.IModelObject) for o in (top.FindObjectsByPoint(x, y, z, True) or ())]
    fs = [o for o in objs if o.ModelObjectType == C3.o3d_face]
    assert len(fs) == 1, ((x, y, z), len(fs))
    return fs[0]


def area(f):
    return qi(f, A7.IFace).GetArea(1)             # 1 — мм²


def plane(base, offset):
    """смещённая плоскость (скрытая) или сама базовая при offset = 0"""
    if abs(offset) < 1e-9:
        return qi(k5.TransferInterface(p5.GetDefaultEntity(base), C.ksAPI7Dual, 0), A7.IModelObject)
    pl = p5.NewEntity(C3.o3d_planeOffset)
    pd = pl.GetDefinition()
    pd.SetPlane(p5.GetDefaultEntity(base))
    pd.offset, pd.direction = abs(offset), offset > 0
    pl.hidden = True
    pl.Create()
    return qi(k5.TransferInterface(pl, C.ksAPI7Dual, 0), A7.IModelObject)


def split(name, cut, at):
    """разрезать грань, проходящую через точку at, плоскостью cut"""
    sl = qi(top, A7.IAuxiliaryGeomContainer).SplitLines.Add()
    sl.CutObjects = [cut]
    sl.Faces = [face_at(*at)]
    assert sl.Update() and sl.Valid, ("линия разъёма не построена", name)
    sl.Name = name
    sl.Update()


ZC = (X_IN, (Y0 + Y1) / 2, (GD_Z0 + Z1) / 2)      # точка в середине зоны контакта
zm = -GD_PL_T / 2                                 # середина толщины пластины
if N_SPLIT == 0:
    split("Зона ползуна: низ", plane(C3.o3d_planeXOZ, Y0), ZC)
    split("Зона ползуна: верх", plane(C3.o3d_planeXOZ, Y1), ZC)
    split("Зона ползуна: перед", plane(C3.o3d_planeXOY, Z1), ZC)
    for nm, at in (("Пластина: левая грань", (GD_X0, (Y_BOT + GD_PL_Y1) / 2, 10.0)),
                   ("Пластина: правая грань", (GD_X1, (Y_BOT + GD_PL_Y1) / 2, 10.0)),
                   ("Пластина: нижняя грань", (GD_X0 + 3, Y_BOT, 10.0))):
        split(nm, plane(C3.o3d_planeXOY, 0.0), at)

# проверка площадей: зона 40 × 16, грани пластины 32,75 × 6 и 37 × 6, задняя 37 × 32,75
checks = {"зона ползуна (сила 1671 Н, +x)": (face_at(*ZC), 40 * 16),
          "пластина: задняя грань": (face_at(E, -30, -GD_PL_T), (GD_X1 - GD_X0) * (GD_PL_Y1 - Y_BOT)),
          "пластина: левая грань": (face_at(GD_X0, -30, zm), (GD_PL_Y1 - Y_BOT) * GD_PL_T),
          "пластина: правая грань": (face_at(GD_X1, -30, zm), (GD_PL_Y1 - Y_BOT) * GD_PL_T),
          "пластина: нижняя грань": (face_at(E, Y_BOT, zm), (GD_X1 - GD_X0) * GD_PL_T)}
for k, (f, a0) in checks.items():
    a = area(f)
    assert abs(a - a0) < 0.05, (k, a, a0)
    print(f"  {k}: {a:.1f} мм²")

# светлая копия без эскизов и начала координат (как копии 09.11)
p5.SetAdvancedColor(LIGHT, 0.5, 0.6, 0.8, 0.8, 1.0, 0.5)
o = p5.GetDefaultEntity(C3.o3d_pointCS); o.hidden = True; o.Update()
sks = qi(top, A7.IModelContainer).Sketchs
for i in range(sks.Count):
    s = sks.Item(i); s.Hidden = True; s.Update()
p5.Update()
d.Save()
assert not d.Changed
# картинка: изометрия
coll = d5.GetViewProjectionCollection()
iso = next(coll.GetByIndex(i) for i in range(coll.GetCount()) if "зометр" in coll.GetByIndex(i).name)
iso.SetCurrent()
d5.ZoomPrevNextOrAll(2)
rp = d5.RasterFormatParam(); rp.Init()
rp.format, rp.colorType, rp.extResolution, rp.extScale, rp.onlyThinLine = C.ksRasterFormatPNG, 3, 200, 1.0, False
png = os.path.join(PIC, PNG)
assert d5.SaveAsToRasterFormat(png, rp), png
print("сохранено:", PATH, "| картинка:", png)
