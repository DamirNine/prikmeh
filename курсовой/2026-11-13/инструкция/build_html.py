# -*- coding: utf-8 -*-
"""Инструкция по сборке: template.html + картинки img/*.png (встраиваются в файл) → «Укупориватель — печать и сборка/
Инструкция по сборке.html» — один самостоятельный файл, открывается в любом браузере без интернета.
    python make_images.py   (картинки из сборки КОМПАС)
    python export_stl.py    (STL деталей)
    python build_html.py"""
import base64, io, os, re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "Укупориватель — печать и сборка")
s = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()


def data_uri(name):
    im = Image.open(os.path.join(HERE, "img", name + ".png")).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


names = sorted(set(re.findall(r"\{\{img:([^}]+)\}\}", s)))
for n in names:
    s = s.replace("{{img:%s}}" % n, data_uri(n))
assert "{{" not in s
out = os.path.join(PKG, "Инструкция по сборке.html")
open(out, "w", encoding="utf-8").write(s)
print(f"картинок {len(names)}, {os.path.getsize(out) // 1024} КБ → {os.path.relpath(out, HERE)}")
