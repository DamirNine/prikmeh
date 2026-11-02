# -*- coding: utf-8 -*-
"""3D-модель v20 (02.11) из 3d_model_v17.html: палец D — одна деталь с камнем-обоймой (цвет обоймы, группа камня),
как на рис. 12 расчёта v20."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, "3d_model_v17.html"), encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:90]
    s = s.replace(a, b)


rep("rodBetween(new THREE.Vector3(0, yk0, -BLK.z/2 + 0.005), new THREE.Vector3(0, yk0, FW0 + 0.01), PIN_R, matMetalCool, link3);   // палец D",
    "rodBetween(new THREE.Vector3(0, 0, -BLK.z/2 + 0.005), new THREE.Vector3(0, 0, FW0 + 0.01), PIN_R, matAccent, kamen);   // палец D — заодно с обоймой")
rep("Камень — обойма 20 мм, охватывает полосу со всех сторон:",
    "Камень — обойма 20 мм с пальцем D (одна деталь), охватывает полосу со всех сторон:")
rep('<li><span class="swatch" style="background:#d1953f"></span>Камень-обойма</li>',
    '<li><span class="swatch" style="background:#d1953f"></span>Камень-обойма с пальцем D</li>')
open(os.path.join(HERE, "3d_model_v20.html"), "w", encoding="utf-8").write(s)
print("ok")
