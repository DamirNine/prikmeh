# -*- coding: utf-8 -*-
"""3D-модели вала ДЗ-1 в КОМПАС-3D v25 Study через API (COM). Размеры — из calc.json.
1) «Вал — токарная часть.m3d» — только тело вращения (шейка под ключ — цилиндр D*), ЛСК на свободном торце шейки 1:
   по ней работает модуль «ЧПУ. Токарная обработка» (Часть 2).
2) «Вал.m3d» — полная деталь: те же ступени + шестигранник S* под ключ (для эскиза/иллюстраций).
Ось вала — ось Z детали; торец шейки 1 (свободный, не в патроне) — z = 0, вал идёт в +Z к патрону (как ЛСК у
преподавателя: начало на свободном торце, ось Z по оси вращения)."""
import json, math, os, subprocess, sys, time
import pythoncom, pywintypes, win32api, win32con, win32process
from win32com.client import GetActiveObject, gencache

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "КОМПАС")
os.makedirs(OUT, exist_ok=True)
R = json.load(open(os.path.join(HERE, "calc.json"), encoding="utf-8"))
BIN = r"C:\Program Files\ASCON\KOMPAS-3D v25 Study\Bin"


def mod(tlb):
    lib = pythoncom.LoadTypeLib(os.path.join(BIN, tlb))
    a = lib.GetLibAttr()
    return gencache.EnsureModule(str(a[0]), a[1], a[3], a[4])


C, C3 = mod("ksConstants.tlb").constants, mod("ksConstants3D.tlb").constants
A5, A7 = mod("kAPI5.tlb"), mod("kAPI7.tlb")


def wait_apps():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq kStudy.exe", "/NH", "/FO", "CSV"], capture_output=True).stdout
    h = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False,
                             int(out.decode("cp866").split('","')[1]))
    n, t_same = 0, time.time()
    while time.time() - t_same < 4:
        try:
            m = len(win32process.EnumProcessModulesEx(h, win32process.LIST_MODULES_ALL))
        except pywintypes.error:
            m = 0
        if m != n:
            n, t_same = m, time.time()
        time.sleep(0.5)
    win32api.CloseHandle(h)


def connect():
    try:
        GetActiveObject("Kompas.Application.5")
    except pythoncom.com_error:
        subprocess.Popen([os.path.join(BIN, "kStudy.Exe")])
        for _ in range(60):
            time.sleep(2)
            try:
                GetActiveObject("Kompas.Application.5"); break
            except pythoncom.com_error:
                pass
        wait_apps()
    k5 = A5.KompasObject(GetActiveObject("Kompas.Application.5")._oleobj_.QueryInterface(A5.KompasObject.CLSID,
                                                                                         pythoncom.IID_IDispatch))
    app = A7.IApplication(GetActiveObject("Kompas.Application.7")._oleobj_.QueryInterface(A7.IApplication.CLSID,
                                                                                          pythoncom.IID_IDispatch))
    app.Visible = True
    return k5, app


k5, app = connect()
qi = lambda obj, cls: cls(obj._oleobj_.QueryInterface(cls.CLSID, pythoncom.IID_IDispatch))


class Sk:
    def __init__(self, d2):
        self.d2 = d2

    def cons(self, obj, kind, index=0, partner=0, pindex=0):
        cp = k5.GetParamStruct(C.ko_ConstraintParam); cp.Init()
        cp.constrType, cp.index, cp.partner, cp.partnerIndex = kind, index, partner, pindex
        assert self.d2.ksSetObjConstraint(obj, cp), ("ограничение не наложено", kind)

    def fixed_poly(self, pts):
        n = len(pts)
        seg = [self.d2.ksLineSeg(*pts[i], *pts[(i + 1) % n], 1) for i in range(n)]
        for i in range(n):
            self.cons(seg[i], C.ksCMergePoints, 1, seg[(i + 1) % n], 0)
            self.cons(seg[i], C.ksCFixedPoint, 0)
        return seg

    def axis(self, x0, y0, x1, y1):
        a = self.d2.ksLineSeg(x0, y0, x1, y1, 3)
        self.cons(a, C.ksCFixedPoint, 0); self.cons(a, C.ksCFixedPoint, 1)

    def circle(self, xc, yc, r):
        c = self.d2.ksCircle(xc, yc, r, 1)
        self.cons(c, C.ksCFixedPoint, 0)
        rp = k5.GetParamStruct(C.ko_RDimParam)
        dp = rp.GetDPar(); dp.Init(); dp.pt1 = dp.pt2 = 1
        sp = rp.GetSPar(); sp.Init(); sp.xc, sp.yc, sp.rad = xc, yc, r
        tp = rp.GetTPar(); tp.Init(False); tp.bitFlag = 1; tp.sign = 1
        rp.SetDPar(dp); rp.SetSPar(sp); rp.SetTPar(tp)
        o = qi(k5.TransferReference(self.d2.ksDiamDimension(rp), self.d2.reference), A7.IDrawingObject1)
        assert o.Associate()
        cc = qi(o.NewConstraint(), A7.IParametriticConstraint); cc.ConstraintType = C.ksCFixedDim
        assert cc.Create()


class Part:
    def __init__(self, name, marking):
        self.doc = k5.Document3D(); self.doc.Create(False, True)
        self.p = self.doc.GetPart(C3.pTop_Part)
        self.p.name, self.p.marking = name, marking
        self.p.SetMaterial(R["material"], 7.8)
        self.first, self.sketches = True, []

    def sketch(self, plane, draw):
        sk = self.p.NewEntity(C3.o3d_sketch)
        d = sk.GetDefinition(); d.SetPlane(plane); sk.Create()
        try:
            draw(Sk(d.BeginEdit()))
        finally:
            d.EndEdit()
        self.sketches.append(sk)
        return sk

    def plane_z(self, z):
        pl = self.p.NewEntity(C3.o3d_planeOffset)
        d = pl.GetDefinition(); d.SetPlane(self.p.GetDefaultEntity(C3.o3d_planeXOY))
        d.offset, d.direction = abs(z), z > 0
        pl.hidden = True; pl.Create()
        return pl

    def revolve(self, sk):
        ent = self.p.NewEntity(C3.o3d_baseRotated if self.first else C3.o3d_bossRotated)
        d = ent.GetDefinition(); d.directionType = C3.dtNormal; d.SetSideParam(True, 360); d.SetSketch(sk)
        assert ent.Create(), "вращение не построено"
        self.first = False

    def cut(self, sk, depth):
        ex = self.p.NewEntity(C3.o3d_cutExtrusion)
        d = ex.GetDefinition(); d.directionType = C3.dtReverse     # dtNormal уводил вырез в −z (масса не менялась)
        d.SetSideParam(False, C3.etBlind, depth, 0, False); d.SetSketch(sk)
        assert ex.Create(), "вырез не построен"

    def lcs(self):
        """ЛСК в начале координат детали (свободный торец шейки 1), ось Z — по оси вала: API7, при неудаче — None"""
        try:
            d7 = qi(k5.TransferInterface(self.doc, C.ksAPI7Dual, 0), A7.IKompasDocument3D)
            aux = qi(d7.TopPart, A7.IAuxiliaryGeomContainer)
            cs = aux.LocalCoordinateSystems.Add()
            cs.X, cs.Y, cs.Z = 0.0, 0.0, 0.0
            cs.Name = "ЛСК ЧПУ (торец шейки 1)"
            ok = cs.Update()
            return ok
        except Exception as e:                    # noqa: BLE001
            print("  ЛСК через API не создана:", e)
            return None

    def save(self, fname):
        for t in (C3.o3d_planeXOY, C3.o3d_planeXOZ, C3.o3d_planeYOZ):
            pl = self.p.GetDefaultEntity(t); pl.hidden = True; pl.Update()
        self.p.Update()
        states = [qi(k5.TransferInterface(sk, C.ksAPI7Dual, 0), A7.ISketch).ConstraintsState for sk in self.sketches]
        path = os.path.join(OUT, fname)
        self.doc.SaveAs(path)
        d7 = qi(k5.TransferInterface(self.doc, C.ksAPI7Dual, 0), A7.IKompasDocument3D)
        mass = qi(d7.TopPart, A7.IMassInertiaParam7).Mass
        print(f"  {fname}: масса {mass/1000:.2f} кг, эскизы определены: {all(s == C.ksStateWellConstrained for s in states)}")
        return path


d1, d2, d3, d4 = R["d"]
L1, L2, L3, L4 = R["L"]
Ls, S, Dst = R["Ls"], R["S"], R["section"]["D_star"]
z1, z2, z3, z4 = L1, L1 + L2, L1 + L2 + L3, L1 + L2 + L3 + Ls
Lt = R["L_total"]
# профиль в эскизе на XOZ: (u, v) = (r, −z) — ось вращения = ось v эскиза = ось z детали
prof = [(0, 0), (d1 / 2, 0), (d1 / 2, -z1), (d2 / 2, -z1), (d2 / 2, -z2), (d3 / 2, -z2), (d3 / 2, -z3), (Dst / 2, -z3),
        (Dst / 2, -z4), (d4 / 2, -z4), (d4 / 2, -Lt), (0, -Lt)]


def body(p):
    p.revolve(p.sketch(p.p.GetDefaultEntity(C3.o3d_planeXOZ),
                       lambda s: (s.fixed_poly(prof), s.axis(0, 10, 0, -Lt - 10))))


# 1) токарная часть + ЛСК
p = Part("Вал (токарная часть)", "ДЗ1.ПТП.001")
body(p)
print("  ЛСК:", p.lcs())
f1 = p.save("Вал — токарная часть (для ЧПУ).m3d")
p.doc.close()

# 2) полная деталь с шестигранником
p = Part("Вал", "ДЗ1.ПТП.001")
body(p)
Rh = S / math.sqrt(3)                                      # радиус описанной окружности шестигранника (= сторона)
hexpts = [(Rh * math.cos(math.radians(90 + 60 * k)), Rh * math.sin(math.radians(90 + 60 * k))) for k in range(6)]
sk = p.sketch(p.plane_z(z3), lambda s: (s.fixed_poly(hexpts), s.circle(0, 0, Dst / 2 + 10)))
p.cut(sk, Ls)
f2 = p.save("Вал.m3d")
p.doc.close()
print("готово:", f1, f2, sep="\n  ")
