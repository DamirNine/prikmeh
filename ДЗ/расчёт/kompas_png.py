# -*- coding: utf-8 -*-
"""PNG-картинки моделей вала (изометрия) для отчёта и проверки: КОМПАС/*.m3d -> КОМПАС/*.png"""
import os, sys
import pythoncom
from win32com.client import GetActiveObject, gencache

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "КОМПАС")
BIN = r"C:\Program Files\ASCON\KOMPAS-3D v25 Study\Bin"


def mod(tlb):
    a = pythoncom.LoadTypeLib(os.path.join(BIN, tlb)).GetLibAttr()
    return gencache.EnsureModule(str(a[0]), a[1], a[3], a[4])


A5, A7 = mod("kAPI5.tlb"), mod("kAPI7.tlb")
app = A7.IApplication(GetActiveObject("Kompas.Application.7")._oleobj_.QueryInterface(A7.IApplication.CLSID,
                                                                                      pythoncom.IID_IDispatch))
k5 = A5.KompasObject(GetActiveObject("Kompas.Application.5")._oleobj_.QueryInterface(A5.KompasObject.CLSID,
                                                                                     pythoncom.IID_IDispatch))
for name in sys.argv[1:] or ["Вал.m3d", "Вал — токарная часть (для ЧПУ).m3d"]:
    path = os.path.join(OUT, name)
    for i in reversed(range(app.Documents.Count)):  # открытые копии (в т.ч. устаревшие после перестроения) закрываем без сохранения
        d7 = app.Documents.Item(i)
        if os.path.normcase(d7.PathName) == os.path.normcase(path):
            d7.Close(0)
    doc = k5.Document3D()
    assert doc.Open(path, False), name             # всегда свежая версия с диска
    rp = doc.RasterFormatParam()
    rp.format, rp.extResolution, rp.colorBPP, rp.greyScale = 3, 150, 24, False
    png = os.path.join(OUT, os.path.splitext(name)[0] + ".png")
    print(name, "->", doc.SaveAsToRasterFormat(png, rp), png)
    doc.close()
