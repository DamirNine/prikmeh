# -*- coding: utf-8 -*-
"""
Перебор параметров тангенсного механизма ручного укупоривателя.

Критерий: минимальная площадь треугольника O–B_н–B_к
(O — ось кулисы, B_н и B_к — крайние положения точки ползуна на его оси).
Высота треугольника — ход ползуна S (зазор + обжим), основание — e:
    A = ½·e·S_f,   S_f = e·(tg φ_н − tg φ_к).

Варьируются независимо:
    φ_к — угол кулисы в конце хода (на обжиме), град;
    ψ   — угловой ход кулисы, град (φ_н = φ_к + ψ);
    e   — расстояние от оси кулисы до оси ползуна, мм.

Ограничения:
    S_f ≥ S                                ход не меньше требуемого;
    L = F·e / (P·cos³φ_max) ≤ L_max        длина рукояти; P вертикально, рычаг — прямое
                                           продолжение кулисы, φ_max — наибольший |φ| на обжиме;
    |φ| ≤ θ_max на всём ходе               угол давления на ползун;
    e ≥ e_min                              конструктивный минимум (ось кулисы, камень, ползун).

При равной площади (с точностью 0,1 мм²) выбирается меньший ψ, затем меньшая L.
Помимо глобального оптимума строится граница «наименьшая площадь при заданном ψ».
"""
import time
import numpy as np

F = 1974.0      # Н, усилие укупоривания
S = 16.0        # мм, ход: зазор 10 + обжим 6
S_OB = 6.0      # мм, участок обжима — последние мм хода


def search(P, L_max, theta_max=60.0, e_min=10.0,
           phi_k_rng=(-60.0, 60.0 + 1e-9, 0.1), psi_rng=(1.0, 120.0 + 1e-9, 0.1), e_rng=(3.0, 60.0 + 1e-9, 0.1)):
    phi_k = np.round(np.arange(*phi_k_rng), 3)
    psi = np.round(np.arange(*psi_rng), 3)
    e = np.round(np.arange(*e_rng), 3)
    E, PSI = np.meshgrid(e, psi, indexing="xy")               # форма (len(psi), len(e))
    n_total = n_ok = 0
    # граница: для каждого ψ — наименьшая площадь и параметры
    fr_A = np.full(psi.size, np.inf)
    fr = {k: np.full(psi.size, np.nan) for k in ("e", "phi_k", "L", "phi_ob", "Sf")}
    for pk in phi_k:
        n_total += E.size
        pn = pk + PSI
        tk = np.tan(np.radians(pk))
        Sf = E * (np.tan(np.radians(pn)) - tk)
        phi_ob = np.degrees(np.arctan(tk + S_OB / E))           # угол в начале обжима
        worst = np.maximum(abs(pk), np.abs(phi_ob))
        L = F * E / (P * np.cos(np.radians(worst)) ** 3)
        ok = (np.abs(pn) <= theta_max) & (abs(pk) <= theta_max) & (E >= e_min) & (Sf >= S) & (L <= L_max)
        cnt = int(ok.sum())
        if not cnt:
            continue
        n_ok += cnt
        A = np.where(ok, 0.5 * E * Sf, np.inf)
        key = np.round(A, 1) + 1e-6 * L                          # по каждому ψ: мин. площадь, затем L
        j = np.argmin(key, axis=1)
        rows = np.arange(psi.size)
        a = A[rows, j]
        better = a < fr_A - 1e-9
        fr_A[better] = a[better]
        fr["e"][better] = E[rows, j][better]
        fr["phi_k"][better] = pk
        fr["L"][better] = L[rows, j][better]
        fr["phi_ob"][better] = phi_ob[rows, j][better]
        fr["Sf"][better] = Sf[rows, j][better]
    # глобальный оптимум: мин. площадь (0,1 мм²), затем мин. ψ
    finite = np.isfinite(fr_A)
    if not finite.any():
        return None, None, n_total, n_ok
    Amin = np.round(fr_A[finite], 1).min()
    idx = np.where(finite & (np.round(fr_A, 1) <= Amin))[0][0]   # первый ψ (наименьший) с минимальной площадью
    best = dict(A=fr_A[idx], psi=psi[idx], **{k: v[idx] for k, v in fr.items()})
    best["phi_n"] = best["phi_k"] + best["psi"]
    frontier = dict(psi=psi, A=fr_A, **fr)
    return best, frontier, n_total, n_ok


def fmt(b):
    return (f"A = {b['A']:.1f} мм², e = {b['e']:.1f} мм, φк = {b['phi_k']:.1f}°, ψ = {b['psi']:.1f}°, "
            f"φн = {b['phi_n']:.1f}°, S = {b['Sf']:.2f} мм, φоб = {b['phi_ob']:.1f}°, L = {b['L']:.0f} мм")


def frontier_rows(fr, psi_marks):
    """Наименьшая площадь при ψ ≤ ψ_max для заданных ψ_max."""
    out = []
    for pm in psi_marks:
        m = fr["psi"] <= pm + 1e-9
        A = np.where(m & np.isfinite(fr["A"]), np.round(fr["A"], 1), np.inf)
        j = int(np.argmin(A))
        if not np.isfinite(A[j]):
            out.append((pm, None))
            continue
        out.append((pm, dict(A=fr["A"][j], psi=fr["psi"][j], phi_n=fr["phi_k"][j] + fr["psi"][j],
                             **{k: fr[k][j] for k in ("e", "phi_k", "L", "phi_ob", "Sf")})))
    return out


if __name__ == "__main__":
    t0 = time.time()
    P, L_MAX = 120.0, 500.0
    best, fr, n, k = search(P, L_MAX)
    print(f"P = {P:.0f} Н (вертикально), L ≤ {L_MAX:.0f} мм, |φ| ≤ 60°, e ≥ 10 мм")
    print(f"перебрано {n:,} вариантов, допустимых {k:,}")
    print("оптимум:", fmt(best))
    print("наименьшая площадь при ограничении углового хода ψ ≤ ψ_max:")
    for pm, b in frontier_rows(fr, (25, 30, 35, 40, 45, 50, 60)):
        print(f"  ψ ≤ {pm:>4}°: " + (fmt(b) if b else "допустимых вариантов нет"))
    print(f"время {time.time() - t0:.0f} с")
