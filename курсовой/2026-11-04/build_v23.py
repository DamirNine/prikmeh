# -*- coding: utf-8 -*-
"""Сборка v23 (04.11) = build_v22.py с рис. 12 из fig12_v23.py: в разрезе Б–Б обойма и палец D — одного цвета (одна деталь),
обойма заштрихована, палец за секущей плоскостью — без штриховки."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "build_v22.py"), encoding="utf-8").read()
for a, b in (('механизм_v22.docx"', 'механизм_v23.docx"'), ('"fig12_kamen_v22.png"', '"fig12_kamen_v23.png"')):
    assert src.count(a) == 1, a
    src = src.replace(a, b)
exec(compile(src, "build_v22 → v23", "exec"), dict(__name__="build_v23", __file__=os.path.join(HERE, "build_v23.py")))
