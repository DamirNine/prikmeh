# -*- coding: utf-8 -*-
r"""Встроенная анимация КОМПАС-3D (приложение «Механика: Анимация», Libs\Animation3D\Animat.rtw): рабочий ход и возврат
рукояти по закону ω(t) из п. 9 расчёта.

    python kompas_animation.py          — собрать копию сборки и сценарий;
    python kompas_animation.py --play   — открыть копию, запустить Анимацию, загрузить сценарий и воспроизвести.

Почему копия сборки: Анимация поворачивает кулису, а камень и ползун идут за ней по сопряжениям — кинематику считает КОМПАС.
Для этого сопряжение «Под углом» должно быть исключено из расчёта, иначе решатель возвращает кулису на место (флаги Mate в
XML этого не делают, они только запоминаются). В рабочей сборке это сопряжение нужно: оно ограничивает ход рукояти мышью.

Что требует Анимация от сценария (проверено на этой версии):
- ось вращения — только ось по цилиндрической поверхности, системная «Ось Z» и ось по двум плоскостям не принимаются;
- пробелы в имени оси записываются в XML подчёркиваниями: «Ось O» → Axis="Ось_O";
- XML в UTF-8 без BOM; Direct="1" — угол φ растёт (рукоять вверх), Direct="-1" — вниз;
- вращение в шаге идёт с постоянной скоростью, поэтому закон ω(t) задан ломаной: N_SEG шагов на ход;
- атрибут Cycle при загрузке не применяется: повтор включает галочка в окне настроек (set_cycle)."""
import os, shutil, subprocess, sys, time
from math import atan2, cos, degrees, radians, sin
import win32api, win32con, win32gui, win32process

from kompas_build import A5, A7, BIN, C, C3, E, HERE, PH_N, app, k5, qi, yD
from kompas_motion import ASM, SLOW_DEFAULT, T_STROKE, phi_work

ASM_ANIM = os.path.join(HERE, "УКП.00.000 Укупориватель (анимация).a3d")
XML = os.path.join(HERE, "Анимация механизма.xml")
RTW = os.path.join(os.path.dirname(BIN), "Libs", "Animation3D", "Animat.rtw")
AXIS = "Ось O"                                    # ось по цилиндру оси O стойки
PARTS = ["Стойка", "Кулиса", "Камень с пальцем D", "Ползун", "Кожух", "Бутылка"]
KULISA = PARTS.index("Кулиса")
N_SEG = 18                                        # участков ломаной на ход: отклонение от закона ω(t) меньше 0,1°
FRAMES = 24                                       # кадров в секунду
CMD_LOAD, CMD_PLAY, CMD_EXIT, CMD_SETTINGS, LIB_START = 32788, 32791, 32790, 32802, 2   # команды меню; 2 — запуск (Animat.xml)
CHK_CYCLE = 1024                                  # «Циклическое воспроизведение» в окне настроек
BTN_PLAY, BTN_BACK = 1008, 1069                   # панель «Воспроизведение»: ▶ и «Возвращать в начало»


def find_doc(path):
    docs = app.Documents
    for i in range(docs.Count):
        d = qi(docs.Item(i), A7.IKompasDocument)
        if os.path.normcase(d.PathName) == os.path.normcase(path):
            return d
    return None


def close_doc(path):
    """закрыть документ без сохранения; вопрос о сохранении не показывать"""
    d = find_doc(path)
    if d:
        app.HideMessage = C.ksHideMessageNo
        try:
            d.Close(0)
        finally:
            app.HideMessage = C.ksShowMessage


def scenario(n_mates, i_angle, z_kulisa):
    """XML: ход вниз и обратно; время растянуто в SLOW_DEFAULT раз, как в окне движения"""
    ph = [phi_work(T_STROKE * i / N_SEG) for i in range(N_SEG + 1)]
    dt = T_STROKE * SLOW_DEFAULT / N_SEG
    mate = "<Mate " + " ".join(f'N_{i}="{int(i == i_angle)}"' for i in range(n_mates)) + "/>"
    fix = "<Fix " + " ".join(f'N_{i}="{-1 if i == 0 else 0}"' for i in range(len(PARTS))) + "/>"

    def step(number, a0, a1):
        c, s = cos(radians(a0)), sin(radians(a0))
        pos = dict(x=0.0, y=0.0, z=z_kulisa, xx=c, yx=s, zx=z_kulisa, xy=-s, yy=c, zy=z_kulisa)
        start = "<Start " + " ".join(f'{k}="{v:.30f}"' for k, v in pos.items()) + "/>"
        rotate = (f'<Rotate><Axis Part="-1" Axis="{AXIS.replace(" ", "_")}" Number="0" Direct="{1 if a1 > a0 else -1}" Type="1" '
                  f'TypeVel="0" Param="{dt:.6f}" MU="Сек" KM="1.000000" Angle="{abs(a1 - a0):.6f}" Error="0"/></Rotate>')
        return (f'<Step Number="{number}" timeScena="0" Error="0">{mate}{fix}'
                f'<Part Name="{PARTS[KULISA]}" Number="{KULISA}" Error="0">{start}{rotate}</Part></Step>')

    pairs = list(zip(ph, ph[1:]))
    pairs += [(b, a) for a, b in reversed(pairs)]
    steps = "".join(step(i + 1, a, b) for i, (a, b) in enumerate(pairs))
    xml = f'<Path><Settings Cycle="1" Rebuild="0" Frames="{FRAMES}" Pause="0"/>{steps}</Path>'
    open(XML, "w", encoding="utf-8", newline="").write(xml)
    print(f"сценарий: {len(pairs)} шагов, ход {T_STROKE * SLOW_DEFAULT:.2f} с (замедление {SLOW_DEFAULT:g}×) — {XML}")


def build():
    """копия сборки: рукоять вверху (φн), сопряжение угла исключено, ось O построена"""
    close_doc(ASM_ANIM)
    shutil.copy2(ASM, ASM_ANIM)
    doc = app.Documents.Open(ASM_ANIM, True, False)
    doc.Active = True
    top = qi(doc, A7.IKompasDocument3D).TopPart
    comp = [qi(top.Parts.Item(i), A7.IPart7) for i in range(top.Parts.Count)]
    assert [c.Name for c in comp] == PARTS, [c.Name for c in comp]         # номера компонентов в XML
    mates = top.MateConstraints
    n_mates = mates.Count
    i_angle = next(i for i in range(n_mates) if qi(mates.Item(i), A7.IMateConstraint3D).ConstraintType == C3.mc_Angle)
    ang = qi(mates.Item(i_angle), A7.IMateConstraint3D)
    qi(ang, A7.IMateInterval).UseInterval = False                          # с диапазоном значение не двигает механизм
    ang.ParamValue = PH_N
    ang.Update()
    top.RebuildModel(True)

    d5 = A5.ksDocument3D(k5.TransferInterface(doc, C.ksAPI5Auto, 0))
    p = d5.GetPart(C3.pTop_Part)
    ox, oy, oz = comp[0].Placement.GetOrigin()[-3:]
    objs = [qi(o, A7.IModelObject) for o in (comp[0].FindObjectsByPoint(ox + 5.0, oy, oz + 10.0, True) or ())]
    faces = [o for o in objs if o.ModelObjectType == C3.o3d_face]          # цилиндр оси O Ø10 на стойке
    assert len(faces) == 1, len(faces)
    ax = p.NewEntity(C3.o3d_axisConeFace)
    d = ax.GetDefinition()
    d.SetFace(A5.ksEntity(k5.TransferInterface(faces[0], C.ksAPI5Auto, 0)))
    ax.name = AXIS
    assert ax.Create(), "ось не построена"
    ax.hidden = True
    ax.Update()

    qi(mates.Item(i_angle), A7.IFeature7).Excluded = True
    top.RebuildModel(True)
    v = comp[KULISA].Placement.GetVector(0)[-3:]
    ph, y = degrees(atan2(v[1], v[0])), comp[PARTS.index("Ползун")].Placement.GetOrigin()[-2]
    assert abs(ph - PH_N) < 1e-3 and abs(y - yD(ph)) < 1e-3, (ph, y)
    doc.Save()                                                             # ничего не возвращает
    assert not doc.Changed, "копия не сохранена"
    print(f"копия сборки: φ = {ph:.2f}°, ползун y = {y:.3f}, сопряжение угла (№ {i_angle}) исключено — {ASM_ANIM}")
    scenario(n_mates, i_angle, comp[KULISA].Placement.GetOrigin()[-1])


# ---------------------------------------------------------------- окна Анимации
def kompas_pid():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq kStudy.exe", "/NH", "/FO", "CSV"], capture_output=True).stdout
    return int(out.decode("cp866").split('","')[1])


def windows():
    pid, res = kompas_pid(), []

    def cb(h, _):
        if win32process.GetWindowThreadProcessId(h)[1] == pid and win32gui.IsWindowVisible(h) and win32gui.GetClassName(h) == "#32770":
            res.append(h)
    win32gui.EnumWindows(cb, None)
    return res


def main_window():
    return next((w for w in windows() if win32gui.GetMenu(w)), None)         # заголовок меняется, а меню есть только у него


def panel():
    return next((w for w in windows() if win32gui.GetWindowText(w) == "Воспроизведение"), None)


def dialogs():
    m, p = main_window(), panel()
    return [w for w in windows() if w not in (m, p)]


def children(h):
    res = []
    win32gui.EnumChildWindows(h, lambda c, _: res.append(c), None)
    return res


def wait(cond, timeout=15):
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = cond()
        if r:
            return r
        time.sleep(0.1)
    return None


def menu(cmd):
    win32gui.PostMessage(main_window(), win32con.WM_COMMAND, cmd, 0)


def press(dlg, cid):
    win32gui.SendMessage(win32gui.GetDlgItem(dlg, cid), win32con.BM_CLICK, 0, 0)


def has_edit(dlg):
    return any(win32gui.GetClassName(c) == "Edit" for c in children(dlg))


def exit_animation():
    """закрыть панель и окно Анимации, не сохраняя сценарий"""
    if panel():
        win32gui.PostMessage(panel(), win32con.WM_CLOSE, 0, 0)
        wait(lambda: not panel(), 5)
        time.sleep(0.5)
    if main_window():
        menu(CMD_EXIT)
        t0 = time.time()
        while main_window() and time.time() - t0 < 8:
            for d in dialogs():
                if win32gui.GetDlgItem(d, 7):
                    press(d, 7)                                               # «Сохранить текущий сценарий?» — нет
            time.sleep(0.2)
        assert not main_window(), "окно Анимации не закрылось"


def load_scenario():
    menu(CMD_LOAD)
    d = wait(lambda: next(iter(dialogs()), None))
    assert d, "нет окна загрузки"
    if not has_edit(d):
        press(d, 7)                                                           # «Сохранить текущий сценарий?» — нет
        d = wait(lambda: next((x for x in dialogs() if has_edit(x)), None))
    edit = next(c for c in children(d) if win32gui.GetClassName(c) == "Edit" and win32gui.IsWindowVisible(c))
    win32gui.SendMessage(edit, win32con.WM_SETTEXT, 0, XML)
    time.sleep(0.2)
    win32gui.PostMessage(d, win32con.WM_COMMAND, 1, 0)
    assert wait(lambda: d not in dialogs(), 10), "окно загрузки не закрылось"
    time.sleep(1.0)
    msg = [win32gui.GetWindowText(c) for x in dialogs() for c in children(x) if win32gui.GetClassName(c) == "Static"]
    assert not any(msg), msg


def set_cycle():
    """циклическое воспроизведение: атрибут Cycle из XML при загрузке не применяется, только галочка в настройках"""
    menu(CMD_SETTINGS)
    d = wait(lambda: next(iter(dialogs()), None), 8)
    assert d, "нет окна настроек"
    if not win32gui.SendMessage(win32gui.GetDlgItem(d, CHK_CYCLE), win32con.BM_GETCHECK, 0, 0):
        press(d, CHK_CYCLE)
    press(d, 1)
    assert wait(lambda: d not in dialogs(), 5), "окно настроек не закрылось"


def play(start=True):
    assert os.path.exists(ASM_ANIM) and os.path.exists(XML), "сначала: python kompas_animation.py"
    exit_animation()
    close_doc(ASM_ANIM)                                                       # перечитать: рукоять снова в φн, откуда идёт сценарий
    doc = app.Documents.Open(ASM_ANIM, True, False)
    doc.Active = True
    # команда библиотеки не возвращается, пока окно открыто, — отдельным процессом
    subprocess.Popen([sys.executable, os.path.abspath(__file__), "--lib"], cwd=HERE, creationflags=subprocess.CREATE_NO_WINDOW)
    assert wait(main_window, 30), "окно Анимации не открылось"
    load_scenario()
    set_cycle()
    menu(CMD_PLAY)
    p = wait(panel)
    assert p, "панель воспроизведения не открылась"
    time.sleep(0.5)
    c = win32gui.GetDlgItem(p, BTN_BACK)
    if not win32gui.SendMessage(c, win32con.BM_GETCHECK, 0, 0):
        press(p, BTN_BACK)                                                    # при закрытии панели вернуть рукоять в начало
    if start:
        win32gui.PostMessage(p, win32con.WM_COMMAND, win32api.MAKELONG(BTN_PLAY, win32con.BN_CLICKED), win32gui.GetDlgItem(p, BTN_PLAY))
    print("анимация загружена" + (" и запущена" if start else ": ▶ на панели «Воспроизведение»"))


if __name__ == "__main__":
    if "--lib" in sys.argv:
        k5.ksExecuteKompasLibraryCommand(k5.ksAttachKompasLibrary(RTW), LIB_START)
    elif "--play" in sys.argv:
        play()
    elif "--load" in sys.argv:
        play(start=False)
    else:
        build()
