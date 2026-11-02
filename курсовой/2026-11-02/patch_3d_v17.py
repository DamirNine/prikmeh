# -*- coding: utf-8 -*-
"""3D-модель v17 (02.11) из 3d_model_v15.html (2026-10-26): обойма охватывает полосу со всех сторон (сзади губки 2,2 мм,
у оси O укорочены на 3 мм — не задевают распорную втулку Ø16), зазор губок до втулки на панели; кнопка «Человек» —
фигура 1750 мм у кухонной столешницы 850 мм, правая рука на рукояти (2-звенная обратная кинематика); #human — открыть с ней."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "2026-10-26", "3d_model_v15.html")
DST = os.path.join(HERE, "3d_model_v17.html")
s = open(SRC, encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:90]
    s = s.replace(a, b)


rep("""    --accent-soft:rgba(209,149,63,.16);
  }""", """    --accent-soft:rgba(209,149,63,.16);
    color-scheme:dark;
  }""")

rep("""  <p class="sub">Размеры по расчёту v13: e = 12,53 мм, рукоять 500 мм, окно кулисы 59,5° → 22,7° (ψ = 36,75°), ход ползуна 16 мм (зазор 10 + обжим 6). Кулиса — сплошная полоса 8×18 (Ст3сп), камень — обойма 20 мм снаружи кулисы; ползун ходит в направляющей на уровне пальца D, шток Ø8, головка Ø40 × 24. Движение — по закону ω(t) из расчёта.</p>""",
    """  <p class="sub">Размеры по расчёту v17: e = 12,53 мм, рукоять 500 мм, окно кулисы 59,5° → 22,7° (ψ = 36,75°), ход ползуна 16 мм (зазор 10 + обжим 6). Кулиса — полоса 8×18 (Ст3сп). Камень — обойма 20 мм, охватывает полосу со всех сторон: сзади губки заходят на рёбра на 2,2 мм и у оси O укорочены на 3 мм, чтобы не задевать распорную втулку оси Ø16. Ползун ходит в направляющей на уровне пальца D, шток Ø8, головка Ø40 × 24. Движение — по закону ω(t) из расчёта.</p>""")

rep("""      <span id="viewLabel">Узел крупно</span>
    </button>""", """      <span id="viewLabel">Узел крупно</span>
    </button>
    <button class="cut" id="humanBtn" aria-pressed="false">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="4.5" r="2.2"/><path d="M12 7.5 V15 M12 15 L8.5 21.5 M12 15 L15.5 21.5 M6.5 10 L12 9 L17.5 7"/></svg>
      <span id="humanLabel">Человек для масштаба</span>
    </button>""")

rep("""    <li><span class="swatch" style="background:#2e333b"></span>Ползун, головка / кронен-крышка</li>""",
    """    <li><span class="swatch" style="background:#2e333b"></span>Ползун, головка / кронен-крышка</li>
    <li><span class="swatch" style="background:#939fb0"></span>Человек 1750 мм у столешницы 850 мм</li>""")

rep("""  var PIN_R = 5*MM;                                  // палец D (размер уточняется при моделировании)""",
    """  var PIN_R = 5*MM;                                  // палец D (размер уточняется при моделировании)
  var BUSH_R = 8*MM;                                 // распорная втулка оси O Ø16
  var LIP_T = 2.5*MM, LIP_O = 2.2*MM, LIP_NOTCH = 3*MM;   // губки обоймы: толщина, заход на ребро, укорочение у оси O""")

rep("controls.maxDistance = 34;", "controls.maxDistance = 60;")

rep("""  rodBetween(new THREE.Vector3(O.x, O.y, STAND_FRONT), new THREE.Vector3(O.x, O.y, STRIP_BACK - 0.5*MM), 8*MM, matMetalCool);""",
    """  rodBetween(new THREE.Vector3(O.x, O.y, STAND_FRONT), new THREE.Vector3(O.x, O.y, STRIP_BACK - 0.5*MM), BUSH_R, matMetalCool);""")

rep("""  // звено 2: камень-обойма — верхняя и нижняя стенки на рёбрах полосы и передняя стенка; открыта к стойке
  var kamen = new THREE.Group(); model.add(kamen);
  (function(){
    var zf = FW1, zb = STRIP_BACK - 0.5*MM, depth = zf - zb, yOut = H_/2 + CL + TW;
    [1, -1].forEach(function(sg){
      addMesh(new THREE.BoxGeometry(LK, TW, depth), matAccent, 0, sg*(H_/2 + CL + TW/2), (zf + zb)/2, 0,0,0, kamen);
    });
    addMesh(new THREE.BoxGeometry(LK, 2*yOut, TW), matAccent, 0, 0, (FW0 + FW1)/2, 0,0,0, kamen);
  })();""", """  // звено 2: камень-обойма охватывает полосу со всех сторон — верхняя, нижняя и передняя стенки, сзади губки на рёбрах полосы.
  // Губки стоят в той же глубине, что и распорная втулка оси O, поэтому у оси O они укорочены на LIP_NOTCH:
  // в конце хода край обоймы подходит к оси на 3,58 мм, и без укорочения угол губки вошёл бы во втулку на 0,3 мм.
  var kamen = new THREE.Group(); model.add(kamen);
  var LIP_ZB = STRIP_BACK - CL, LIP_Z0 = LIP_ZB - LIP_T;
  (function(){
    var zf = FW1, zb = LIP_Z0, depth = zf - zb, yOut = H_/2 + CL + TW, lipH = LIP_O + CL, lipL = LK - LIP_NOTCH;
    [1, -1].forEach(function(sg){
      addMesh(new THREE.BoxGeometry(LK, TW, depth), matAccent, 0, sg*(H_/2 + CL + TW/2), (zf + zb)/2, 0,0,0, kamen);
      addMesh(new THREE.BoxGeometry(lipL, lipH, LIP_T), matAccent, LIP_NOTCH/2, sg*(H_/2 + CL - lipH/2), (LIP_Z0 + LIP_ZB)/2, 0,0,0, kamen);
    });
    addMesh(new THREE.BoxGeometry(LK, 2*yOut, TW), matAccent, 0, 0, (FW0 + FW1)/2, 0,0,0, kamen);
  })();
  // зазор от угла губки (у оси O, на внутренней кромке) до поверхности втулки, мм
  function lipGap(phi){ return (Math.hypot(E_/Math.cos(phi) - LK/2 + LIP_NOTCH, H_/2 - LIP_O) - BUSH_R)/MM; }""")

rep("""  var readEl = document.getElementById('read');
  function setPhi(phi){""", """  var readEl = document.getElementById('read'), curPhi = PHI_N;
  function setPhi(phi){
    curPhi = phi;
    if(humanOn) updateArm(phi);""")

rep("""    readEl.innerHTML = '<span>φ</span> ' + (phi*180/Math.PI).toFixed(1).replace('.', ',') + '°  ' +
                       '<span>ход</span> ' + travel.toFixed(1).replace('.', ',') + ' мм<br><span>' + phase + '</span>';""",
    """    readEl.innerHTML = '<span>φ</span> ' + (phi*180/Math.PI).toFixed(1).replace('.', ',') + '°  ' +
                       '<span>ход</span> ' + travel.toFixed(1).replace('.', ',') + ' мм<br><span>' + phase + '</span><br>' +
                       '<span>губки — втулка оси O</span> ' + lipGap(phi).toFixed(1).replace('.', ',') + ' мм';""")

HUMAN = r"""
  // ---------- человек для масштаба: рост 1750 мм, стоит у кухонной столешницы 850 мм, правая рука на рукояти ----------
  var TABLE_H = 8.5, FLOOR_Y = -TABLE_H, humanOn = false;
  var matHuman = new THREE.MeshStandardMaterial({color:0x939fb0, metalness:0.05, roughness:0.78});
  var matTable = new THREE.MeshStandardMaterial({color:0x3a434f, metalness:0.15, roughness:0.7});
  var scaleSet = new THREE.Group(); scaleSet.visible = false; scene.add(scaleSet);
  function part(geo, mat, parent, x, y, z){
    var m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; parent.add(m); return m;
  }
  // столешница 1200 × 750 × 40 под основанием, ножки до пола
  part(new THREE.BoxGeometry(12, 0.4, 7.5), matTable, scaleSet, 0, -0.2, -0.75);
  [[-5.5, -4.0], [5.5, -4.0], [-5.5, 2.5], [5.5, 2.5]].forEach(function(p){
    part(new THREE.BoxGeometry(0.5, TABLE_H - 0.4, 0.5), matTable, scaleSet, p[0], FLOOR_Y + (TABLE_H - 0.4)/2, p[1]);
  });
  // фигура в своих координатах: начало — пол между стопами, лицо в сторону −z; повёрнута лицом к укупоривателю (−x)
  // и стоит у торца столешницы против конца рычага, правое плечо — над плоскостью кулисы
  var human = new THREE.Group(); human.position.set(7.3, FLOOR_Y, 2.35); human.rotation.y = Math.PI/2; scaleSet.add(human);
  function seg(a, b, ra, rb){
    var d = new THREE.Vector3().subVectors(b, a), m = part(new THREE.CylinderGeometry(rb, ra, d.length(), 20), matHuman, human, 0, 0, 0);
    m.position.addVectors(a, b).multiplyScalar(0.5); m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.normalize()); return m;
  }
  function ball(p, r, sx, sy, sz){ var m = part(new THREE.SphereGeometry(r, 20, 14), matHuman, human, p.x, p.y, p.z); m.scale.set(sx || 1, sy || 1, sz || 1); return m; }
  var V = function(x, y, z){ return new THREE.Vector3(x, y, z); };
  [-1, 1].forEach(function(sg){                                                   // ноги: бедро, голень, стопа
    var hip = V(0.9*sg, 9.2, 0), knee = V(0.95*sg, 5.0, -0.1), ankle = V(1.0*sg, 0.75, 0.1);
    seg(hip, knee, 0.78, 0.56); ball(knee, 0.56); seg(knee, ankle, 0.54, 0.36);
    part(new THREE.BoxGeometry(0.9, 0.65, 2.5), matHuman, human, 1.0*sg, 0.33, -0.6);
  });
  var pelvis = part(new THREE.CylinderGeometry(1.45, 1.6, 1.6, 24), matHuman, human, 0, 9.6, 0); pelvis.scale.z = 0.66;
  var torso = part(new THREE.CylinderGeometry(1.8, 1.4, 4.4, 24), matHuman, human, 0, 12.4, 0); torso.scale.z = 0.6;
  var SH_L = V(-1.95, 14.25, 0), SH_R = V(1.95, 14.25, 0);
  ball(SH_L, 0.6); ball(SH_R, 0.6);
  seg(V(0, 14.4, 0), V(0, 15.5, 0), 0.5, 0.48);
  ball(V(0, 16.45, -0.05), 1.0, 0.85, 1.08, 0.98);                                 // голова, макушка ≈ 1750 мм
  var elL = V(-2.15, 11.15, 0.15), wrL = V(-2.2, 8.6, 0.0);                       // левая рука свободно опущена
  seg(SH_L, elL, 0.5, 0.42); ball(elL, 0.42); seg(elL, wrL, 0.4, 0.3); ball(V(-2.2, 8.0, -0.05), 0.45, 0.8, 1.4, 1.0);
  // правая рука: плечо 325 мм, предплечье 255 мм, от запястья до центра хвата 90 мм
  var UA = 3.25, FA = 2.55, HAND = 0.9, GRIP_OFF = V(0, 0.3, 0.05), POLE = V(0.8, -1.0, 0.25);
  function unitSeg(r){ var m = part(new THREE.CylinderGeometry(r, r, 1, 20), matHuman, human, 0, 0, 0); return m; }
  var upperArm = unitSeg(0.48), foreArm = unitSeg(0.36), elbowBall = ball(V(0, 0, 0), 0.42), handBall = ball(V(0, 0, 0), 0.45, 1.1, 0.75, 1.25);
  function place(m, a, b){
    var d = new THREE.Vector3().subVectors(b, a), len = d.length();
    m.position.addVectors(a, b).multiplyScalar(0.5); m.scale.set(1, len, 1); m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.divideScalar(len));
  }
  function updateArm(phi){
    var r = L_ - 0.50;                                                           // центр рукоятки-накладки
    scaleSet.updateMatrixWorld(true);
    var T = human.worldToLocal(V(O.x + r*Math.cos(phi), O.y + r*Math.sin(phi), KZ).add(GRIP_OFF));
    var d = new THREE.Vector3().subVectors(T, SH_R), b = FA + HAND, dist = Math.min(d.length(), UA + b - 1e-3); d.normalize();
    var pole = POLE.clone(); pole.sub(d.clone().multiplyScalar(pole.dot(d))).normalize();
    var ca = (UA*UA + dist*dist - b*b)/(2*UA*dist), sa = Math.sqrt(Math.max(0, 1 - ca*ca));
    var E = SH_R.clone().addScaledVector(d, UA*ca).addScaledVector(pole, UA*sa);
    var H = SH_R.clone().addScaledVector(d, dist);
    var W = E.clone().addScaledVector(new THREE.Vector3().subVectors(H, E).normalize(), FA);
    place(upperArm, SH_R, E); place(foreArm, E, W); elbowBall.position.copy(E); handBall.position.copy(H);
  }
  var VIEW_HUMAN = {pos: new THREE.Vector3(10, 4.5, 33), tgt: new THREE.Vector3(2.2, 0.2, 0.5)};
  function setHuman(state, instant){
    humanOn = state; scaleSet.visible = state;
    var gy = state ? FLOOR_Y : 0; ground.position.y = gy; gridHelper.position.y = gy + 0.001;
    scene.fog.near = state ? 45 : 20; scene.fog.far = state ? 110 : 42;
    var sc = key.shadow.camera;
    if(state){ sc.left = -16; sc.right = 18; sc.top = 24; sc.bottom = -16; sc.far = 80; }
    else { sc.left = -4; sc.right = 7; sc.top = 10; sc.bottom = -2; sc.far = 40; }
    sc.updateProjectionMatrix();
    if(state) updateArm(curPhi);
    nodeView = false;
    document.getElementById('viewBtn').setAttribute('aria-pressed', 'false');
    document.getElementById('viewLabel').textContent = 'Узел крупно';
    var v = state ? VIEW_HUMAN : VIEW_ALL;
    if(instant){ camera.position.copy(v.pos); controls.target.copy(v.tgt); controls.update(); } else flyTo(v);
    document.getElementById('humanBtn').setAttribute('aria-pressed', state ? 'true' : 'false');
  }
  document.getElementById('humanBtn').addEventListener('click', function(){ setHuman(!humanOn); });
  if(location.hash === '#human') setHuman(true, true);
"""

rep("""    nodeView = !nodeView; flyTo(nodeView ? VIEW_NODE : VIEW_ALL);""",
    """    nodeView = !nodeView; flyTo(nodeView ? VIEW_NODE : (humanOn ? VIEW_HUMAN : VIEW_ALL));""")

rep("""  var animOn = false, animT = 0, lastT = performance.now();""", HUMAN.lstrip("\n") + """  var animOn = false, animT = 0, lastT = performance.now();""")

open(DST, "w", encoding="utf-8").write(s)
print("saved", DST)
