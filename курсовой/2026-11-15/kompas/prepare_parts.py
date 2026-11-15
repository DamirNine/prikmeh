# -*- coding: utf-8 -*-
"""Детали для сборки 13.11 из окончательных вариантов, проверенных в APM FEM (курсовой/2026-11-09/apm/Детали):
кулиса облегчённая 3 (9 пазов, фаска по контуру), ползун облегчённый (головка-колокол, R3), камень закрытый 2 (замкнутая
обойма, R1,5, фаски на отверстии, скругления пользователя), палец D; шайба, гайка, бутылка — из 2026-11-09/kompas;
стойка и кожух строятся здесь (python kompas_build.py stand cover). Копиям возвращаются рабочие цвета; пальцу — сталь 40Х
(APM, подшипниковая нагрузка: 192 МПа > [σ] = 142 для стали 45), камню — сталь 45 (закрытая обойма: 100 МПа < 142).
Массы — в parts_mass.json. Затем: python unhide_parts.py; python kompas_assembly.py
    python prepare_parts.py"""
import json, os, shutil, sys
from kompas_build import A5, A7, C, C3, FILES, HERE, PARTS_DIR, PIN_COLOR, ST3, ST45, app, k5, qi, rgb

APM = os.path.join(HERE, "..", "..", "2026-11-09", "apm", "Детали")
OLD = os.path.join(HERE, "..", "..", "2026-11-09", "kompas", "Детали")
ST40X = ("Сталь 40Х ГОСТ 4543-2016", 7.85)
SRC = {"kulisa": (os.path.join(APM, "УКП.01.001 Кулиса облегчённая 3 (APM).m3d"), "#2d3540", ST3),
       "polzun": (os.path.join(APM, "УКП.03.001 Ползун облегчённый (APM).m3d"), "#3a4049", ST3),
       "kamen": (os.path.join(APM, "УКП.02.001 Камень закрытый 2 (APM).m3d"), "#e8c99a", ST45),
       "pin": (os.path.join(APM, "УКП.02.002 Палец D (APM).m3d"), PIN_COLOR, ST40X)}


def find_doc(path):
    for i in range(app.Documents.Count):
        d = qi(app.Documents.Item(i), A7.IKompasDocument)
        if os.path.normcase(d.PathName) == os.path.normcase(path):
            return d
    return None


mj = os.path.join(HERE, "parts_mass.json")
mass = json.load(open(mj, encoding="utf-8"))
for k in ("washer", "nut", "bottle"):
    shutil.copy2(os.path.join(OLD, FILES[k]), os.path.join(PARTS_DIR, FILES[k]))
for k, (src, color, mat) in SRC.items():
    dst = os.path.join(PARTS_DIR, FILES[k])
    assert not find_doc(dst), ("деталь открыта в КОМПАСе — закройте", dst)
    shutil.copy2(src, dst)
    d = app.Documents.Open(dst, True, False)
    d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
    p5 = d5.GetPart(C3.pTop_Part)
    p5.SetMaterial(*mat)
    p5.SetAdvancedColor(rgb(color), 0.5, 0.6, 0.8, 0.8, 1.0, 0.5)
    p5.Update()
    top = qi(d, A7.IKompasDocument3D).TopPart
    bad = [f.Name for f in (qi(x, A7.IFeature7) for x in (qi(top, A7.IFeature7).SubFeatures(1, False, False) or ()))
           if not f.Valid and not f.Excluded]
    assert not bad, (k, bad)
    mass[k] = qi(top, A7.IMassInertiaParam7).Mass
    d.Save()
    d.Close(0)
    print(f"  {FILES[k]}: {mat[0]}, масса {mass[k]:.1f} г")
json.dump(mass, open(mj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("массы:", {k: round(v, 1) for k, v in mass.items()})
