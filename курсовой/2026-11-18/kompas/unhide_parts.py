# -*- coding: utf-8 -*-
"""Детали, скопированные из APM-копий (prepare_parts.py), унаследовали скрытые тела: APM FEM прячет модель, пока показывает
карту результатов, и так сохраняет. Здесь у кулисы, ползуна, камня и пальца снова показываются все элементы тела
(эскизы, плоскости, оси, линии разъёма — скрываются). Запускать после prepare_parts.py, до kompas_assembly.py.
    python unhide_parts.py"""
import os
from kompas_build import A7, FILES, PARTS_DIR, app, qi

AUX = ("Эскиз", "Вспомогательная", "Плоскость", "Ось", "Начало", "Разбиение", "Линия разъёма", "Отверстие: верх", "Зона")

for k in ("kulisa", "polzun", "kamen", "pin"):
    p = os.path.join(PARTS_DIR, FILES[k])
    d = app.Documents.Open(p, True, False)
    assert d is not None, p
    top = qi(d, A7.IKompasDocument3D).TopPart
    shown = []
    for x in qi(top, A7.IFeature7).SubFeatures(1, False, False) or ():
        f, o = qi(x, A7.IFeature7), qi(x, A7.IModelObject)
        aux = f.Name.startswith(AUX)         # тело — показать; плоскости, оси, эскизы — скрыть (в APM-копиях их включали)
        o.Hidden = aux                       # ставится всегда: чтение Hidden после APM ненадёжно, проверка — по картинке
        o.Update()
        shown.append(f.Name) if aux else None
    qi(d, A7.IKompasDocument3D).RebuildDocument()
    d.Save()
    d.Close(0)
    print(f"  {FILES[k]}: скрыто вспомогательных {len(shown)}")
