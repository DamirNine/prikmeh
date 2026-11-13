# -*- coding: utf-8 -*-
"""Картинки для инструкции по сборке (img/*.png) — из сборки ../kompas/УКП.00.000 Укупориватель.a3d.
Каждый кадр: показаны только нужные компоненты, новая деталь шага подсвечена (цвет компонента в сборке меняется только
на время съёмки; сборка закрывается без сохранения). Угол кулисы и сдвиг кожуха задаются через их сопряжения.
Детали отдельно не открываются: КОМПАС (v25) теряет документ детали, если открыть её при открытой сборке.
    python make_images.py"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kompas"))
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A5, A7, C, C3, PH_K, PH_N, app, k5, qi, rgb
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

ASM = os.path.abspath(os.path.join(HERE, "..", "kompas", "УКП.00.000 Укупориватель.a3d"))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
HL = rgb("#ffb000")                                   # подсветка новой детали — янтарный

docs = [qi(app.Documents.Item(i), A7.IKompasDocument) for i in range(app.Documents.Count) if app.Documents.Item(i) is not None]
doc = next((d for d in docs if os.path.normcase(d.PathName) == os.path.normcase(ASM)), None)
if doc is not None:
    doc.Close(0)
doc = app.Documents.Open(ASM, True, False)
doc.Active = True
time.sleep(2)
d5 = A5.ksDocument3D(k5.TransferInterface(doc, C.ksAPI5Auto, 0))
top = qi(doc, A7.IKompasDocument3D).TopPart
KEYS = {"Стойка": "stand", "Кулиса": "kulisa", "Камень": "kamen", "Палец": "pin", "Ползун": "polzun", "Шайба": "washer",
        "Гайка": "nut", "Кожух": "cover", "Бутылка": "bottle"}
comp = {}
for i in range(top.Parts.Count):
    p = qi(top.Parts.Item(i), A7.IPart7)
    comp[next(v for k, v in KEYS.items() if p.Name.startswith(k))] = p
assert len(comp) == 9, list(comp)

ang = cov = None
mc = top.MateConstraints
for i in range(mc.Count):
    m = qi(mc.Item(i), A7.IMateConstraint3D)
    if m.ConstraintType == C3.mc_Angle:
        ang = m
    elif m.ConstraintType == C3.mc_Distance and qi(m, A7.IMateInterval).UseInterval and qi(m, A7.IMateInterval).MaxValue > 100:
        cov = m
assert ang and cov, "не найдены сопряжения угла кулисы и сдвига кожуха"


def set_mate(m, v):
    qi(m, A7.IMateInterval).UseInterval = False
    m.ParamValue = v
    m.Update()
    top.RebuildModel(True)


base_color = {k: qi(p, A7.IColorParam7).Color for k, p in comp.items()}


def raster(path, dpi):
    rp = d5.RasterFormatParam()
    rp.Init()
    rp.format, rp.colorType, rp.extResolution, rp.extScale, rp.onlyThinLine = C.ksRasterFormatPNG, 3, dpi, 1.0, False
    assert d5.SaveAsToRasterFormat(path, rp), path
    im = Image.open(path).convert("RGB")
    bb = Image.eval(im.convert("L"), lambda v: 255 if v < 250 else 0).getbbox()
    assert bb, ("пустой кадр", path)
    return im, bb


def frame(name, visible, new=(), phi=41.63, cover=0.0, focus=None, view=None, crop_pad=20):
    """focus — крупный план: тот же вид всей видимой сборки, обрезанный вокруг деталей focus (с полями)"""
    set_mate(ang, phi)
    set_mate(cov, cover)
    for k, p in comp.items():
        o = qi(p, A7.IModelObject)
        o.Hidden = k not in visible
        cp = qi(p, A7.IColorParam7)
        cp.Color = HL if k in new else base_color[k]
        o.Update()
    top.RebuildModel(True)
    coll = d5.GetViewProjectionCollection()
    next(coll.GetByIndex(i) for i in range(coll.GetCount()) if "зометр" in coll.GetByIndex(i).name).SetCurrent()
    if view:
        vpm = qi(k5.TransferInterface(d5, C.ksAPI7Dual, 0), A7.IKompasDocument3D1).ViewProjectionManager
        vpm.SetMatrix3D(view, vpm.Scale)
    d5.ZoomPrevNextOrAll(2)
    out = os.path.join(IMG, name + ".png")
    # КОМПАС сохраняет картинку по габариту видимых деталей в масштабе (пиксели ∝ dpi), не по окну: сначала пробный кадр
    # 100 dpi, по нему — область кадра и dpi, чтобы нужное заняло ~1300 пикселей
    im0, bb = raster(out, 100)
    if focus:                                     # крупный план: детали focus временно пурпурные — их область на том же кадре
        for k in focus:
            qi(comp[k], A7.IColorParam7).Color = rgb("#ff00ff"); qi(comp[k], A7.IModelObject).Update()
        top.RebuildModel(True)
        mk, _ = raster(out, 100)
        px = mk.load()
        mask = Image.new("L", mk.size, 0); mp = mask.load()
        for y in range(mk.height):
            for x in range(mk.width):
                r, g, b_ = px[x, y]
                if r > 110 and b_ > 110 and g < 0.6 * min(r, b_):
                    mp[x, y] = 255
        fb = mask.getbbox()
        assert fb, ("нет деталей крупного плана", name)
        for k in focus:
            qi(comp[k], A7.IColorParam7).Color = HL if k in new else base_color[k]; qi(comp[k], A7.IModelObject).Update()
        top.RebuildModel(True)
        m = 0.3 * max(fb[2] - fb[0], fb[3] - fb[1])
        bb = (fb[0] - m, fb[1] - m, fb[2] + m, fb[3] + m)
    else:
        bb = (bb[0] - 4, bb[1] - 4, bb[2] + 4, bb[3] + 4)
    dpi = 100 * 1300 / max(bb[2] - bb[0], bb[3] - bb[1])
    dpi = min(dpi, 1500, 100 * (1.2e8 / (im0.width * im0.height)) ** 0.5)
    im, _ = raster(out, dpi)
    k = im.width / im0.width
    im = im.crop((max(int(bb[0] * k), 0), max(int(bb[1] * k), 0), min(int(bb[2] * k), im.width), min(int(bb[3] * k), im.height)))
    im.thumbnail((1300, 1300))
    im.save(out, optimize=True)
    print(f"  {name}: {im.size}")


ALL = set(comp)
MECH = ALL - {"bottle"}
if __name__ == "__main__":
    only = sys.argv[1:]
    F = [  # имя, видимые, новые, угол, сдвиг кожуха[, крупный план]
        ("00_общий_вид", ALL, (), 41.63, 0.0),
        ("01_без_кожуха", ALL - {"cover"}, (), 41.63, 0.0),
        ("02_рукоять_вверху", ALL - {"cover"}, (), PH_N, 0.0),
        ("03_рукоять_внизу", ALL - {"cover"}, (), PH_K, 0.0),
        ("10_стойка", {"stand"}, (), 41.63, 0.0),
        ("11_палец_в_камень", {"kamen", "pin"}, ("pin",), 41.63, 0.0),
        ("12_камень_на_кулису", {"kulisa", "kamen", "pin"}, ("kamen", "pin"), 41.63, 0.0, {"kamen", "pin"}),
        ("13_кулиса_на_ось", {"stand", "kulisa", "kamen", "pin"}, ("kulisa", "kamen", "pin"), 41.63, 0.0),
        ("14_ползун", {"stand", "kulisa", "kamen", "pin", "polzun"}, ("polzun",), 41.63, 0.0, {"polzun", "kamen"}),
        ("15_шайба_гайка", MECH - {"cover"}, ("washer", "nut"), 41.63, 0.0, {"washer", "nut", "pin", "kamen"}),
        ("16_кожух_надевание", MECH, ("cover",), 41.63, 90.0),
        ("17_кожух_на_месте", MECH, ("cover",), 41.63, 0.0),
        ("18_бутылка", ALL, ("bottle",), PH_N, 0.0),
    ] + [(f"p_{k}", {k}, (), 41.63, 0.0) for k in ("stand", "kulisa", "kamen", "pin", "polzun", "washer", "nut", "cover")]
    for name, vis, new, ph, dz, *fc in F:
        if not only or name in only:
            frame(name, vis, new, ph, dz, fc[0] if fc else None)
    doc.Close(0)                                                  # подсветка и скрытие — только для съёмки
    print("готово, сборка закрыта без сохранения")
