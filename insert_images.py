# -*- coding: utf-8 -*-
# Заменяет картинки fig01..fig14 (media_fixed/) в копии docx, пересчитывая cy под новый аспект.
import re
import os
import zipfile
from PIL import Image

PROJ = os.path.dirname(__file__)
SRC = os.path.join(PROJ, "РК6-45Б_бригада_2_решение_ПМ_исправл.docx")
DST = os.path.join(PROJ, "РК6-45Б_бригада_2_решение_ПМ_финал.docx")
FIGDIR = os.path.join(PROJ, "media_fixed")

fig_files = {
    1: "fig01_traj.png", 2: "fig02_dsk_v.png", 3: "fig03_dsk_a.png", 4: "fig04_psk_r.png",
    5: "fig05_psk_v.png", 6: "fig06_psk_a.png", 7: "fig07_espzd_tn.png", 8: "fig08_espzd_v.png",
    9: "fig09_espzd_a.png", 10: "fig10_3d_schema.png", 11: "fig11_3d_v.png", 12: "fig12_3d_a.png",
    13: "fig13_3d_v2.png", 14: "fig14_3d_a2.png",
}

z = zipfile.ZipFile(SRC)
rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
doc = z.read("word/document.xml").decode("utf-8")

rid_to_num = {}
for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="media/image(\d+)\.png"', rels):
    rid_to_num[m.group(1)] = int(m.group(2))

replacements = []
count = 0
for m in re.finditer(r'<a:blip r:embed="(rId\d+)"', doc):
    rid = m.group(1)
    if rid not in rid_to_num or rid_to_num[rid] not in fig_files:
        continue
    num = rid_to_num[rid]
    fname = fig_files[num]
    im = Image.open(os.path.join(FIGDIR, fname))
    W, H = im.size
    blip_pos = m.start()

    wp_match = None
    for wpm in re.finditer(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', doc[:blip_pos]):
        wp_match = wpm
    assert wp_match is not None, f"no wp:extent before blip for image{num}"
    cx = int(wp_match.group(1))
    new_cy = round(cx * H / W)
    replacements.append((wp_match.start(), wp_match.end(), f'<wp:extent cx="{cx}" cy="{new_cy}"/>'))

    am = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"/>', doc[blip_pos:])
    assert am is not None, f"no a:ext after blip for image{num}"
    a_start = blip_pos + am.start()
    a_end = blip_pos + am.end()
    acx = int(am.group(1))
    a_new_cy = round(acx * H / W)
    replacements.append((a_start, a_end, f'<a:ext cx="{acx}" cy="{a_new_cy}"/>'))
    count += 1

print(f"найдено и обработано картинок: {count}")
replacements.sort(key=lambda r: r[0])
out = []
last = 0
for start, end, text in replacements:
    out.append(doc[last:start])
    out.append(text)
    last = end
out.append(doc[last:])
new_doc = "".join(out)

with zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in z.infolist():
        if item.filename == "word/document.xml":
            zout.writestr(item, new_doc.encode("utf-8"))
        elif item.filename.startswith("word/media/image") and item.filename.endswith(".png"):
            mm = re.search(r"image(\d+)\.png", item.filename)
            num = int(mm.group(1)) if mm else None
            if num in fig_files:
                with open(os.path.join(FIGDIR, fig_files[num]), "rb") as f:
                    zout.writestr(item, f.read())
            else:
                zout.writestr(item, z.read(item.filename))
        else:
            zout.writestr(item, z.read(item.filename))

print("saved", DST)
