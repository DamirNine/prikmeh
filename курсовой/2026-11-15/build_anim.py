# -*- coding: utf-8 -*-
"""3D-анимация сборки укупоривателя — один самостоятельный HTML-файл (без интернета и без установки):
геометрия деталей — из STL комплекта 13.11 (в координатах самих деталей), положения в сборке — как в kompas_assembly.py
(PLACE), three.js и OrbitControls встроены в файл из папки lib/.
    python build_anim.py"""
import base64, json, os
from math import tan, radians
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "..", "2026-11-13", "Укупориватель — печать и сборка", "Детали для печати")
OUT = os.path.join(HERE, "3D-сборка укупоривателя.html")
RJ = json.load(open(os.path.join(HERE, "..", "2026-11-04", "calc_v21.json"), encoding="utf-8"))

# ---------------- размеры и положения — те же числа, что в 2026-11-13/kompas/kompas_build.py и kompas_assembly.py
E = 12.53
PH_N, PH_K, PH0 = RJ["phi_n"], RJ["phi_k"], RJ["phi_y"]
Z_ST, Y_ST0 = -34.0, -325.25                      # передняя грань стойки; верх основания = дно бутылки
Z_KUL, Z_KAM, Z_PIN = -21.5, -9.0, -13.0          # начала деталей по z в сборке
PIN_L1, WASHER_S, NUT_M = 21.5, 1.6, 6.5
Z_WASHER = Z_PIN + PIN_L1
BOTTLE_H, BOTTLE_R = 226.5, 30.2
CAP_TOP, CAP_SKIRT, R_OBZH, R_K = 0.94, 5.4, 14.3, 16.05

PARTS = [("stand", "1 Стойка", "Стойка", "#8a94a3"), ("kulisa", "2 Кулиса (рукоять)", "Кулиса", "#2d3540"),
         ("kamen", "3 Камень", "Камень", "#e8c99a"), ("pin", "4 Палец", "Палец", "#7fae6a"),
         ("polzun", "5 Ползун", "Ползун", "#3a4049"), ("washer", "6 Шайба", "Шайба", "#c3c8cf"),
         ("nut", "7 Гайка", "Гайка", "#c3c8cf"), ("cover", "8 Кожух", "Кожух", "#b03a2e")]
BBOX = {"stand": (128.0, 410.0, 92.0), "kulisa": (509.0, 18.0, 20.0), "kamen": (20.0, 27.0, 15.5), "pin": (10.0, 10.0, 32.0),
        "polzun": (40.0, 136.65, 40.0), "washer": (16.0, 16.0, 1.6), "nut": (13.0, 15.0, 6.5), "cover": (57.5, 115.0, 58.0)}


def read_stl(path):
    v = [list(map(float, ln.split()[1:4])) for ln in open(path, encoding="ascii") if ln.strip().startswith("vertex")]
    return np.array(v, dtype=np.float32).reshape(-1, 9)


def bottle_contour():
    """половина сечения бутылки (как bottle_contour() в kompas_build.py), дуги — ломаными; (r, y), дно y = 0"""
    rb, rn, t, b = BOTTLE_R, 13.0, 2.3, 5.0
    y1, y2 = 98.0, 173.4
    dx, dy = rb - rn, y2 - y1
    s = (dx ** 2 + dy ** 2) / (2 * dx)
    r1, r2 = 0.76 * s, 0.24 * s
    c1, c2 = (rb - r1, y1), (rn + r2, y2)
    ux, uy = (c2[0] - c1[0]) / s, (c2[1] - c1[1]) / s
    tp = lambda r: (c1[0] + r * ux, c1[1] + r * uy)
    ri = rb - t
    seq = [(0.0, 0.0), (24.0, 0.0), (rb, 6.2, 24.0, 6.2), (rb, y1), (*tp(r1), *c1), (rn, y2, *c2),
           (rn, 218.2), (13.3, 219.6), (13.3, 225.0), (12.0, BOTTLE_H), (8.7, BOTTLE_H), (8.7, 212.0), (rn - t, 205.0),
           (rn - t, y2), (*tp(r1 - t), *c2), (ri, y1, *c1), (ri, b + 3.2), (ri - 3.2, b, ri - 3.2, b + 3.2), (0.0, b)]
    pts = [seq[0]]
    for p in seq[1:]:
        if len(p) == 2:
            pts.append(p); continue
        x, y, xc, yc = p
        x0, y0 = pts[-1]
        a0, a1 = np.arctan2(y0 - yc, x0 - xc), np.arctan2(y - yc, x - xc)
        da = (a1 - a0 + np.pi) % (2 * np.pi) - np.pi                 # короткая дуга
        r = np.hypot(x - xc, y - yc)
        for k in range(1, 13):
            a = a0 + da * k / 12
            pts.append((xc + r * np.cos(a), yc + r * np.sin(a)))
    return [[round(float(x), 3), round(float(y), 3)] for x, y in pts]


geo, info = {}, []
for key, fname, title, color in PARTS:
    tri = read_stl(os.path.join(STL, fname + ".stl"))
    p = tri.reshape(-1, 3)
    size = p.max(axis=0) - p.min(axis=0)
    assert np.allclose(size, BBOX[key], atol=0.06), (key, size)        # это те самые детали 13.11
    geo[key] = base64.b64encode(tri.astype("<f4").tobytes()).decode("ascii")
    info.append(f"{title}: {len(tri)} треуг.")

data = {"E": E, "PH_N": PH_N, "PH_K": PH_K, "PH0": PH0, "Z_ST": Z_ST, "Y_ST0": Y_ST0, "Z_KUL": Z_KUL, "Z_KAM": Z_KAM,
        "Z_PIN": Z_PIN, "Z_WASHER": Z_WASHER, "Z_NUT": Z_WASHER + WASHER_S + NUT_M / 2, "BOTTLE_H": BOTTLE_H,
        "CAP_TOP": CAP_TOP, "CAP_SKIRT": CAP_SKIRT, "R_OBZH": R_OBZH, "R_K": R_K, "bottle": bottle_contour(),
        "parts": [{"key": k, "title": t, "color": c} for k, _, t, c in PARTS], "geo": geo}
assert abs(E * tan(radians(PH_N)) - E * tan(radians(PH_K)) - 16.0) < 1e-6                # ход ползуна 16 мм

html = open(os.path.join(HERE, "anim_template.html"), encoding="utf-8").read()
for mark, text in (("/*__THREE__*/", open(os.path.join(HERE, "lib", "three.min.js"), encoding="utf-8").read()),
                   ("/*__ORBIT__*/", open(os.path.join(HERE, "lib", "OrbitControls.js"), encoding="utf-8").read()),
                   ("/*__DATA__*/", "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";")):
    assert html.count(mark) == 1, mark
    html = html.replace(mark, text.replace("</script", "<\\/script"))
open(OUT, "w", encoding="utf-8").write(html)
print("; ".join(info))
print(f"{OUT}: {os.path.getsize(OUT) / 1024:.0f} КБ")
