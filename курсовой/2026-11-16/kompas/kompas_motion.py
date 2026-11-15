# -*- coding: utf-8 -*-
"""Окно с кнопкой: движение механизма в КОМПАС-3D туда-сюда в открытой сборке УКП.00.000.
Угол кулисы меняется по закону п. 9 расчёта: рабочий ход — разгон, упругий участок, торможение; обратный ход — то же в
обратную сторону. Угол задаётся сопряжением «Под углом», поэтому на время движения его диапазон выключается (при включённом
диапазоне значение угла механизм не двигает), а при остановке включается снова. Камень и ползун идут за кулисой сами.
Сборку скрипт не сохраняет. Запуск: «Движение механизма.bat» или python kompas_motion.py; замер скорости без окна:
python kompas_motion.py --test"""
import os, sys, time
from math import degrees
import tkinter as tk
from tkinter import messagebox

from kompas_build import A7, C3, HERE, PH_K, PH_N, RJ, app, qi, yD

ASM = os.path.join(HERE, "УКП.00.000 Укупориватель.a3d")
W, EP_R, EP_T = RJ["w"], RJ["eps_r"], abs(RJ["eps_t"])          # ω макс, ε разгона, ε торможения (рад/с, рад/с²)
T_R, T_U, T_T = RJ["t_r"], RJ["t_u"], RJ["t_t"]                  # времена фаз рабочего хода, с
PH_OB, PH_Y = RJ["phi_ob"], RJ["phi_y"]
T_STROKE = T_R + T_U + T_T                                       # рабочий ход; обратный — столько же


def phi_work(t):
    """угол кулисы на рабочем ходе, градусы; t — время от начала хода"""
    if t <= T_R:                                                 # разгон — холостой ход
        return PH_N - degrees(EP_R * t ** 2 / 2)
    if t <= T_R + T_U:                                           # упругая деформация — постоянная скорость
        return PH_OB - degrees(W * (t - T_R))
    tau = min(t - T_R - T_U, T_T)                                # пластическая деформация — торможение
    return PH_Y - degrees(W * tau - EP_T * tau ** 2 / 2)


def phi_cycle(t):
    """угол в цикле «вниз — вверх»: обратный ход — рабочий в обратном времени"""
    t %= 2 * T_STROKE
    return phi_work(t) if t <= T_STROKE else phi_work(2 * T_STROKE - t)


class Mechanism:
    """сборка в КОМПАС и её сопряжение «Под углом»"""

    def __init__(self):
        docs = app.Documents
        doc = None
        for i in range(docs.Count):
            d = qi(docs.Item(i), A7.IKompasDocument)
            if os.path.normcase(d.PathName) == os.path.normcase(ASM):
                doc = d
        doc = doc or docs.Open(ASM, True, False)                 # не открыта — открыть
        doc.Active = True
        self.top = qi(doc, A7.IKompasDocument3D).TopPart
        mates = self.top.MateConstraints
        all_mates = [qi(mates.Item(i), A7.IMateConstraint3D) for i in range(mates.Count)]
        self.ang = next(m for m in all_mates if m.ConstraintType == C3.mc_Angle)
        self.itv = qi(self.ang, A7.IMateInterval)

    def set_angle(self, ph):
        self.itv.UseInterval = False                             # с диапазоном значение угла не двигает механизм
        self.ang.ParamValue = ph
        self.ang.Update()
        self.top.RebuildModel(True)

    def angle(self):
        return self.ang.ParamValue

    def release(self):
        """вернуть диапазон угла, чтобы рукоять снова двигалась мышью и останавливалась на границах"""
        self.itv.UseInterval = True
        self.itv.SetValueRange(PH_K, PH_N)
        self.ang.Update()
        self.top.RebuildModel(True)


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Укупориватель: движение")
        self.resizable(False, False)
        self.attributes("-topmost", True)                        # окно поверх КОМПАСа
        self.mech = Mechanism()
        self.running = False
        self.slow = tk.DoubleVar(value=SLOW_DEFAULT)
        self.btn = tk.Button(self, text="▶  Старт", font=("Segoe UI", 16), width=14, command=self.toggle)
        self.btn.pack(padx=16, pady=(14, 8))
        tk.Scale(self, label="Замедление, раз", variable=self.slow, from_=1, to=10, resolution=0.5, orient="horizontal",
                 length=220).pack(padx=16)
        self.info = tk.Label(self, text=f"φ = {self.mech.angle():.2f}°", font=("Segoe UI", 11))
        self.info.pack(pady=(6, 12))
        self.protocol("WM_DELETE_WINDOW", self.close)

    def toggle(self):
        if self.running:
            self.stop()
        else:
            ph = self.mech.angle()                               # начать с текущего положения, без рывка
            self.t = min((k * T_STROKE / 200 for k in range(201)), key=lambda t: abs(phi_work(t) - ph))
            self.last = time.perf_counter()
            self.running = True
            self.btn.config(text="■  Стоп")
            self.tick()

    def tick(self):
        if not self.running:
            return
        now = time.perf_counter()
        self.t += (now - self.last) / self.slow.get()            # модельное время, не зависит от скорости перестроения
        self.last = now
        ph = phi_cycle(self.t)
        try:
            self.mech.set_angle(ph)
        except Exception as ex:                                  # например, в КОМПАСе открыта команда или диалог
            self.stop()
            messagebox.showerror("КОМПАС не ответил", f"Движение остановлено.\n{ex}")
            return
        self.info.config(text=f"φ = {ph:.2f}°   ползун y = {yD(ph):.2f} мм")
        self.after(1, self.tick)

    def stop(self):
        self.running = False
        self.btn.config(text="▶  Старт")
        try:
            self.mech.release()
        except Exception:
            pass

    def close(self):
        if self.running:
            self.stop()
        self.destroy()


SLOW_DEFAULT = 3.0

if __name__ == "__main__":
    if "--test" in sys.argv:                                     # замер: сколько длится один кадр
        m = Mechanism()
        ph0 = m.angle()
        t0 = time.perf_counter()
        N = 30
        for k in range(N):
            m.set_angle(phi_cycle(2 * T_STROKE * k / N))
        dt = (time.perf_counter() - t0) / N
        m.set_angle(ph0)
        m.release()
        print(f"кадр {dt * 1000:.0f} мс; кадров на ход при реальной скорости: {T_STROKE / dt:.1f}; угол возвращён {m.angle():.2f}°")
    else:
        try:
            Window().mainloop()
        except Exception as ex:
            messagebox.showerror("Не удалось запустить", str(ex))
