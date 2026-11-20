# -*- coding: utf-8 -*-
"""21.11: 3D-анимация под направляющую-«стул» и ползун из двух частей — головка (6а) отдельной деталью, новый порядок шагов
(11 шагов: палец — после ползуна, ползун опускается сверху, головка клеится снизу). Пояснение про длинное плечо ключа убрано.
    python patch_anim_2111.py"""
import io, os
HERE = os.path.dirname(os.path.abspath(__file__))


def patch(fn, pairs):
    s = io.open(fn, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (fn, a[:70], s.count(a))
        s = s.replace(a, b)
    io.open(fn, "w", encoding="utf-8").write(s)


patch(os.path.join(HERE, "build_anim.py"), [
    ('''         ("polzun", "6 Ползун", "Ползун", "#3a4049"),''',
     '''         ("polzun", "6 Ползун", "Ползун", "#3a4049"), ("head", "6а Головка ползуна", "Головка ползуна", "#3a4049"),'''),
    ('''"polzun": (40.0, 136.65, 40.0),''', '''"polzun": (24.0, 112.5, 16.0), "head": (40.0, 34.15, 40.0),'''),
])

T = os.path.join(HERE, "anim_template.html")
s = io.open(T, encoding="utf-8").read()
a, b = s.index("const STEPS = ["), s.index("const N = STEPS.length;")
s = s[:a] + '''const STEPS = [
  { t: "Стойка", d: "Поставьте стойку основанием на стол. На ней уже есть ось O, два упора рукояти, выемка под направляющую с резьбовым отверстием М10 в дне и два зацепа для кожуха.", dur: 2.2, hl: ["stand"], tag: "Стойка" },
  { t: "Камень на кулису", d: "Наденьте камень на кулису с дальнего конца рукояти и сдвиньте к середине. Стенка камня с отверстием и втулка кулисы смотрят в разные стороны. Палец пока не ставится — он войдёт через ползун.", dur: 3.8, hl: ["kamen", "kulisa"], tag: "Камень" },
  { t: "Кулиса на ось O", d: "Сдвиньте камень к отверстию и наденьте кулису на ось O до упора в стойку: рукоять встаёт между упорами, отверстие камня смотрит вперёд.", dur: 4.4, hl: ["kulisa", "kamen"], tag: "Кулиса с камнем" },
  { t: "Направляющая", d: "Задвиньте направляющую спереди: пластину — в выемку стойки до дна, планки — по обе стороны от камня, полка с отверстием под шток — внизу. Резьбовые отверстия пластины и стойки встают соосно.", dur: 3.4, hl: ["guide"], tag: "Направляющая" },
  { t: "Винт М10", d: "Вверните установочный винт М10 × 10 ключом-шестигранником S5 (деталь 11) через пластину в стойку — до упора, заподлицо с площадкой. Винт держит направляющую в выемке. Ставится до ползуна — потом шток и брусок закроют к нему доступ.", dur: 3.8, hl: ["screw", "key"], tag: "Винт М10" },
  { t: "Ползун сверху", d: "Опустите ползун (брусок со штоком) сверху между планками направляющей: шток проходит в отверстие полки, брусок встаёт перед камнем, его отверстие — напротив отверстия камня.", dur: 3.6, hl: ["polzun"], tag: "Ползун" },
  { t: "Палец через ползун", d: "Вставьте палец гладким концом спереди через отверстие бруска ползуна в камень — до упора, резьба остаётся снаружи. В камне палец сидит туго, ползун на нём поворачивается свободно.", dur: 3.2, hl: ["pin"], tag: "Палец" },
  { t: "Шайба и гайка", d: "Наденьте шайбу на резьбовой конец пальца и навинтите гайку М10 до упора — дальше её не пустит конец резьбы. Шайба остаётся с зазором 0,5 мм, ползун свободно поворачивается на пальце.", dur: 3.6, hl: ["washer", "nut"], tag: "Шайба и гайка" },
  { t: "Головка на клей", d: "Нанесите клей в гнездо головки и наденьте её снизу на хвостовик штока до упора, конусом вниз. Клеится последней: головка шире отверстия полки, после неё ползун из направляющей не вынуть.", dur: 3.4, hl: ["head"], tag: "Головка" },
  { t: "Проверка хода", d: "Поднимите рукоять до верхнего упора и плавно опустите до нижнего: ползун идёт строго вертикально — брусок между планками, шток в полке; ход колокола — 16 мм.", dur: 4.6, hl: ["kulisa"], tag: "" },
  { t: "Кожух", d: "Поставьте рукоять посередине хода и надвиньте кожух спереди до листа стойки: паз — на рукоять, паз в дне — на шток. Крючки боковых язычков наезжают скосом на зацепы стойки, язычки отгибаются наружу и в конце защёлкиваются (нажим около 10 Н). Снять: отжать оба язычка и потянуть кожух вперёд.", dur: 3.2, hl: ["cover"], tag: "Кожух" }];
''' + s[b:]
a, b = s.index("function baseState(n) {"), s.index("const WCYC = [")
s = s[:a] + '''function baseState(n) {                                    // состояние после n выполненных шагов
  return { phi: PH0, hl: 0, hlKeys: [], bottle: null,
    stand: { o: +(n >= 1), dy: 0 },
    kamen: { o: +(n >= 2), s: n === 2 ? S_MID : null, dz: n === 2 ? DZ : 0 },
    kulisa: { o: +(n >= 2), dz: n === 2 ? DZ : 0 },
    guide: { o: +(n >= 4), dz: 0 }, screw: { o: +(n >= 5), dz: 0, spin: 0 }, key: { o: 0 },
    polzun: { o: +(n >= 6), dz: 0, dy: 0 }, pin: { o: +(n >= 7), dz: 0 },
    washer: { o: +(n >= 8), dz: 0 }, nut: { o: +(n >= 8), dz: 0, spin: 0 }, head: { o: +(n >= 9), dy: 0 },
    cover: { o: +(n >= 11), dz: 0 } };
}
const MOVE = [
  (S, t) => { S.stand.o = seg(t, 0, .45); S.stand.dy = 80 * (1 - ease(t)); },
  (S, t) => { S.kulisa.o = seg(t, 0, .25); S.kulisa.dz = DZ + 40 * (1 - ease(seg(t, 0, .3)));
              S.kamen.o = seg(t, .2, .4); S.kamen.s = lerp(S_FAR, S_MID, ease(seg(t, .35, 1))); S.kamen.dz = DZ; },
  (S, t) => { S.kamen.s = lerp(S_MID, sD(PH0), ease(seg(t, 0, .45))); S.kamen.dz = S.kulisa.dz = DZ * (1 - ease(seg(t, .45, 1))); },
  (S, t) => { S.guide.o = seg(t, 0, .22); S.guide.dz = DZ * (1 - ease(seg(t, .1, 1))); },
  (S, t) => { S.screw.o = seg(t, 0, .18);                 // подлёт спереди до входа в резьбу, затем 10 мм ввинчивания: оборот на 1,5 мм
              const dz = t < .38 ? 10 + 45 * (1 - ease(seg(t, .04, .38))) : 10 * (1 - ease(seg(t, .38, 1)));
              S.screw.dz = dz; S.screw.spin = 2 * Math.PI * Math.min(dz, 10) / 1.5;
              S.key.o = Math.min(seg(t, .02, .2), 1 - seg(t, .9, 1)); },   // ключ в гнезде винта, крутится вместе с ним
  (S, t) => { S.polzun.o = seg(t, 0, .2); S.polzun.dy = 150 * (1 - ease(seg(t, .08, 1))); },   // сверху, шток — в полку
  (S, t) => { S.pin.o = seg(t, 0, .2); S.pin.dz = 60 * (1 - ease(seg(t, .12, 1))); },          // спереди через ползун в камень
  (S, t) => { S.washer.o = seg(t, 0, .18); S.washer.dz = 60 * (1 - ease(seg(t, .05, .5)));
              S.nut.o = seg(t, .38, .55); const k = ease(seg(t, .42, 1)); S.nut.dz = 60 * (1 - k); S.nut.spin = 5 * Math.PI * (1 - k); },
  (S, t) => { S.head.o = seg(t, 0, .2); S.head.dy = -70 * (1 - ease(seg(t, .08, 1))); },        // головка снизу на хвостовик
  (S, t) => { S.phi = t < .28 ? lerp(PH0, PH_N, ease(t / .28)) : t < .75 ? lerp(PH_N, PH_K, ease((t - .28) / .47)) : lerp(PH_K, PH0, ease((t - .75) / .25)); },
  (S, t) => { S.cover.o = seg(t, 0, .22); S.cover.dz = 120 * (1 - ease(seg(t, .1, 1))); }];
''' + s[b:]
for x, y in [
    ('const HL = new THREE.Color(0xf2a900), DARK = { kulisa: 1, polzun: 1 }, P = {};',
     'const HL = new THREE.Color(0xf2a900), DARK = { kulisa: 1, polzun: 1, head: 1 }, P = {};'),
    ('''  // ключ: длинное плечо (вдоль +z ключа, 75 мм) — в гнезде S5 глубиной 5, угол — на 70 мм над торцом винта, впереди планок''',
     '''  // ключ: плечо 75 мм (вдоль +z ключа) — в гнезде S5 глубиной 5, угол — на 70 мм над торцом винта, впереди планок'''),
    ('''  P.polzun.grp.position.set(E, y, S.polzun.dz);''',
     '''  P.polzun.grp.position.set(E, y + S.polzun.dy, S.polzun.dz);
  P.head.grp.position.set(E, y + S.polzun.dy + S.head.dy, S.polzun.dz);       // головка — в системе координат ползуна'''),
    ('''  else if (i === 1) tagPos.copy(P.pin.grp.position).add(tmp.set(0, 6, 30));
  else if (i === 2) tagPos.copy(P.kamen.grp.position).add(tmp.set(0, 14, 8));
  else if (i === 3) tagPos.set(230 * c, 230 * s + 10, Z_KUL + S.kulisa.dz + 8);
  else if (i === 4) tagPos.set(E + 18, -48, Z_ST + S.guide.dz + 55);
  else if (i === 5) tagPos.copy(P.screw.grp.position).add(tmp.set(0, 9, 4));
  else if (i === 6) tagPos.set(E, y + 22, S.polzun.dz + 8);
  else if (i === 7) tagPos.copy(P.nut.grp.position).add(tmp.set(0, 11, 5));
  else if (i === 9) tagPos.set(16, 64, Z_ST + S.cover.dz + 58);''',
     '''  else if (i === 1) tagPos.copy(P.kamen.grp.position).add(tmp.set(0, 14, 8));
  else if (i === 2) tagPos.set(230 * c, 230 * s + 10, Z_KUL + S.kulisa.dz + 8);
  else if (i === 3) tagPos.set(E + 18, -48, Z_ST + S.guide.dz + 55);
  else if (i === 4) tagPos.copy(P.screw.grp.position).add(tmp.set(0, 9, 4));
  else if (i === 5) tagPos.set(E, y + S.polzun.dy + 22, S.polzun.dz + 8);
  else if (i === 6) tagPos.copy(P.pin.grp.position).add(tmp.set(0, 8, 30));
  else if (i === 7) tagPos.copy(P.nut.grp.position).add(tmp.set(0, 11, 5));
  else if (i === 8) tagPos.copy(P.head.grp.position).add(tmp.set(0, -100, 22));
  else if (i === 10) tagPos.set(16, 64, Z_ST + S.cover.dz + 58);'''),
    ('''const VIEWS = [{ c: [14, -135, 0], d: 1180 }, { c: [S_FAR * c0, S_FAR * s0, DZ + 12], d: 300 }, { c: [335 * c0, 335 * s0, DZ], d: 960 },
  { c: [150, 110, DZ / 2], d: 880 }, { c: [E, -30, 50], d: 620 }, { c: [SCR_X, SCR_Y, 10], d: 200, dir: [.15, .28, .95] }, { c: [E, -28, 62], d: 560 },
  { c: [E, yD(PH0), 36], d: 250 }, VIEW_ALL,
  VIEW_ALL];''',
     '''const VIEWS = [{ c: [14, -135, 0], d: 1180 }, { c: [335 * c0, 335 * s0, DZ], d: 960 },
  { c: [150, 110, DZ / 2], d: 880 }, { c: [E, -30, 50], d: 620 }, { c: [SCR_X, SCR_Y, 10], d: 200, dir: [.15, .28, .95] }, { c: [E, 0, 40], d: 640 },
  { c: [E, yD(PH0), 36], d: 260 }, { c: [E, yD(PH0), 36], d: 250 }, { c: [E, -80, 30], d: 420 }, VIEW_ALL,
  VIEW_ALL];'''),
]:
    assert s.count(x) == 1, (x[:70], s.count(x))
    s = s.replace(x, y)
io.open(T, "w", encoding="utf-8").write(s)
print("ok")
