# -*- coding: utf-8 -*-
"""Рис. 14 (v21) = figs_v19.py (2026-11-02) по данным calc_v21 (масса кулисы со ступицей)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "..", "2026-11-02", "figs_v19.py"), encoding="utf-8").read()
reps = [('"calc_v17.npz"', '"calc_v21.npz"'), ('"calc_v17.json"', '"calc_v21.json"'),
        ('"fig14_unknowns_v19.png"', '"fig14_unknowns_v21.png"')]
for a, b in reps:
    assert src.count(a) == 1, a
    src = src.replace(a, b)
exec(compile(src, "figs_v19 (рис. 14)", "exec"), dict(__name__="fig14_v21", __file__=os.path.join(HERE, "fig14_v21.py")))
print("ok")
