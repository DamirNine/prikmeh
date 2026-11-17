# -*- coding: utf-8 -*-
"""Эскиз вала ДЗ-1 (A2, М 1:1) в КОМПАС-3D v25 Study через API5: главный вид, вынесенное сечение А–А шейки под ключ,
размеры, шероховатости, технические требования. Размеры — из calc.json. Результат: КОМПАС/Эскиз вала.cdw + .png"""
import json, math, os, sys
import pythoncom
from win32com.client import GetActiveObject, gencache
from PIL import ImageFont

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "КОМПАС")
R = json.load(open(os.path.join(HERE, "calc.json"), encoding="utf-8"))
BIN = r"C:\Program Files\ASCON\KOMPAS-3D v25 Study\Bin"


def mod(tlb):
    a = pythoncom.LoadTypeLib(os.path.join(BIN, tlb)).GetLibAttr()
    return gencache.EnsureModule(str(a[0]), a[1], a[3], a[4])


C, A5, A7 = mod("ksConstants.tlb").constants, mod("kAPI5.tlb"), mod("kAPI7.tlb")
k5 = A5.KompasObject(GetActiveObject("Kompas.Application.5")._oleobj_.QueryInterface(A5.KompasObject.CLSID,
                                                                                     pythoncom.IID_IDispatch))
app = A7.IApplication(GetActiveObject("Kompas.Application.7")._oleobj_.QueryInterface(A7.IApplication.CLSID,
                                                                                      pythoncom.IID_IDispatch))
qi = lambda obj, cls: cls(obj._oleobj_.QueryInterface(cls.CLSID, pythoncom.IID_IDispatch))
FONT = "GOST Type AU"
_PIL = ImageFont.truetype(os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "GOST_AU.ttf"), 1000)
MAIN, THIN, AXIAL = 1, 2, 3
CDW = os.path.join(OUT, "Эскиз вала.cdw")

for i in reversed(range(app.Documents.Count)):          # старая копия эскиза — закрыть (иначе SaveAs не перезапишет)
    d7 = app.Documents.Item(i)
    if os.path.normcase(d7.PathName) == os.path.normcase(CDW):
        d7.Close(0)

dp = A5.ksDocumentParam(k5.GetParamStruct(35)); dp.Init(); dp.type = 1
sp = A5.ksSheetPar(dp.GetLayoutParam()); sp.Init(); sp.shtType = 1
st = A5.ksStandartSheet(sp.GetSheetParam()); st.Init(); st.format, st.multiply, st.direct = 2, 1, True   # A2 альбомный (на A3 сечение не помещалось)
d = k5.Document2D()
assert d.ksCreateDocument(dp), "чертёж не создан"


def width(s, h):
    return h * (1.432 * _PIL.getlength(s) / 1000.0 + 0.34)


def text(x, y, s, h=5.0, align="l", ang=0.0):
    if align != "l":
        x -= width(s, h) / 2 if align == "c" else width(s, h)
    par = A5.ksParagraphParam(k5.GetParamStruct(27)); par.Init()
    par.x, par.y, par.ang, par.width, par.height, par.hFormat, par.vFormat = x, y, ang, 0.0, 0.0, 0, 0
    d.ksParagraph(par)
    line = A5.ksTextLineParam(k5.GetParamStruct(29)); line.Init()
    arr = line.GetTextItemArr()
    item = A5.ksTextItemParam(k5.GetParamStruct(31)); item.Init()
    f = A5.ksTextItemFont(item.GetItemFont()); f.Init(); f.fontName, f.height, f.ksu = FONT, h, 1.0
    item.SetItemFont(f); item.s, item.type = s, 0
    A5.ksDynamicArray(arr).ksAddArrayItem(-1, item)
    line.SetTextItemArr(arr); d.ksTextLine(line)
    return d.ksEndObj()


def seg(x1, y1, x2, y2, s=MAIN):
    d.ksLineSeg(float(x1), float(y1), float(x2), float(y2), s)


def poly(pts, s=MAIN, closed=False):
    pts = list(pts) + ([pts[0]] if closed else [])
    for a, b in zip(pts, pts[1:]):
        seg(*a, *b, s)


def dim(x1, y1, x2, y2, vertical, off, diam=False):
    """линейный размер; off — смещение размерной линии от точек (по x для вертикального, по y для горизонтального)"""
    lp = k5.GetParamStruct(C.ko_LDimParam)
    dpp = lp.GetDPar(); dpp.Init(); dpp.pt1 = dpp.pt2 = 1
    spp = lp.GetSPar(); spp.Init()
    spp.x1, spp.y1, spp.x2, spp.y2 = x1, y1, x2, y2
    spp.dx, spp.dy, spp.basePoint, spp.ps = (off, 0, 1, 1) if vertical else (0, off, 1, 0)
    tp = lp.GetTPar(); tp.Init(False); tp.bitFlag = 1; tp.sign = 1 if diam else 0
    lp.SetDPar(dpp); lp.SetSPar(spp); lp.SetTPar(tp)
    return d.ksLinDimension(lp)


def rough(x, y, val, up=True):
    """знак шероховатости (√ с полкой) на линии поверхности в точке (x, y): вершина знака — на поверхности"""
    s = 1 if up else -1
    h = 5.0
    seg(x - h * 0.6, y + s * h * 0.6, x, y, THIN)
    seg(x, y, x + h * 1.2, y + s * h * 2.0, THIN)
    seg(x + h * 1.2, y + s * h * 2.0, x + h * 1.2 + width(val, 3.5) + 2, y + s * h * 2.0, THIN)
    text(x + h * 1.2 + 1, y + s * h * 2.0 + (2.5 if up else -6.0), val, 3.5)   # у надписи непрозрачный фон — не на полку


def arrow(x1, y1, x2, y2, L=4.0, W=1.2):
    seg(x1, y1, x2, y2, THIN)
    ux, uy = (x2 - x1), (y2 - y1); n = math.hypot(ux, uy); ux, uy = ux / n, uy / n
    bx, by = x2 - ux * L, y2 - uy * L
    poly([(bx - uy * W, by + ux * W), (x2, y2), (bx + uy * W, by - ux * W)], THIN, closed=True)


# ------------------------------------------------------------------ главный вид (М 1:1, ось горизонтальна)
d1, d2, d3, d4 = R["d"]; L1, L2, L3, L4 = R["L"]; Ls, S = R["Ls"], R["S"]
Rh = S / math.sqrt(3)                       # сторона = радиус описанной окружности шестигранника
X0, YA = 50.0, 270.0                        # левый торец (шейка 1) и ось
xs = [X0, X0 + L1, X0 + L1 + L2, X0 + L1 + L2 + L3, X0 + L1 + L2 + L3 + Ls, X0 + R["L_total"]]
half = [d1 / 2, d2 / 2, d3 / 2, S / 2, d4 / 2]   # шестигранник — гранями вверх/вниз: на виде высота ±S/2
top = []
for i in range(5):
    top += [(xs[i], YA + half[i]), (xs[i + 1], YA + half[i])]
outline = [(xs[0], YA)] + top + [(xs[5], YA)]
poly(outline)
poly([(x, 2 * YA - y) for x, y in outline])
for i in range(1, 5):                       # уступы (вертикальные линии на всю высоту большей ступени)
    hh = max(half[i - 1], half[i]); seg(xs[i], YA - hh, xs[i], YA + hh)
seg(xs[0], YA - half[0], xs[0], YA + half[0]); seg(xs[5], YA - half[4], xs[5], YA + half[4])
seg(xs[3], YA, xs[4], YA)                   # ребро шестигранника (вершина к наблюдателю) — по оси
seg(xs[0] - 6, YA, xs[5] + 6, YA, AXIAL)

# диаметры (кроме шестигранника)
for i, xx in ((0, xs[0] + 18), (1, xs[1] + 22), (2, xs[2] + 14), (4, xs[4] + 18)):
    dim(xx, YA + half[i], xx, YA - half[i], True, 0.0, diam=True)
# длины: цепочка + общий размер
yb = YA - S / 2
for i in range(5):
    dim(xs[i], YA - half[i], xs[i + 1], YA - half[i], False, (yb - 26) - (YA - half[i]))
dim(xs[0], YA - half[0], xs[5], YA - half[4], False, (yb - 40) - (YA - half[0]))

# шероховатость: Rz1 (шейка 1), Rz2 (шейка 2), Rz4 (шейка 4), Rz* (грань под ключ — сверху, «на ребро»)
Rz = R["Rz"]
rough(xs[0] + 32, YA + half[0], f"Rz {Rz['Rz1']}")
rough(xs[1] + 45, YA + half[1], f"Rz {Rz['Rz2']}")
rough(xs[4] + 30, YA + half[4], f"Rz {Rz['Rz4']}")

# линия сечения А–А по середине шейки под ключ
xc = (xs[3] + xs[4]) / 2
for yy, sgn in ((YA + S / 2 + 6, 1), (YA - S / 2 - 6, -1)):
    seg(xc, yy, xc, yy + sgn * 8, MAIN)
    arrow(xc, yy + sgn * 6, xc + 9, yy + sgn * 6)
    if sgn > 0:
        text(xc + 4, yy + 9.5, "А", 5.0)
    else:
        text(xc + 11, yy - 8.5, "А", 5.0)

# ------------------------------------------------------------------ сечение А–А (вынесенное)
XC, YC = 470.0, YA
hexp = [(XC + Rh * math.cos(math.radians(60 * k)), YC + Rh * math.sin(math.radians(60 * k))) for k in range(6)]  # грани сверху/снизу
d.ksHatch(0, 45.0, 3.0, 0.0, 0.0, 0.0)
d.ksPolyline(MAIN)
for x, y in hexp + [hexp[0]]:
    d.ksPoint(x, y, 0)
d.ksEndObj()
hatch_ok = d.ksEndObj()
poly(hexp, MAIN, closed=True)
seg(XC - Rh - 5, YC, XC + Rh + 5, YC, AXIAL); seg(XC, YC - S / 2 - 5, XC, YC + S / 2 + 5, AXIAL)
text(XC, YC + S / 2 + 18, "А–А", 7.0, "c")
dim(XC + Rh / 2, YC + S / 2, XC + Rh / 2, YC - S / 2, True, Rh / 2 + 10)          # S* = 110 (под ключ)
dim(XC - Rh, YC, XC + Rh, YC, False, -(S / 2 + 12))                            # 127,02 — справочный (по вершинам)
rough(XC - 18, YC + S / 2, f"Rz {Rz['Rzs']}")

# ------------------------------------------------------------------ технические требования
ty = 150
for s in ["1. Размер 127,02 — для справок (по вершинам шестигранника).",
          f"2. Материал — сталь {R['material']}.",
          "3. Неуказанные предельные отклонения размеров: валов h14,",
          "    остальных ± IT14/2."]:
    text(50, ty, s, 5.0); ty -= 8

# основная надпись: через API7 (если в Study не применится — заполнить вручную)
stamp_ok = False
try:
    d7 = qi(k5.TransferInterface(d, C.ksAPI7Dual, 0), A7.IKompasDocument2D)
    stamp = qi(d7, A7.IKompasDocument).LayoutSheets.Item(0).Stamp
    for col, s in ((1, "Вал (эскиз)"), (2, "ДЗ1.ПТП.001"), (3, f"Сталь {R['material']}"), (6, "1:1"),
                   (110, "Девяткин Д. А."), (9, "МГТУ им. Н. Э. Баумана")):
        stamp.Text(col).Str = s
    stamp_ok = stamp.Update()
except Exception as e:                        # noqa: BLE001
    print("штамп:", e)

d.ksSaveDocument(CDW)
rp = d.RasterFormatParam()
rp.format, rp.extResolution, rp.extScale, rp.colorBPP, rp.greyScale, rp.multiPageOutput = 3, 150, 1.0, 8, True, False
png = os.path.join(OUT, "Эскиз вала.png")
print("hatch", hatch_ok, "stamp", stamp_ok, "png", d.SaveAsToRasterFormat(png, rp))
d.ksCloseDocument()
print(CDW)
