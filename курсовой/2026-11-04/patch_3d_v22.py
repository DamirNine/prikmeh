# -*- coding: utf-8 -*-
"""3D-модель v22 (04.11) из 3d_model_v21.html: изменения расчёта v21 видны в модели — ступица кулисы у оси O выделена
отдельным цветом и в легенде, на панели — блок «Что изменено»."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, "3d_model_v21.html"), encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:90]
    s = s.replace(a, b)


rep("Размеры по расчёту v21:", "Размеры по расчёту v22:")
rep('  <div class="read" id="read" aria-live="off"></div>',
    '  <p class="sub"><b>Что изменено по расчёту кинематических пар (п. 12.6):</b> 1) у оси O вместо отдельной распорной '
    'втулки — <b>ступица Ø16 × 12, приваренная к кулисе</b> (голубая, поворачивается вместе с кулисой): в полосе толщиной '
    '8 мм отверстие под ось сминалось бы (30,4 МПа при допускаемых 24), со ступицей отверстие длиной 20 мм — 12,2 МПа; '
    '2) <b>палец D Ø10 проходит через ползун насквозь</b> — отверстие длиной 16 мм, смятие 15,7 МПа. Узел виден по кнопке '
    '«Узел крупно».</p>\n'
    '  <div class="read" id="read" aria-live="off"></div>')
rep('<li><span class="swatch" style="background:#232a33"></span>Кулиса с рукоятью (полоса 8×18, ступица Ø16 у оси O)</li>',
    '<li><span class="swatch" style="background:#232a33"></span>Кулиса с рукоятью (полоса 8×18)</li>\n'
    '    <li><span class="swatch" style="background:#3d8fd1"></span>Ступица кулисы Ø16 × 12 у оси O</li>')
rep("  var allMats = [matMetalCool, matMetalDark, matAccent, matGlass, matCapDark, matGrip];",
    "  var matHub      = new THREE.MeshStandardMaterial({color:0x3d8fd1, metalness:0.5, roughness:0.35, side:THREE.DoubleSide});\n"
    "  var allMats = [matMetalCool, matMetalDark, matAccent, matGlass, matCapDark, matGrip, matHub];")
rep("BUSH_R, matMetalDark, link1);", "BUSH_R, matHub, link1);")
open(os.path.join(HERE, "3d_model_v22.html"), "w", encoding="utf-8").write(s)
print("ok")
