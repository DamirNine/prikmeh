# -*- coding: utf-8 -*-
"""эпюры РПЗ (рис. 11, 12): чёрные точки O, D, K → белые кружки с чёрным контуром (замечание преподавателя 23.11)
    python dots_to_rings.py вход.png выход.png OD/OK"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
g = im.convert("L").point(lambda v: 0 if v < 70 else 255)
core = np.asarray(g.filter(ImageFilter.MaxFilter(13))) == 0          # эрозия тёмного: линии исчезают, точки остаются
seen = np.zeros_like(core); H, W = core.shape
blobs = []
for y0, x0 in zip(*np.nonzero(core)):
    if seen[y0, x0]: continue
    st, pts = [(y0, x0)], []; seen[y0, x0] = True
    while st:
        y, x = st.pop(); pts.append((y, x))
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            v, u = y + dy, x + dx
            if 0 <= v < H and 0 <= u < W and core[v, u] and not seen[v, u]:
                seen[v, u] = True; st.append((v, u))
    blobs.append(np.array(pts))
# точка D у самой оси O сливается с толстой линией кулисы — ставим её по геометрии: D = O + (OD/OK)·(K − O)
ratio = float(sys.argv[3])
keep = [p for p in blobs if 5 <= np.ptp(p[:, 0]) + 1 <= 20 and 5 <= np.ptp(p[:, 1]) + 1 <= 20]
panels = {}
for p in keep:
    cy, cx = p.mean(axis=0)
    panels.setdefault((cx < W / 2, cy < H / 2), []).append((cy, cx))
extra = []
for pts in panels.values():
    O, K = np.array(max(pts)), np.array(min(pts))            # O — нижняя, K — верхняя точка панели
    D = O + ratio * (K - O)
    extra.append(np.array([D - 3, D + 3]))
blobs += extra
d = ImageDraw.Draw(im); found = []
for p in blobs:
    h, w = np.ptp(p[:, 0]) + 1, np.ptp(p[:, 1]) + 1
    if h > 20 or w > 20 or h < 5 or w < 5 or abs(h - w) > 4:      # остаток точки после эрозии маленький и круглый; буквы/линии — нет
        continue
    cy, cx = p.mean(axis=0)
    r = (max(h, w) + 12) / 2 + 5
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="white", outline=(23, 33, 46), width=5)
    found.append((int(cx), int(cy), int(h), int(w)))
im.save(dst); print(dst, "точек:", len(found), found)
