# -*- coding: utf-8 -*-
"""Копирует рабочие модели КОМПАС (детали с настоящей резьбой + сборку) в папку комплекта «Сборка/Модели КОМПАС».
Сборка ссылается на детали относительно себя (Детали\…) — копия открывается со своими деталями (проверено 16.11).
Бутылка — только для вида сборки, не печатается.
    python pack_models.py"""
import glob, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(HERE, "..", "Сборка", "Модели КОМПАС")
os.makedirs(os.path.join(DST, "Детали"), exist_ok=True)
for f in glob.glob(os.path.join(HERE, "Детали", "*.m3d")):
    shutil.copy2(f, os.path.join(DST, "Детали"))
shutil.copy2(os.path.join(HERE, "УКП.00.000 Укупориватель.a3d"), DST)
print("скопировано в", os.path.normpath(DST))
