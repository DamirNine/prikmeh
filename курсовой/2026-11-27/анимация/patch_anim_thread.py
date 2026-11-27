# -*- coding: utf-8 -*-
"""27.11 (пользователь): головка ползуна — на резьбе Ø8,3 × 2 вместо клея. В анимации шаг 9: головку подносят снизу и
наворачивают на резьбовой конец штока (10 мм резьбы — 5 оборотов), тюбик клея не показывается. Детали — из STL 2026-11-21
(polzun_thread.py). Запуск: python patch_anim_thread.py && python build_anim.py"""
import io, os
HERE = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(HERE, "anim_template.html")
s = io.open(fn, encoding="utf-8").read()
i = s.index('  { t: "Головка на клей"'); j = s.index("\n", i)
pairs = [(s[i:j], '  { t: "Головка на резьбу", d: "Наверните головку снизу на резьбовой конец штока (резьба Ø8,3 × 2 мм) до упора, конусом вниз — '
                  'от руки, без клея. Ставится последней: головка шире отверстия полки, после неё ползун из направляющей не вынуть. Чтобы разобрать, '
                  'головку просто откручивают.", dur: 4.6, hl: ["head"], tag: "Головка" },'),
         ("head: { o: +(n >= 9), dy: 0 },", "head: { o: +(n >= 9), dy: 0, spin: 0 },"),
         ('''  (S, t) => { S.head.o = seg(t, 0, .1); S.head.dy = -70 * (1 - ease(seg(t, .62, 1)));          // клей в гнездо, затем головку — на хвостовик
              S.glue.o = Math.min(seg(t, .08, .16), 1 - seg(t, .52, .6));
              S.glue.k = 1 - ease(seg(t, .08, .28)) + ease(seg(t, .48, .6));
              S.glue.drop = seg(t, .3, .46); S.glue.pud = seg(t, .42, .47) * (1 - seg(t, .94, 1)); },''',
          '''  (S, t) => { S.head.o = seg(t, 0, .12);                 // снизу до начала резьбы, затем 10 мм наворачивания: оборот на 2 мм
              const dy = t < .32 ? 10 + 60 * (1 - ease(seg(t, .04, .32))) : 10 * (1 - ease(seg(t, .32, 1)));
              S.head.dy = -dy; S.head.spin = -2 * Math.PI * Math.min(dy, 10) / 2; },'''),
         ("  P.head.grp.position.set(E, y + S.polzun.dy + S.head.dy, S.polzun.dz);       // головка — в системе координат ползуна",
          "  P.head.grp.position.set(E, y + S.polzun.dy + S.head.dy, S.polzun.dz);       // головка — в системе координат ползуна\n"
          "  P.head.grp.rotation.y = S.head.spin;                                         // наворачивание вокруг оси штока")]
for a, b in pairs:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
io.open(fn, "w", encoding="utf-8").write(s)
print("ok")
