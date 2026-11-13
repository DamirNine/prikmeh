# -*- coding: utf-8 -*-
"""STL всех деталей укупоривателя (без бутылки) для 3D-печати — в папку комплекта «Укупориватель — печать и сборка/
Детали для печати». Размеры в миллиметрах (КОМПАС пишет текстовый STL — слайсеры его читают). Проверка каждого файла: габариты совпадают с деталью,
сетка замкнута (каждое ребро — ровно у двух треугольников). Сборка в КОМПАСе должна быть закрыта.
    python export_stl.py"""
import os, struct, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kompas"))
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A5, A7, C, FILES, PARTS_DIR, app, k5, qi

PKG = os.path.join(HERE, "..", "Укупориватель — печать и сборка")
OUT = os.path.join(PKG, "Детали для печати")
os.makedirs(OUT, exist_ok=True)
# номер в инструкции, имя файла
PARTS = [("stand", "1 Стойка"), ("kulisa", "2 Кулиса (рукоять)"), ("kamen", "3 Камень"), ("pin", "4 Палец"),
         ("polzun", "5 Ползун"), ("washer", "6 Шайба"), ("nut", "7 Гайка"), ("cover", "8 Кожух")]


def read_stl(path):
    """двоичный или текстовый (ASCII) STL — список треугольников (9 координат)"""
    data = open(path, "rb").read()
    if data[:5] == b"solid" and b"facet" in data[:400]:
        v = [tuple(map(float, ln.split()[1:4])) for ln in data.decode("ascii").splitlines() if ln.strip().startswith("vertex")]
        assert len(v) % 3 == 0
        return [v[i] + v[i + 1] + v[i + 2] for i in range(0, len(v), 3)]
    n = struct.unpack("<I", data[80:84])[0]
    assert len(data) == 84 + 50 * n, "повреждённый STL"
    return [struct.unpack("<12f", data[84 + 50 * i: 84 + 50 * i + 48])[3:] for i in range(n)]


def check(path):
    tris = read_stl(path)
    pts = [t[i:i + 3] for t in tris for i in (0, 3, 6)]
    lo = [min(p[j] for p in pts) for j in range(3)]
    hi = [max(p[j] for p in pts) for j in range(3)]
    key = lambda p: tuple(round(c, 4) for c in p)
    edges = Counter()
    for t in tris:
        v = [key(t[i:i + 3]) for i in (0, 3, 6)]
        for a, b in ((v[0], v[1]), (v[1], v[2]), (v[2], v[0])):
            edges[frozenset((a, b))] += 1
    open_edges = sum(1 for c in edges.values() if c != 2)
    return len(tris), [h - l for l, h in zip(lo, hi)], open_edges


for k, name in PARTS:
    src = os.path.join(PARTS_DIR, FILES[k])
    d = app.Documents.Open(src, True, False)
    assert d is not None, src
    d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
    p = A5.ksAdditionFormatParam(d5.AdditionFormatParam())
    p.Init()
    p.format, p.formatBinary, p.lengthUnits = C.ksConverterToSTL, True, C.ksLUnMM
    p.step, p.angle = 0.02, 3.0                      # отклонение хорды 0,02 мм, угол 3° — окружности гладкие для печати
    dst = os.path.join(OUT, name + ".stl")
    if os.path.exists(dst):
        os.remove(dst)
    d5.SaveAsToAdditionFormat(dst, p)
    d.Close(0)
    assert os.path.exists(dst), dst
    n, size, open_edges = check(dst)
    print(f"  {name}.stl: {n} треуг., габарит {size[0]:.1f} × {size[1]:.1f} × {size[2]:.1f} мм, "
          f"{'замкнута' if open_edges == 0 else f'НЕЗАМКНУТЫХ рёбер {open_edges}'}, {os.path.getsize(dst) // 1024} КБ")
