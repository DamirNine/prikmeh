# -*- coding: utf-8 -*-
"""27.11: ползун и головка на резьбе — копии в v25 и пересохранение в v24 (SaveAsEx mode 30) для папок вывода.
    python save_thread_parts.py <папка_v25> <папка_v24> [...]  (можно несколько пар)"""
import os, shutil, sys, zipfile, re
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A5, A7, C, PARTS_DIR, app, k5, qi

NAMES = ["УКП.03.001 Ползун.m3d", "УКП.03.002 Головка ползуна.m3d"]
args = sys.argv[1:]
for v25, v24 in zip(args[::2], args[1::2]):
    os.makedirs(v25, exist_ok=True); os.makedirs(v24, exist_ok=True)
    for n in NAMES:
        shutil.copyfile(os.path.join(PARTS_DIR, n), os.path.join(v25, n))
        d = app.Documents.Open(os.path.join(v25, n), False, False)
        d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
        dst = os.path.join(v24, n)
        if os.path.exists(dst): os.remove(dst)
        assert d5.SaveAsEx(dst, 30), dst
        d.Close(0)
        with zipfile.ZipFile(dst) as z:
            info = next((z.read(x).decode("utf-8", "ignore") for x in z.namelist() if "FileInfo" in x), "")
        ver = re.search(r"AppFullVersion[^0-9]*([0-9.]+)", info)
        print(n, "→ v24:", ver.group(1) if ver else "?")
