# -*- coding: utf-8 -*-
"""Картинки для презентации: рисунки из РПЗ v13 (Саша, 20.11) + рендеры и герб из 2026-11-18/РПЗ/fig.
Обрезаются белые поля, размеры пишутся в fig/sizes.json.  python prep_figs.py"""
import json, os, sys, zipfile, posixpath
from PIL import Image, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
RPZ = os.path.join(HERE, "..", "РПЗ_v13", "РПЗ_укупориватель.docx")
OLD = os.path.join(HERE, "..", "..", "2026-11-18", "РПЗ", "fig")
OUT = os.path.join(HERE, "fig")
# номер картинки в РПЗ v13 (по порядку в тексте) → имя
NAMES = {1: "без_кожуха", 2: "обжим", 3: "кин_схема", 4: "синтез_площадь", 5: "синтез_уступки", 6: "омега",
         7: "ползун_кинематика", 8: "закон_обжима", 9: "схемы_первичный", 10: "длина_рукояти", 11: "реакции_первичный",
         12: "эпюры_фи_у", 13: "эпюры_фи_к", 14: "узел_камня", 15: "узел_камня_2", 16: "схемы_уточняющий",
         17: "реакции_уточняющий", 18: "детали", 19: "крайние_положения", 20: "мкэ_кулиса", 21: "мкэ_ползун",
         22: "мкэ_камень", 23: "мкэ_направляющая", 24: "общий_вид"}


def trim(im, pad=12):
    rgb = im.convert("RGB")
    bg = Image.new("RGB", rgb.size, (255, 255, 255))
    box = ImageChops.difference(rgb, bg).point(lambda v: 255 if v > 12 else 0).getbbox()
    if not box:
        return im
    l, t, r, b = box
    return im.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, im.width), min(b + pad, im.height)))


def main():
    import docx
    from docx.oxml.ns import qn
    d = docx.Document(RPZ)
    blips = [b.get(qn("r:embed")) for p in d.element.body.iterchildren(qn("w:p"))       # без герба в таблице титула
             for b in p.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip")]
    assert len(blips) == 24, len(blips)
    sizes = {}
    for k, rid in enumerate(blips, 1):
        part = d.part.rels[rid].target_part
        tmp = os.path.join(OUT, "_tmp.png")
        open(tmp, "wb").write(part.blob)
        im = trim(Image.open(tmp))
        fn = NAMES[k] + ".png"
        im.save(os.path.join(OUT, fn))
        os.remove(tmp)
        sizes[fn] = im.size
    for fn in ("герб.png", "00_общий_вид.png", "01_без_кожуха.png"):
        im = Image.open(os.path.join(OLD, fn))
        if fn != "герб.png":
            im = trim(im)
        im.save(os.path.join(OUT, fn))
        sizes[fn] = im.size
    json.dump(sizes, open(os.path.join(OUT, "sizes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(sizes), "картинок")


main()
