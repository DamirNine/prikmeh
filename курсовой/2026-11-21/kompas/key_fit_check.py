# -*- coding: utf-8 -*-
"""Проверка: ключ S5 входит в гнездо установочного винта М10. Временная сборка (не сохраняется): винт (начало — центр
верхнего торца, винт к −z) и ключ длинным плечом в гнезде — ключ повёрнут на 180° вокруг x, конец плеча в 0,1 мм от дна
гнезда (глубина 5). Проверяется: (1) тела не пересекаются; (2) угловой люфт — поворот ключа вокруг оси винта, пока не
коснётся граней гнезда; (3) запас по размеру — какой «распухший» на печати ключ ещё входит (ключ с размером S+2δ
моделируется сдвигом в сторону на δ: при сдвиге на зазор грань упирается в грань).
    python key_fit_check.py"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A7, C, FILES, PARTS_DIR, SCR_HEX_S, SCR_HEX_T, app, qi

KEY = os.path.join(PARTS_DIR, "Ключ шестигранный S5 (печать).m3d")
S_KEY, L_LONG = 4.6, 75.0
doc = qi(app.Documents.Add(C.ksDocumentAssembly, False), A7.IKompasDocument3D)
top = doc.TopPart
scr = top.Parts.AddFromFile(os.path.join(PARTS_DIR, FILES["screw"]), True, False)
key = top.Parts.AddFromFile(KEY, True, False)
scr.Fixed = True; scr.Update()
key.Fixed = False


def place(dx=0.0, ang=0.0):
    pl = key.Placement
    pl.InitByMatrix3D([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
    pl.Rotate(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 180.0)                     # длинное плечо — к −z, в гнездо
    if ang:
        pl.Rotate(0.0, 0.0, 0.0, 0.0, 0.0, 1.0, ang)                   # поворот вокруг оси плеча (ось гнезда)
    pl.SetOrigin(dx, 0.0, -SCR_HEX_T + 0.1 + L_LONG)                    # конец плеча — в 0,1 мм над дном гнезда
    key.UpdatePlacement(False)
    top.RebuildModel(True)
    b = lambda p: [qi(x, A7.IBody7) for x in (lambda r: r if isinstance(r, tuple) else (r,))(qi(p, A7.IFeature7).ResultBodies)]
    return any(x.CheckIntersectionWithBody(y, False) for x in b(scr) for y in b(key))


print(f"гнездо винта S{SCR_HEX_S:g} × {SCR_HEX_T:g}, ключ S{S_KEY} — расчётный зазор по граням {(SCR_HEX_S - S_KEY) / 2:.2f} мм на сторону")
print("  ключ в гнезде соосно:", "ПЕРЕСЕЧЕНИЕ" if place() else "входит, пересечений нет")
a = 0.0
while a < 30 and not place(ang=a + 0.25):
    a += 0.25
print(f"  угловой люфт: ±{a:.2f}° (дальше ключ упирается в грани гнезда и крутит винт)")
d = 0.0
while d < 0.5 and not place(dx=d + 0.01):
    d += 0.01
print(f"  сдвиг вбок до касания: {d:.2f} мм — столько на сторону может «съесть» печать (гнездо уже + ключ толще)")
doc.Close(0)
