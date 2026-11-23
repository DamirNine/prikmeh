# -*- coding: utf-8 -*-
"""эпюры_фи_у.png: точка K — не шарнир → вернуть чёрную точку из эпюры_фи_у_исходный.png (Корнеев 23.11 22:58).
K ищется в исходнике как верхняя чёрная точка каждой панели; область вокруг неё копируется из исходника."""
import os, numpy as np
from PIL import Image, ImageFilter
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
src = Image.open(os.path.join(F, "эпюры_фи_у_исходный.png")).convert("RGB")
dst = Image.open(os.path.join(F, "эпюры_фи_у_v1.png")).convert("RGB")
assert src.size == dst.size
g = src.convert("L").point(lambda v: 0 if v < 70 else 255)
core = np.asarray(g.filter(ImageFilter.MaxFilter(13))) == 0
H, W = core.shape; seen = np.zeros_like(core); blobs = []
for y0, x0 in zip(*np.nonzero(core)):
    if seen[y0, x0]: continue
    st, pts = [(y0, x0)], []; seen[y0, x0] = True
    while st:
        y, x = st.pop(); pts.append((y, x))
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            v, u = y + dy, x + dx
            if 0 <= v < H and 0 <= u < W and core[v, u] and not seen[v, u]:
                seen[v, u] = True; st.append((v, u))
    p = np.array(pts); h, w = np.ptp(p[:, 0]) + 1, np.ptp(p[:, 1]) + 1
    if 5 <= h <= 20 and 5 <= w <= 20 and abs(h - w) <= 4: blobs.append(p.mean(axis=0))
panels = {}
for cy, cx in blobs: panels.setdefault((cx < W / 2, cy < H / 2), []).append((cy, cx))
for pts in panels.values():
    cy, cx = map(int, min(pts)); r = 22
    dst.paste(src.crop((cx - r, cy - r, cx + r, cy + r)), (cx - r, cy - r)); print("K:", cx, cy)
dst.save(os.path.join(F, "эпюры_фи_у.png"))
