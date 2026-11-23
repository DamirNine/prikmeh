# -*- coding: utf-8 -*-
"""23.11: анимация сборки под принятую направляющую варианта Б (УКП.00.002-01, без верхних планок — «стул» с полкой).
Копии build_anim.py и anim_template.html из 2026-11-21 правятся здесь: деталь 5 → 5Б, тексты шагов без планок.
Детали (STL) и three.js берутся из 2026-11-21. Запуск: python patch_anim_B.py && python build_anim.py"""
import io, os
HERE = os.path.dirname(os.path.abspath(__file__))


def patch(fn, pairs):
    s = io.open(fn, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (fn, a[:70], s.count(a))
        s = s.replace(a, b)
    io.open(fn, "w", encoding="utf-8").write(s)


patch(os.path.join(HERE, "build_anim.py"), [
    ('HERE = os.path.dirname(os.path.abspath(__file__))\n',
     'HERE = os.path.dirname(os.path.abspath(__file__))\nSRC = os.path.join(HERE, "..", "..", "2026-11-21")              # детали STL и three.js\n'),
    ('STL = os.path.join(HERE, "Сборка", "Детали для печати")', 'STL = os.path.join(SRC, "Сборка", "Детали для печати")'),
    ('OUT = os.path.join(HERE, "Сборка", "3D-сборка укупоривателя.html")', 'OUT = os.path.join(HERE, "3D-сборка укупоривателя.html")'),
    ('os.path.join(HERE, "..", "2026-11-04", "calc_v21.json")', 'os.path.join(SRC, "..", "2026-11-04", "calc_v21.json")'),
    ('("guide", "5 Направляющая", "Направляющая", "#5b7896")', '("guide", "5Б Направляющая без планок (вариант Б)", "Направляющая", "#5b7896")'),
    ('"guide": (43.0, 97.0, 61.0)', '"guide": (43.0, 32.753, 61.0)'),          # вариант Б: всё выше пластины (y > −17) срезано
    ('os.path.join(HERE, "lib", "three.min.js")', 'os.path.join(SRC, "lib", "three.min.js")'),
    ('os.path.join(HERE, "lib", "OrbitControls.js")', 'os.path.join(SRC, "lib", "OrbitControls.js")'),
])

patch(os.path.join(HERE, "anim_template.html"), [
    ("пластину — в выемку стойки до дна, планки — по обе стороны от камня, полка с отверстием под шток — внизу.",
     "пластину — в выемку стойки до дна, полка с отверстием под шток — внизу, под камнем."),
    ("Опустите ползун (брусок со штоком) сверху между планками направляющей: шток проходит в отверстие полки,",
     "Опустите ползун (брусок со штоком) сверху: шток проходит в отверстие полки направляющей,"),
    ("ползун идёт строго вертикально — брусок между планками, шток в полке;",
     "ползун идёт строго вертикально — шток скользит в отверстии полки;"),
])
print("ok")
