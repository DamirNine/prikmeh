# -*- coding: utf-8 -*-
"""Рис. 10, 11 (v21) = рис. 10, 11 из figs_v14.py (2026-10-24); на расчётной схеме связи отброшены, поэтому точки O и D —
закрашенные точки (было: пустой кружок O и квадрат D)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "2026-10-24", "figs_v14.py")
src = open(SRC, encoding="utf-8").read()
src = src[:src.index("# ====================================================================== рис. 12")]
reps = [('OUT = os.path.dirname(os.path.abspath(__file__))', 'OUT = HERE_V21\nJS_DIR = os.path.join(HERE_V21, "..", "2026-10-24")'),
        ('json.load(open(os.path.join(OUT, "strength_v13.json")', 'json.load(open(os.path.join(JS_DIR, "strength_v13.json")'),
        ('ax.plot(*O, "o", ms=5.5, mfc="white", mec=INK, mew=1.2, zorder=7)', 'ax.plot(*O, "o", ms=5.0, color=INK, zorder=7)'),
        ('ax.plot(*D, "s", ms=4.2, color=INK, zorder=7)', 'ax.plot(*D, "o", ms=4.2, color=INK, zorder=7)'),
        ('"fig10_epury_phiy_v14.png"', '"fig10_epury_phiy_v21.png"'), ('"fig11_epury_phik_v14.png"', '"fig11_epury_phik_v21.png"')]
for a, b in reps:
    assert src.count(a) == 1, a
    src = src.replace(a, b)
exec(compile(src, "figs_v14 (рис. 10, 11)", "exec"), dict(__name__="figs_epury_v21", HERE_V21=HERE))
print("ok")
