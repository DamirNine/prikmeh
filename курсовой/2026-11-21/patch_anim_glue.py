# -*- coding: utf-8 -*-
"""21.11 (пользователь): в анимации — нанесение клея на шаге «Головка на клей» (тюбик подлетает к гнезду, капля стекает,
на торце остаётся клей, тюбик улетает, затем головка поднимается на хвостовик); ключ — S4,85 (габарит STL).
    python patch_anim_glue.py"""
import io, os
HERE = os.path.dirname(os.path.abspath(__file__))


def patch(fn, pairs):
    s = io.open(fn, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (fn, a[:70], s.count(a))
        s = s.replace(a, b)
    io.open(fn, "w", encoding="utf-8").write(s)


patch(os.path.join(HERE, "build_anim.py"), [
    ('''        "key": (27.66, 4.6, 77.66)}''', '''        "key": (27.80, 4.85, 77.80)}                     # 21.11: ключ S4,85 (было 4,6 — проворачивался в винте)'''),
])
patch(os.path.join(HERE, "anim_template.html"), [
    ('''  { t: "Головка на клей", d: "Нанесите клей в гнездо головки и наденьте её снизу на хвостовик штока до упора, конусом вниз. Клеится последней: головка шире отверстия полки, после неё ползун из направляющей не вынуть.", dur: 3.4, hl: ["head"], tag: "Головка" },''',
     '''  { t: "Головка на клей", d: "Капните клей (эпоксидный или суперклей) в гнездо головки и сразу наденьте её снизу на хвостовик штока до упора, конусом вниз; держите ровно, пока клей не схватится. Клеится последней: головка шире отверстия полки, после неё ползун из направляющей не вынуть.", dur: 5.6, hl: ["head"], tag: "Головка" },'''),
    ('''    washer: { o: +(n >= 8), dz: 0 }, nut: { o: +(n >= 8), dz: 0, spin: 0 }, head: { o: +(n >= 9), dy: 0 },''',
     '''    washer: { o: +(n >= 8), dz: 0 }, nut: { o: +(n >= 8), dz: 0, spin: 0 }, head: { o: +(n >= 9), dy: 0 },
    glue: { o: 0, k: 1, drop: 0, pud: 0 },                // тюбик клея: видимость, вынос (1 — далеко), капля 0…1, клей на торце'''),
    ('''  (S, t) => { S.head.o = seg(t, 0, .2); S.head.dy = -70 * (1 - ease(seg(t, .08, 1))); },        // головка снизу на хвостовик''',
     '''  (S, t) => { S.head.o = seg(t, 0, .1); S.head.dy = -70 * (1 - ease(seg(t, .62, 1)));          // клей в гнездо, затем головку — на хвостовик
              S.glue.o = Math.min(seg(t, .08, .16), 1 - seg(t, .52, .6));
              S.glue.k = 1 - ease(seg(t, .08, .28)) + ease(seg(t, .48, .6));
              S.glue.drop = seg(t, .3, .46); S.glue.pud = seg(t, .42, .47) * (1 - seg(t, .94, 1)); },'''),
    ('''// стол под основанием: мягкое светлое пятно''',
     '''// клей: тюбик (корпус, колпачок, носик), капля и клей на торце головки — только на шаге «Головка на клей»
const HEAD_TOP = -82.5;                                     // верхний торец головки в координатах ползуна
const glueMat = new THREE.MeshStandardMaterial({ color: 0xf2c14e, roughness: .2, metalness: 0, transparent: true, opacity: .92 });
const tube = new THREE.Group(); scene.add(tube);
const tubeMats = [new THREE.MeshStandardMaterial({ color: 0xeef1f5, roughness: .45, transparent: true }),
                  new THREE.MeshStandardMaterial({ color: 0x2f6fb3, roughness: .4, transparent: true })];
{ const body = new THREE.Mesh(new THREE.CylinderGeometry(6.5, 6.5, 34, 28), tubeMats[0]); body.position.y = 12 + 17;
  const capm = new THREE.Mesh(new THREE.CylinderGeometry(7, 7, 8, 28), tubeMats[1]); capm.position.y = 12 + 34 + 4;
  const noz = new THREE.Mesh(new THREE.ConeGeometry(6.5, 12, 28), tubeMats[0]); noz.rotation.x = Math.PI; noz.position.y = 6;
  tube.add(body, capm, noz); }
tube.rotation.z = -.5;                                      // корпус уходит вправо-вверх, носик — к гнезду
const drop = new THREE.Mesh(new THREE.SphereGeometry(2.1, 18, 12), glueMat); scene.add(drop);
const puddle = new THREE.Mesh(new THREE.CylinderGeometry(4.3, 4.3, .9, 24), glueMat); scene.add(puddle);
// стол под основанием: мягкое светлое пятно'''),
    ('''  P.head.grp.position.set(E, y + S.polzun.dy + S.head.dy, S.polzun.dz);       // головка — в системе координат ползуна''',
     '''  P.head.grp.position.set(E, y + S.polzun.dy + S.head.dy, S.polzun.dz);       // головка — в системе координат ползуна
  const hy = y + S.polzun.dy + S.head.dy + HEAD_TOP, G = S.glue;              // торец головки с гнездом
  tube.visible = G.o > .004; tubeMats.forEach(m => { m.opacity = G.o; m.depthWrite = G.o > .5; });
  tube.position.set(E + 70 * G.k, hy + 2 + 45 * G.k, S.polzun.dz + 30 * G.k);
  drop.visible = G.drop > 0 && G.drop < 1;
  drop.position.set(E, hy + 2 - 3.5 * G.drop, S.polzun.dz); drop.scale.setScalar(.4 + .6 * Math.min(1, G.drop * 3));
  puddle.visible = G.pud > .01; puddle.scale.set(G.pud, 1, G.pud); puddle.position.set(E, hy + .45, S.polzun.dz);'''),
    ('''{ c: [E, -80, 30], d: 420 }, VIEW_ALL,''', '''{ c: [E, -115, 30], d: 360 }, VIEW_ALL,'''),
])
print("ok")
