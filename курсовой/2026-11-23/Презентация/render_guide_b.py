# -*- coding: utf-8 -*-
"""23.11 (Корнеев: на слайде «до/после МКЭ» направляющая — нынешняя: отверстие в горизонтальной полке, без боковых планок):
рендер УКП.00.002-01 «Направляющая (без планок)» (2026-11-22/Новые детали, v25) → fig/фэм_после_направляющая_Б.png.
Тёмные рендеры «после» (кулиса, ползун) осветляются → fig/фэм_после_*_светл.png, чтобы были видны отверстия."""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
KURS = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image

FIG = os.path.join(HERE, "fig")


def lighten(name):
    im = np.asarray(Image.open(os.path.join(FIG, f"фэм_после_{name}.png")).convert("RGB")).astype(float)
    part = (255 - im).max(axis=2) > 18
    L = im.mean(axis=2)
    lo, hi = np.percentile(L[part], 4), np.percentile(L[part], 97)
    t = np.clip((L - lo) / (hi - lo), 0, 1)[..., None]
    dark, light = np.array([62, 84, 112]), np.array([226, 233, 242])           # сталь: тени → блики
    out = np.where(part[..., None], dark + (light - dark) * t, im)
    Image.fromarray(out.astype(np.uint8)).save(os.path.join(FIG, f"фэм_после_{name}_светл.png"))


if __name__ == "__main__":
    for n in ("кулиса", "ползун"):
        lighten(n)
    if "--kompas" in sys.argv:
        import render_fem_parts_lib as R
        src = os.path.join(KURS, "2026-11-22", "Новые детали", "КОМПАС v25", "УКП.00.002-01 Направляющая (без планок).m3d")
        print("масса", R.render(src, os.path.join(FIG, "фэм_после_направляющая_Б.png")))
