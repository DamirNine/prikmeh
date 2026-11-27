# -*- coding: utf-8 -*-
"""3D-анимация сборки укупоривателя — один самостоятельный HTML-файл (без интернета и без установки):
геометрия деталей — из STL комплекта «Сборка» (в координатах самих деталей), положения в
сборке — как в kompas/kompas_assembly.py
(PLACE), three.js и OrbitControls встроены в файл из папки lib/.
    python build_anim.py"""
import base64, json, os
from math import tan, radians
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "2026-11-21")              # детали STL и three.js
STL = os.path.join(SRC, "Сборка", "Детали для печати")
OUT = os.path.join(HERE, "3D-сборка укупоривателя.html")
RJ = json.load(open(os.path.join(SRC, "..", "2026-11-04", "calc_v21.json"), encoding="utf-8"))

# ---------------- размеры и положения — те же числа, что в kompas/kompas_build.py и kompas_assembly.py
E = 12.53
PH_N, PH_K, PH0 = RJ["phi_n"], RJ["phi_k"], RJ["phi_y"]
Z_ST, Y_ST0 = -34.0, -325.25                      # передняя грань стойки; верх основания = дно бутылки
Z_KUL, Z_KAM, Z_PIN = -21.5, -9.0, -13.0          # начала деталей по z в сборке
PIN_L1, WASHER_S, NUT_M = 23.5, 2.0, 8.0         # гладкая часть пальца Ø10 до передней грани шайбы; шайба 10; гайка М10
Z_WASHER = Z_PIN + PIN_L1 - WASHER_S
BOTTLE_H, BOTTLE_R = 226.5, 30.2
SCR_X, SCR_Y = E - 5.5, (E * tan(radians(PH_K)) - 55 - 17.0) / 2   # установочный винт М10 направляющей (как в kompas_build.py)
CAP_TOP, CAP_SKIRT, R_OBZH, R_K = 0.94, 5.4, 14.3, 16.05

PARTS = [("stand", "1 Стойка", "Стойка", "#8a94a3"), ("kulisa", "2 Кулиса (рукоять)", "Кулиса", "#2d3540"),
         ("kamen", "3 Камень", "Камень", "#e8c99a"), ("pin", "4 Палец", "Палец", "#7fae6a"),
         ("guide", "5Б Направляющая без планок (вариант Б)", "Направляющая", "#5b7896"), ("screw", "10 Винт М10", "Винт М10", "#c3c8cf"),
         ("polzun", "6 Ползун", "Ползун", "#3a4049"), ("head", "6а Головка ползуна", "Головка ползуна", "#3a4049"),
         ("washer", "7 Шайба", "Шайба", "#c3c8cf"), ("nut", "8 Гайка", "Гайка", "#c3c8cf"), ("cover", "9 Кожух", "Кожух", "#b03a2e"),
         ("key", "11 Ключ шестигранный S5", "Ключ S5", "#d08a2a")]       # 18.11: ключ — только на шаге «Винт М10»
BBOX = {"stand": (128.0, 410.0, 92.0), "kulisa": (509.0, 18.0, 20.0), "kamen": (20.0, 27.0, 15.5), "pin": (10.0, 10.0, 32.0),
        "guide": (43.0, 32.753, 61.0), "polzun": (24.0, 112.5, 16.0), "head": (40.0, 34.15, 40.0), "washer": (20.0, 20.0, 2.0), "nut": (16.0, 18.48, 8.0),
        "cover": (57.5, 115.0, 58.0), "screw": (9.7, 9.7, 10.0),
        "key": (27.80, 4.85, 77.80)}                     # 21.11: ключ S4,85 (было 4,6 — проворачивался в винте)


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


# защёлки кожуха (kompas_build.py, 15.11): язычок — часть боковой стенки 10 × 2 × 30 между двумя прорезями от задней кромки,
# на конце крючок внутрь 1,5 мм (скос 30° на z 0,06…2,66, удерживающая грань z = 4); зацеп на стойке — козырёк z 4…7 в 0,2 мм
# от стенки. Язычок вырезается из сетки кожуха (треугольники разрезаются гранями коробки язычка) и в анимации поворачивается
# вокруг корня (z = 30)
CV_X0, CV_X1, CV_T = -12.0, 45.5, 2.0
SN_L, SN_Y, SN_ZH, SN_ZL, SN_CLR = 30.0, 1.5, 4.0, 7.0, 0.2
SN_POS = {"left": (25.0, 35.0), "right": (-30.0, -20.0)}


def split_box(tris, lo, hi):
    """разрезать треугольники (n × 9) коробкой [lo, hi]: (внутри, снаружи) — выпуклые многоугольники, веером в треугольники"""
    inside, outside = [], []

    def fan(poly, out):
        for i in range(1, len(poly) - 1):
            out.append(np.concatenate([poly[0], poly[i], poly[i + 1]]))

    for t in tris:
        poly = [t[0:3], t[3:6], t[6:9]]
        for ax in range(3):
            for bound, sgn in ((lo[ax], 1.0), (hi[ax], -1.0)):        # полупространство sgn·(p − bound) ≥ 0 — «внутри»
                f = [sgn * (p[ax] - bound) for p in poly]
                pin, pout = [], []
                for i in range(len(poly)):
                    a, b, fa, fb = poly[i], poly[(i + 1) % len(poly)], f[i], f[(i + 1) % len(poly)]
                    if fa >= 0: pin.append(a)
                    if fa <= 0: pout.append(a)
                    if (fa > 0 > fb) or (fa < 0 < fb):
                        q = a + (b - a) * (fa / (fa - fb)); pin.append(q); pout.append(q)
                if len(pout) >= 3 and any(x < -1e-9 for x in f):
                    fan(pout, outside)
                poly = pin
                if len(poly) < 3:
                    break
            if len(poly) < 3:
                break
        if len(poly) >= 3:
            fan(poly, inside)
    ok = lambda a: [x for x in a if np.linalg.norm(np.cross(x[3:6] - x[0:3], x[6:9] - x[0:3])) > 1e-9]
    return np.array(ok(inside), dtype=np.float32), np.array(ok(outside), dtype=np.float32)


def snap_tongues(tri):
    """тело кожуха без язычков и язычки: [(сторона, треугольники, шарнир (x, z), k — «внутрь» по x)]"""
    body, tongues = tri.astype(np.float64), []
    for side, (y0, y1) in SN_POS.items():
        if side == "left":
            xa, xb, xh, k = CV_X0 - 0.01, CV_X0 + CV_T + SN_Y + 0.01, CV_X0 + CV_T / 2, 1.0
        else:
            xa, xb, xh, k = CV_X1 - CV_T - SN_Y - 0.01, CV_X1 + 0.01, CV_X1 - CV_T / 2, -1.0
        t_in, body = split_box(body, (xa, y0 - 0.005, -0.01), (xb, y1 + 0.005, SN_L))
        body = body.astype(np.float64)
        assert len(t_in) > 20, (side, len(t_in))
        tongues.append({"side": side, "geo": base64.b64encode(t_in.astype("<f4").tobytes()).decode("ascii"),
                        "hinge": [xh, SN_L], "k": k})
    return body.astype(np.float32), tongues


geo, info = {}, []
for key, fname, title, color in PARTS:
    tri = read_stl(os.path.join(STL, fname + ".stl"))
    p = tri.reshape(-1, 3)
    size = p.max(axis=0) - p.min(axis=0)
    assert np.allclose(size, BBOX[key], atol=0.06), (key, size)        # это те самые детали
    if key == "cover":
        n0 = len(tri)
        tri, tongues = snap_tongues(tri)
        info.append(f"кожух: {n0} треуг. → тело {len(tri)} + язычки")
    geo[key] = base64.b64encode(tri.astype("<f4").tobytes()).decode("ascii")
    info.append(f"{title}: {len(tri)} треуг.")

data = {"E": E, "PH_N": PH_N, "PH_K": PH_K, "PH0": PH0, "Z_ST": Z_ST, "Y_ST0": Y_ST0, "Z_KUL": Z_KUL, "Z_KAM": Z_KAM,
        "Z_PIN": Z_PIN, "Z_WASHER": Z_WASHER, "SCR_X": SCR_X, "SCR_Y": SCR_Y, "Z_NUT": Z_WASHER + WASHER_S + NUT_M / 2, "BOTTLE_H": BOTTLE_H,
        "CAP_TOP": CAP_TOP, "CAP_SKIRT": CAP_SKIRT, "R_OBZH": R_OBZH, "R_K": R_K, "bottle": bottle_contour(),
        "parts": [{"key": k, "title": t, "color": c} for k, _, t, c in PARTS], "geo": geo, "tongues": tongues,
        "SNAP": {"L": SN_L, "Y": SN_Y, "ZH": SN_ZH, "ZL": SN_ZL, "CLR": SN_CLR, "RAMP0": 0.06, "RAMP1": 0.06 + SN_Y / tan(radians(30))}}
assert abs(E * tan(radians(PH_N)) - E * tan(radians(PH_K)) - 16.0) < 1e-6                # ход ползуна 16 мм

html = open(os.path.join(HERE, "anim_template.html"), encoding="utf-8").read()
for mark, text in (("/*__THREE__*/", open(os.path.join(SRC, "lib", "three.min.js"), encoding="utf-8").read()),
                   ("/*__ORBIT__*/", open(os.path.join(SRC, "lib", "OrbitControls.js"), encoding="utf-8").read()),
                   ("/*__DATA__*/", "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";")):
    assert html.count(mark) == 1, mark
    html = html.replace(mark, text.replace("</script", "<\\/script"))
open(OUT, "w", encoding="utf-8").write(html)
print("; ".join(info))
print(f"{OUT}: {os.path.getsize(OUT) / 1024:.0f} КБ")
