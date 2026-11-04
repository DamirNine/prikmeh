# -*- coding: utf-8 -*-
"""3D-модель v21 (04.11) из 3d_model_v20.html по расчёту кинематических пар (п. 12.6 v21): распорная втулка оси O Ø16
заменена ступицей Ø16 × 12, приваренной к кулисе (вращается вместе с ней); палец D Ø10 проходит через отверстие
направляемой части ползуна на всю её толщину 16 мм."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, "..", "2026-11-02", "3d_model_v20.html"), encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:90]
    s = s.replace(a, b)


rep("Размеры по расчёту v17:", "Размеры по расчёту v21:")
rep("чтобы не задевать распорную втулку оси Ø16.",
    "чтобы не задевать ступицу кулисы Ø16 у оси O. Ось O и палец D — Ø10; ступица Ø16 × 12 приварена к кулисе и удлиняет "
    "отверстие под ось до 20 мм (расчёт на смятие).")
rep('<li><span class="swatch" style="background:#232a33"></span>Кулиса с рукоятью (полоса 8×18)</li>',
    '<li><span class="swatch" style="background:#232a33"></span>Кулиса с рукоятью (полоса 8×18, ступица Ø16 у оси O)</li>')
rep("var PIN_R = 5*MM;                                  // палец D (размер уточняется при моделировании)",
    "var PIN_R = 5*MM;                                  // палец D Ø10 (срез и смятие — п. 12.6)")
rep("var BUSH_R = 8*MM;                                 // распорная втулка оси O Ø16",
    "var BUSH_R = 8*MM;                                 // ступица кулисы Ø16 × 12 у оси O (вместо распорной втулки)")
rep("полоса кулисы · втулка оси · стойка", "полоса кулисы · ступица кулисы · стойка")
rep("// стойка, ось O с распорной втулкой", "// стойка и ось O Ø10, запрессованная в стойку")
rep("  rodBetween(new THREE.Vector3(O.x, O.y, STAND_FRONT), new THREE.Vector3(O.x, O.y, STRIP_BACK - 0.5*MM), BUSH_R, matMetalCool);\n", "")
rep("grip.rotation.z = Math.PI/2; grip.position.set(L_ - 0.50, 0, KZ); grip.castShadow = true; link1.add(grip);",
    "grip.rotation.z = Math.PI/2; grip.position.set(L_ - 0.50, 0, KZ); grip.castShadow = true; link1.add(grip);\n"
    "  // ступица Ø16 × 12 приварена к полосе с тыльной стороны соосно отверстию: длина отверстия под ось 8 + 12 = 20 мм\n"
    "  rodBetween(new THREE.Vector3(0, 0, STAND_FRONT + 0.5*MM), new THREE.Vector3(0, 0, STRIP_BACK + 0.001), BUSH_R, matMetalDark, link1);")
rep("// Губки стоят в той же глубине, что и распорная втулка оси O,", "// Губки стоят в той же глубине, что и ступица кулисы у оси O,")
rep("без укорочения угол губки вошёл бы во втулку на 0,3 мм.", "без укорочения угол губки вошёл бы в ступицу на 0,3 мм.")
rep("// зазор от угла губки (у оси O, на внутренней кромке) до поверхности втулки, мм",
    "// зазор от угла губки (у оси O, на внутренней кромке) до поверхности ступицы, мм")
rep("'<span>губки — втулка оси O</span> '", "'<span>губки — ступица у оси O</span> '")
rep("rodBetween(new THREE.Vector3(0, 0, -BLK.z/2 + 0.005), new THREE.Vector3(0, 0, FW0 + 0.01), PIN_R, matAccent, kamen);   // палец D — заодно с обоймой",
    "rodBetween(new THREE.Vector3(0, 0, BLK.z/2 - 0.0005), new THREE.Vector3(0, 0, FW0 + 0.01), PIN_R, matAccent, kamen);   // палец D — заодно с обоймой, через отверстие ползуна")
assert "втулк" not in s.replace("вместо распорной втулки", ""), [l for l in s.splitlines() if "втулк" in l]
open(os.path.join(HERE, "3d_model_v21.html"), "w", encoding="utf-8").write(s)
print("ok")
