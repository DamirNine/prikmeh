# -*- coding: utf-8 -*-
"""Скрины APM для слайда МКЭ (Корнеев 23.11 23:22): «не вставляй скрины с SVM-диаграммой, оставляй только деталь,
снизу подписывай максимальное, минимальное значения». Шкала ищется по чёрной рамке цветной полосы (вертикальный тёмный
отрезок > 120 px в правой половине); её область закрашивается фоном, кадр обрезается по детали (насыщенные пиксели).
  вход  ../../2026-11-16/apm/_для_отчёта/*.png  →  fig/apm_<имя>.png
    python crop_apm.py"""
import os, numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
APM = os.path.join(HERE, "..", "..", "2026-11-16", "apm", "_для_отчёта")
NAMES = ["кулиса_2_тест", "кулиса_4_тест_новой_2", "ползун_2_тест", "ползун_4_тест_нового", "камень_2_тест",
         "камень_4_тест_итог", "направляющая_2_тест", "направляющая_6_тест_с_винтом"]


def legend_bar(a):
    H, W, _ = a.shape
    dark = a.max(axis=2) < 70
    for x in range(W // 2, W):
        col = dark[:, x]; run = 0
        for y in range(H):
            if col[y]:
                run += 1
            else:
                if run > 120:
                    return x, y - run, y
                run = 0
    return None


for n in NAMES:
    im = Image.open(os.path.join(APM, n + ".png")).convert("RGB")
    a = np.asarray(im).astype(int).copy(); H, W, _ = a.shape
    x, y0, y1 = legend_bar(a)
    lx0, ly0, ly1 = max(x - 25, 0), max(y0 - 120, 0), min(y1 + 30, H)
    sat = (a.max(axis=2) - a.min(axis=2)) > 45
    sat[:18, :] = False                                     # полоса панели инструментов сверху
    sat[ly0:ly1, lx0:] = False                              # шкала SVM
    ys, xs = np.nonzero(sat)
    # отбрасываем одиночный мусор: берём 0,2…99,8 перцентили
    bx0, bx1 = int(np.percentile(xs, 0.1)), int(np.percentile(xs, 99.9))
    by0, by1 = int(np.percentile(ys, 0.1)), int(np.percentile(ys, 99.9))
    pad = 14
    bx0, by0, bx1, by1 = max(bx0 - pad, 0), max(by0 - pad, 0), min(bx1 + pad, W), min(by1 + pad, H)
    # если шкала попала в кадр — закрасить её цветом фона (медиана по строке слева от шкалы)
    if bx1 > lx0 and by1 > ly0 and by0 < ly1:
        for y in range(ly0, ly1):
            a[y, lx0:] = np.median(a[y, max(lx0 - 40, 0):lx0], axis=0)
    out = Image.fromarray(a.astype(np.uint8)).crop((bx0, by0, bx1, by1))
    out.save(os.path.join(HERE, "fig", "apm_" + n + ".png"))
    print(n, "шкала x =", x, "кадр", (bx0, by0, bx1, by1), "закраска" if bx1 > lx0 and by1 > ly0 else "")
