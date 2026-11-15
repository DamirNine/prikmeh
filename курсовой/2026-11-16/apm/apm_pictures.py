# -*- coding: utf-8 -*-
"""Картинки для отчёта APM FEM (как apm_prep.py 09.11: светлая деталь, изометрия, 200 dpi) по рабочим деталям 16.11 —
направляющая (УКП.00.002, окончательная форма) и палец D (резьба М10 × 1,5); рисуются временные копии в _копии/.
Направляющей в рабочей модели ставится материал сталь 45 ГОСТ 1050-2013 ([σ] = 142 МПа; для Ст3 [σ] = 98 МПа < 136 МПа
по APM): сохраняется через API5 SaveAs (IKompasDocument.Save у этой детали молча не сохраняет).
Исходный камень (обойма с губками, 09.11) — чистая картинка из 2026-11-09/kompas/Детали (в отчёте 09.11 была картинка
APM-копии с сохранённой картой напряжений).
    python apm_pictures.py [--pin | --kamen]   (только картинка пальца / исходного камня)"""
import os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kompas"))
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A5, A7, C, C3, FILES, PARTS_DIR, ST45, app, k5, qi

PIC = os.path.join(HERE, "Картинки"); os.makedirs(PIC, exist_ok=True)
TMP = os.path.join(HERE, "_копии"); os.makedirs(TMP, exist_ok=True)
LIGHT = 0xccc1b7


def open5(path):
    d = app.Documents.Open(path, True, False)
    return d, A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))


def picture(key, png, dpi=200, src=None):
    """key — деталь рабочей модели; src — другой файл детали (тогда key — только имя копии)"""
    src = src or os.path.join(PARTS_DIR, FILES[key])
    dst = os.path.join(TMP, os.path.basename(src))
    shutil.copy2(src, dst)
    d, d5 = open5(dst)
    p5 = d5.GetPart(C3.pTop_Part)
    p5.SetAdvancedColor(LIGHT, 0.5, 0.6, 0.8, 0.8, 1.0, 0.5)
    o = p5.GetDefaultEntity(C3.o3d_pointCS); o.hidden = True; o.Update()
    top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
    sks = qi(top, A7.IModelContainer).Sketchs
    for i in range(sks.Count):
        s = sks.Item(i); s.Hidden = True; s.Update()
    for x in qi(top, A7.IFeature7).SubFeatures(1, False, False) or ():     # винтовые линии резьбы
        o = qi(x, A7.IModelObject)
        if o.ModelObjectType == C3.o3d_cylindricSpiral:
            o.Hidden = True; o.Update()
    p5.Update()
    coll = d5.GetViewProjectionCollection()
    iso = next(coll.GetByIndex(i) for i in range(coll.GetCount()) if "зометр" in coll.GetByIndex(i).name)
    iso.SetCurrent()
    d5.ZoomPrevNextOrAll(2)
    rp = d5.RasterFormatParam(); rp.Init()
    rp.format, rp.colorType, rp.extResolution, rp.extScale, rp.onlyThinLine = C.ksRasterFormatPNG, 3, dpi, 1.0, False
    out = os.path.join(PIC, png)
    assert d5.SaveAsToRasterFormat(out, rp), out
    d5.SaveAs(dst)                                 # сохранённый документ закрывается без вопросов (изменённый — роняет КОМПАС)
    d.Close(0)
    print("  картинка:", png)


if "--kamen" in sys.argv:
    picture("kamen", "камень_1_деталь.png", dpi=600,
            src=os.path.join(HERE, "..", "..", "2026-11-09", "kompas", "Детали", "УКП.02.001 Камень.m3d"))
    sys.exit()
if "--pin" not in sys.argv:
    # материал направляющей
    path = os.path.join(PARTS_DIR, FILES["guide"])
    d, d5 = open5(path)
    p5 = d5.GetPart(C3.pTop_Part)
    p5.SetMaterial(*ST45)
    p5.Update()
    d5.SaveAs(path)
    top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
    print(f"  направляющая: {qi(top, A7.IMassInertiaParam7).Mass:.1f} г, материал — {ST45[0]}")
    d.Close(0)
    d, d5 = open5(path)
    mat = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart.Material
    print("  после повторного открытия:", mat)
    assert mat.startswith("Сталь 45"), mat
    d.Close(0)

if "--pin" not in sys.argv:
    picture("guide", "направляющая_3_новая.png")
picture("pin", "палец_1_деталь.png", dpi=600)          # палец мал — картинка по габариту, поэтому dpi выше
