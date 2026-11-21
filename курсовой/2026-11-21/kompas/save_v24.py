# -*- coding: utf-8 -*-
"""21.11 (Корнеев А.Е.: у него КОМПАС-3D v24 Учебная): копия «Сборка/Модели КОМПАС» в формате v24 —
«Сборка/Модели КОМПАС v24». Сначала папка копируется целиком (ссылки сборок на детали относительные — Детали\\…), затем
каждая деталь и сборка пересохраняются на месте ksDocument3D.SaveAsEx(путь, 30) — режим 30 = формат v24 (проверено по
FileInfo: MathFileVersion 0x18000001, AppFullVersion 24.0). Проверка: версия каждого файла и пути деталей в сборках.
    python save_v24.py"""
import os, shutil, sys, zipfile
sys.stdout.reconfigure(encoding="utf-8")
from kompas_build import A5, A7, C, HERE, app, k5, qi

SRC = os.path.join(HERE, "..", "Сборка", "Модели КОМПАС")
DST = os.path.join(HERE, "..", "Сборка", "Модели КОМПАС v24")
MODE_V24 = 30
if os.path.exists(DST):
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)
for i in reversed(range(app.Documents.Count)):
    x = app.Documents.Item(i)
    if x is not None:
        qi(x, A7.IKompasDocument).Close(0)


def resave(path):
    d = app.Documents.Open(path, False, False)
    d5 = A5.ksDocument3D(k5.TransferInterface(d, C.ksAPI5Auto, 0))
    assert d5.SaveAsEx(path, MODE_V24), path
    d.Close(0)


def version(path):
    t = zipfile.ZipFile(path).read("FileInfo").decode("utf-16")
    return next(l.split("=")[1] for l in t.splitlines() if l.startswith("AppFullVersion"))


parts = sorted(os.path.join(DST, "Детали", f) for f in os.listdir(os.path.join(DST, "Детали")) if f.endswith(".m3d"))
asms = sorted(os.path.join(DST, f) for f in os.listdir(DST) if f.endswith(".a3d"))
for p in parts + asms:
    resave(p)
bad = [(os.path.basename(p), version(p)) for p in parts + asms if version(p) != "24.0"]
assert not bad, bad
for a in asms:                                     # детали сборки — из новой папки
    d = app.Documents.Open(a, False, False)
    top = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart
    n = top.Parts.Count
    paths = {os.path.normcase(os.path.dirname(qi(top.Parts.Part(i), A7.IPart7).FileName)) for i in range(n)}
    d.Close(0)
    assert paths == {os.path.normcase(os.path.join(os.path.abspath(DST), "Детали"))}, (os.path.basename(a), paths)
    print(f"{os.path.basename(a)}: {n} деталей — из «Модели КОМПАС v24\\Детали»")
print(f"формат v24: {len(parts)} деталей, {len(asms)} сборки → {os.path.abspath(DST)}")
