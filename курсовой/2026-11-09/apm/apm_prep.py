# -*- coding: utf-8 -*-
"""Подготовка деталей к расчёту в APM FEM (клики в APM делает пользователь):
  — копии деталей в apm/Детали (APM создаёт рядом с деталью свой .apmf — рабочие детали сборки не трогаем);
  — на копии кулисы зона контакта с камнем при φу (20 мм на нижней грани полосы) отделена линией разъёма — на неё
    прикладывается реакция камня;
  — изометрия исходной детали в PNG: apm/Картинки/<деталь>_1_деталь.png.
    python apm_prep.py kulisa polzun        (ключи: kulisa, polzun, kamen, pin)"""
import os, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kompas"))
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A5, A7, C, C3, FILES, PARTS_DIR, app, k5, qi
from kompas_build import Sketch2D

HERE = os.path.dirname(os.path.abspath(__file__))
DET, PIC = os.path.join(HERE, "Детали"), os.path.join(HERE, "Картинки")
os.makedirs(DET, exist_ok=True); os.makedirs(PIC, exist_ok=True)
NAMES = {"kulisa": "кулиса", "polzun": "ползун", "kamen": "камень", "pin": "палец"}
LOD_Y, LK = 16.76, 20.0                              # камень при φу: центр в 16,76 мм от O, длина контакта 20 мм


def find_doc(path):
    for i in range(app.Documents.Count):
        d = qi(app.Documents.Item(i), A7.IKompasDocument)
        if os.path.normcase(d.PathName) == os.path.normcase(path):
            return d
    return None


def open_doc(path):
    d = find_doc(path) or app.Documents.Open(path, True, False)
    d.Active = True
    return d


LIGHT = 0xccc1b7                                     # светло-серый #b7c1cc (BGR) — только у копий для APM и картинок
# ракурс — матрица вида 4 × 4 по строкам: ось X экрана, ось Y экрана, направление на наблюдателя, сдвиг (как
# IViewProjectionManager.Matrix3D); None — стандартная изометрия (взгляд сверху: (0,577; 0,577; 0,577))
A_, B_ = 0.5773502691896258, 0.7071067811865476
VIEW = {"polzun": (B_, 0, -B_, 0, A_ * B_, 2 * A_ * B_, A_ * B_, 0, A_, -A_, A_, 0, 0, 0, 0, 1)}   # снизу: видна горловина


def prettify(path):
    """копия для APM: светлый цвет, без значка начала координат"""
    d = open_doc(path)
    p5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0)).GetPart(C3.pTop_Part)
    p5.SetAdvancedColor(LIGHT, 0.5, 0.6, 0.8, 0.8, 1.0, 0.5)
    o = p5.GetDefaultEntity(C3.o3d_pointCS)
    o.hidden = True
    o.Update()
    top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
    sks = qi(top, A7.IModelContainer).Sketchs                   # эскизы (в т. ч. линии разъёма) на картинке не нужны
    for i in range(sks.Count):
        s = sks.Item(i)
        s.Hidden = True
        s.Update()
    p5.Update()
    d.Save()


def picture(path_m3d, png, view=None):
    """изометрия (или свой ракурс), показать всё, PNG 200 dpi"""
    d = open_doc(path_m3d)
    d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
    coll = d5.GetViewProjectionCollection()
    iso = next(coll.GetByIndex(i) for i in range(coll.GetCount()) if "зометр" in coll.GetByIndex(i).name)
    iso.SetCurrent()
    if view:                                                     # свой ракурс — матрицей вида
        vpm = qi(k5.TransferInterface(d5, C.ksAPI7Dual, 0), A7.IKompasDocument3D1).ViewProjectionManager
        vpm.SetMatrix3D(view, vpm.Scale)
    d5.ZoomPrevNextOrAll(C.ksZoomAll) if hasattr(C, "ksZoomAll") else d5.ZoomPrevNextOrAll(2)
    rp = d5.RasterFormatParam()
    rp.Init()
    rp.format, rp.colorType, rp.extResolution, rp.extScale, rp.onlyThinLine = C.ksRasterFormatPNG, 3, 200, 1.0, False
    assert d5.SaveAsToRasterFormat(png, rp), png
    print("  картинка:", os.path.relpath(png, HERE))


def face_at(top, x, y, z):
    objs = [qi(o, A7.IModelObject) for o in (top.FindObjectsByPoint(x, y, z, True) or ())]
    fs = [o for o in objs if o.ModelObjectType == C3.o3d_face]
    assert len(fs) == 1, ((x, y, z), len(fs))
    return fs[0]


def split_kulisa(path):
    """линия разъёма на нижней грани полосы (y = −9): зона контакта с камнем x = 6,76…26,76"""
    d = open_doc(path)
    d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
    p5 = d5.GetPart(C3.pTop_Part)
    sk = p5.NewEntity(C3.o3d_sketch)
    sd = sk.GetDefinition()
    sd.SetPlane(p5.GetDefaultEntity(C3.o3d_planeXOZ))           # эскиз XOZ: (u, v) = (x, −z)
    sk.Create()
    d2 = sd.BeginEdit()
    s2 = Sketch2D(d2)
    for x in (LOD_Y - LK / 2, LOD_Y + LK / 2):
        seg = d2.ksLineSeg(x, 2.0, x, -10.0, 1)
        s2.cons(seg, C.ksCFixedPoint, 0); s2.cons(seg, C.ksCFixedPoint, 1)
    sd.EndEdit()
    top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
    low = face_at(top, LOD_Y, -9.0, 4.0)
    sl = qi(top, A7.IAuxiliaryGeomContainer).SplitLines.Add()
    sl.Sketch = qi(k5.TransferInterface(sk, C.ksAPI7Dual, 0), A7.ISketch)
    sl.Faces = [low]
    assert sl.Update() and sl.Valid, "линия разъёма не построена"
    sl.Name = "Зона контакта с камнем (φу)"
    sl.Update()
    zone = face_at(top, LOD_Y, -9.0, 4.0)                        # теперь — отдельная грань 20 × 8
    try:
        a = qi(zone, A7.IFace).Area
    except Exception:
        a = None
    print(f"  кулиса: зона контакта отделена, площадь грани {a:.1f} мм² (надо {LK * 8:.0f})" if a else "  кулиса: зона отделена")
    d.Save()
    assert not d.Changed


if __name__ == "__main__":
    for key in sys.argv[1:]:
        src = os.path.join(PARTS_DIR, FILES[key])
        dst = os.path.join(DET, FILES[key].replace(".m3d", " (APM).m3d"))
        print(NAMES[key] + ":")
        if not os.path.exists(dst):                                  # новая копия; если уже есть — разъём не повторяем
            shutil.copy2(src, dst)
            if key == "kulisa":
                split_kulisa(dst)
        prettify(dst)
        print("  копия для APM:", os.path.relpath(dst, HERE))
        picture(dst, os.path.join(PIC, f"{NAMES[key]}_1_деталь.png"), VIEW.get(key))
