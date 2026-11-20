# -*- coding: utf-8 -*-
"""pptx → pdf через PowerPoint (+ png слайдов для проверки в папку из argv[1], если задана).  python to_pdf.py [png_dir]"""
import os, sys
import win32com.client as w
HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, "Презентация_укупориватель.pptx")
pdf = src[:-5] + ".pdf"
app = w.DispatchEx("PowerPoint.Application")
try:
    p = app.Presentations.Open(src, True, False, False)
    p.SaveAs(pdf, 32)
    p.Close()
finally:
    app.Quit()
print("pdf ok")
if len(sys.argv) > 1:
    import fitz
    os.makedirs(sys.argv[1], exist_ok=True)
    for i, pg in enumerate(fitz.open(pdf), 1):
        pg.get_pixmap(dpi=110).save(os.path.join(sys.argv[1], f"s{i:02d}.png"))
    print("png ok")
