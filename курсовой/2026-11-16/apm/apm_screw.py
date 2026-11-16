# -*- coding: utf-8 -*-
"""Копия установочного винта М10 × 10 для APM FEM (16.11, просьба пользователя: «сделай визуальную резьбу»): гладкий
цилиндр Ø10 с условным изображением резьбы М10 × 1,5 вместо витков (у рабочего винта под печать — витки), шестигранник S5.
Цилиндр разделён линией разъёма плоскостью z = −6 (граница пластины направляющей и стойки):
  верх z 0…−6   — в резьбе пластины направляющей: сюда сила F = 2061 Н вдоль оси наружу (+z) — отрыв направляющей;
  низ  z −6…−10 — в резьбе глухого отверстия стойки: закрепление.
Сила: ползун давит на правую планку R30N = 1671 Н на высоте z = 34 мм; направляющая опрокидывается вокруг правого нижнего
края пластины (x = e + 24,5, z = −6), боковую силу держит стенка выемки (z ≈ −3): T = 1671 · (34 + 3) / 30 = 2061 Н
(30 мм — от винта до края). Срез винт не несёт: зазор пластины в выемке 0,2 мм меньше радиального зазора в резьбе.
Файл — apm/Детали/«Винт установочный М10 × 10 (APM).m3d» (светлый, как остальные копии для APM).
    python apm_screw.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kompas"))
sys.stdout.reconfigure(encoding="utf-8")
from math import cos, sin, radians, pi
from kompas_build import A7, C, C3, SCR_HEX_S, SCR_HEX_T, SCR_L, ST45, Part, k5, qi

DET = os.path.join(HERE, "Детали"); os.makedirs(DET, exist_ok=True)
PATH = os.path.join(DET, "Винт установочный М10 × 10 (APM).m3d")
assert not os.path.exists(PATH), "копия уже есть"
R, Z_SPLIT = 5.0, -6.0
LIGHT = "#b7c1cc"

p = Part("Винт установочный М10 × 10 ГОСТ 8878-84 (APM)", "", ST45, LIGHT)
prof = [(0, 0), (R - 0.5, 0), (R, -0.5), (R, -SCR_L + 1.0), (R - 1.0, -SCR_L), (0, -SCR_L)]
p.revolve(p.sketch_xz(lambda s: (s.contour([(r, -z) for r, z in prof]), s.axis(0, -5, 0, SCR_L + 5))))
rh = SCR_HEX_S / 2 / cos(radians(30))
p.cut(lambda s: s.poly_fixed([(rh * cos(radians(60 * k)), rh * sin(radians(60 * k))) for k in range(6)]), -SCR_HEX_T, 0.5)   # шестигранник S5
p.thread(0.0, R, -0.5, 8.376, 1.5)                # условная резьба М10 × 1,5 (d1 = 8,376) — от верхнего кругового ребра

top = qi(k5.TransferInterface(p.doc, C.ksAPI7Dual, 0), A7.IKompasDocument3D).TopPart


def face_at(x, y, z):
    fs = [o for o in (qi(q, A7.IModelObject) for q in (top.FindObjectsByPoint(x, y, z, True) or ())) if o.ModelObjectType == C3.o3d_face]
    assert len(fs) == 1, ((x, y, z), len(fs))
    return fs[0]


sl = qi(top, A7.IAuxiliaryGeomContainer).SplitLines.Add()
sl.CutObjects = [qi(k5.TransferInterface(p.plane_z(Z_SPLIT), C.ksAPI7Dual, 0), A7.IModelObject)]
sl.Faces = [face_at(0.0, R, -3.0)]
assert sl.Update() and sl.Valid, "линия разъёма не построена"
sl.Name = "Граница пластина / стойка (z = −6)"
sl.Update()
up, low = face_at(0.0, R, -3.0), face_at(0.0, R, -8.0)
assert str(up.Reference) != str(low.Reference), "цилиндр не разделился"
a_up, a_low = (qi(f, A7.IFace).GetArea(1) for f in (up, low))
assert abs(a_up - 2 * pi * R * 5.5) < 0.5 and abs(a_low - 2 * pi * R * 3.0) < 0.5, (a_up, a_low)
bad = [f.Name for f in (qi(x, A7.IFeature7) for x in qi(top, A7.IFeature7).SubFeatures(1, False, False)) if not f.Valid and not f.Excluded]
assert not bad, bad
o = p.p.GetDefaultEntity(C3.o3d_pointCS); o.hidden = True; o.Update()
p.p.SetAdvancedColor(0xccc1b7, 0.5, 0.6, 0.8, 0.8, 1.0, 0.5)
for t in (C3.o3d_planeXOY, C3.o3d_planeXOZ, C3.o3d_planeYOZ):
    pl = p.p.GetDefaultEntity(t); pl.hidden = True; pl.Update()
for sk in p.sketches:
    sk.hidden = True; sk.Update()
p.p.Update()
mass = qi(top, A7.IMassInertiaParam7).Mass
p.doc.SaveAs(PATH)
p.doc.close()
print(f"сохранено: {os.path.relpath(PATH, HERE)}; масса {mass:.2f} г")
print(f"  верх (в пластине, сила 2061 Н по оси наружу): {a_up:.1f} мм²; низ (в стойке, закрепление): {a_low:.1f} мм²")
