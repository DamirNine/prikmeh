# -*- coding: utf-8 -*-
"""LaTeX для всех выносных формул v17 — по порядку их следования (list_formulas.py → formulas_v17.txt).
Элемент: (начало исходного текста для сверки, LaTeX | [LaTeX, LaTeX…] — разбить на строки | None — удалить абзац)."""

T = r"\text"
FORMULAS = [
    # 3.1–3.3
    ("σ_{раб} = k", r"\sigma_{\text{раб}} = k\cdot\sigma_{\text{т}} = 1,05\cdot 415 = 435,75\ \text{МПа}"),
    ("A_{торц} = π/4", r"A_{\text{торц}} = \frac{\pi}{4}\left({26,55}^{2} - {17,25}^{2}\right) = 319,9\ \text{мм}^{2},\qquad F = 435,75\cdot 319,9 \approx 139\ \text{кН}"),
    ("F_{ук} = n·σ_{раб}", r"F_{\text{ук}} = n\cdot\sigma_{\text{раб}}\cdot A\cdot\ln\frac{D_{k}}{D_{\text{обж}}},\qquad A = \pi\cdot d_{\text{ср}}\cdot s"),
    ("A = π·(28,6", r"A = \pi\cdot(28,6 - 0,22)\cdot 0,22 = 19,61\ \text{мм}^{2},\qquad \ln\frac{32,10}{28,6} = 0,1154"),
    ("F_{ук} = 2,0·435,75", r"F_{\text{ук}} = 2,0\cdot 435,75\cdot 19,61\cdot 0,1154 = 1974\ \text{Н} \approx 2,0\ \text{кН}"),
    # 4.1–4.4
    ("W = 3n", r"W = 3n - 2p_{5} = 3\cdot 3 - 2\cdot 4 = 1,\qquad k = p - n = 4 - 3 = 1\ \ \text{(формула Гохмана)}"),
    ("l_{OD} = e + y", r"\mathbf{l}_{OD} = \mathbf{e} + \mathbf{y}\qquad\text{(векторы — полужирным)}"),
    ("x:   l_{OD}", r"x\colon\quad l_{OD}\cos\varphi = e,\qquad y\colon\quad l_{OD}\sin\varphi = y"),
    ("y = e·tg φ", r"y = e\cdot\operatorname{tg}\varphi,\qquad l_{OD} = \frac{e}{\cos\varphi}"),
    ("ползун D:", r"\text{ползун }D\colon\quad V_{qDx} = \frac{dx_{D}}{dq} = 0,\qquad V_{qDy} = \frac{dy_{D}}{dq} = -\frac{e}{\cos^{2}\varphi}"),
    ("a_{qDx} = 0", r"a_{qDx} = 0,\qquad a_{qDy} = \frac{d^{2}y_{D}}{dq^{2}} = \frac{2e\sin\varphi}{\cos^{3}\varphi}"),
    ("камень относительно", r"\text{камень относительно кулисы:}\quad V_{q,r} = \frac{e\sin\varphi}{\cos^{2}\varphi},\qquad a_{q,r} = \frac{e\,(1 + \sin^{2}\varphi)}{\cos^{3}\varphi}"),
    ("точка C кулисы", r"\text{точка }C\text{ кулисы под камнем:}\quad V_{qC} = l_{OD} = \frac{e}{\cos\varphi}"),
    ("конец рукояти K", r"\text{конец рукояти }K\colon\quad V_{qKx} = L\sin\varphi,\qquad V_{qKy} = -L\cos\varphi"),
    ("a_{qKx} = −L", r"a_{qKx} = -L\cos\varphi,\qquad a_{qKy} = -L\sin\varphi,\qquad |V_{qK}| = |a_{qK}| = L"),
    ("S = e·(tg φ_{н}", r"S = e\cdot\left(\operatorname{tg}\varphi_{\text{н}} - \operatorname{tg}\varphi_{\text{к}}\right)\quad\Rightarrow\quad e = \frac{S}{\operatorname{tg}\varphi_{\text{н}} - \operatorname{tg}\varphi_{\text{к}}}"),
    # 5
    ("P = 120 Н", r"P = 120\ \text{Н (вертикально)}"),
    ("P·L·cos φ·dφ", r"P\cdot L\cos\varphi\,d\varphi = F\,dy = \frac{F\cdot e}{\cos^{2}\varphi}\,d\varphi\quad\Rightarrow\quad F = \frac{P\cdot L\cos^{3}\varphi}{e}"),
    ("L = F_{ук}·e / (P", r"L = \frac{F_{\text{ук}}\cdot e}{P\cos^{3}\varphi_{\text{max}}}"),
    ("s_{руки}", r"s_{\text{руки}} \ge \frac{F_{\text{ук}}\cdot S_{\text{об}}}{P} = \frac{1974\cdot 6}{120} = 99\ \text{мм}"),
    # 6.1–6.2 (были линейными формулами Word)
    ("S = e·(tan", r"S = e\cdot\left(\operatorname{tg}\varphi_{\text{н}} - \operatorname{tg}\varphi_{\text{к}}\right)"),
    ("ψ = φн", r"\psi = \varphi_{\text{н}} - \varphi_{\text{к}},\qquad \varphi_{\text{н}} = \varphi_{\text{к}} + \psi"),
    ("e(φк, ψ)", r"e(\varphi_{\text{к}},\psi) = \frac{S}{\operatorname{tg}(\varphi_{\text{к}} + \psi) - \operatorname{tg}\varphi_{\text{к}}}"),
    ("A = 1/2", r"A = \frac{1}{2}\cdot e\cdot S"),
    ("A(φк, ψ)", r"A(\varphi_{\text{к}},\psi) = \frac{S^{2}}{2\left[\operatorname{tg}(\varphi_{\text{к}} + \psi) - \operatorname{tg}\varphi_{\text{к}}\right]}"),
    ("L = Fук", r"L = \frac{F_{\text{ук}}\cdot e}{P\cos^{3}\varphi_{\text{об}}},\qquad \varphi_{\text{об}} = \operatorname{arctg}\left(\operatorname{tg}\varphi_{\text{к}} + \frac{S_{\text{об}}}{e}\right)"),
    # 6.6, 7.1
    ("δ_{A} =", r"\delta_{A} = \frac{A_{\text{min}}(\psi)}{A^{*}} - 1,\qquad A^{*} = 80,0\ \text{мм}^{2}\ \ (e = 10\ \text{мм})"),
    ("δ_{ψ} =", r"\delta_{\psi} = \frac{\psi}{\psi^{*}} - 1,\qquad \psi^{*} = 29,33°\ \ \text{(наименьший }\psi\text{ при }L \le 500\ \text{мм)}"),
    ("φ_{н} = 59,47°", [r"\varphi_{\text{н}} = 59,47°,\qquad \varphi_{\text{к}} = 22,72°,\qquad \psi = 36,75°",
                        r"\varphi_{\text{об}} = \operatorname{arctg}\left(\operatorname{tg}22,72° + \frac{6}{12,53}\right) = 41,91°"]),
    ("L_{0} = 1974", r"L_{0} = \frac{1974\cdot 12,53}{120\cdot\cos^{3}41,91°} \approx 500\ \text{мм}"),
    # 9
    ("ψ = ½", r"\psi = \frac{1}{2}\cdot\omega_{\text{max}}\cdot t_{\text{р}} + \omega_{\text{max}}\cdot t_{\text{у}} + \frac{1}{2}\cdot\omega_{\text{max}}\cdot t_{\text{т}}"),
    ("ε_{р} = ω_{max}", r"\varepsilon_{\text{р}} = \frac{\omega_{\text{max}}}{t_{\text{р}}},\qquad \varepsilon_{\text{т}} = -\frac{\omega_{\text{max}}}{t_{\text{т}}}"),
    ("ε_{т} = σ_{т}/E", r"\varepsilon_{\text{т}} = \frac{\sigma_{\text{т}}}{E} = \frac{415}{2,1\cdot 10^{5}} = 0,00198"),
    ("Δr_{у}", r"\Delta r_{\text{у}} = \frac{\varepsilon_{\text{т}}\cdot D_{k}}{2} = \frac{0,00198\cdot 32,10}{2} = 0,032\ \text{мм}"),
    ("tg α = 1,75", r"\operatorname{tg}\alpha = \frac{1,75}{6} = 0,292\ \ (\alpha = 16,3°),\qquad \delta_{\text{у}} = \frac{\Delta r_{\text{у}}}{\operatorname{tg}\alpha} = \frac{0,032}{0,292} = 0,109\ \text{мм}"),
    ("φ_{об} = arctg", [r"\varphi_{\text{об}} = \operatorname{arctg}\left(\operatorname{tg}22,72° + \frac{6}{12,53}\right) = 41,91°",
                        r"\varphi_{\text{у}} = \operatorname{arctg}\left(\operatorname{tg}22,72° + \frac{5,891}{12,53}\right) = 41,63°"]),
    ("ψ_{хх} =", r"\psi_{\text{хх}} = 59,47° - 41,91° = 17,56° = 0,3065\ \text{рад}"),
    ("ψ_{у} = 41,91°", [r"\psi_{\text{у}} = 41,91° - 41,63° = 0,28° = 0,00483\ \text{рад}",
                        r"\psi_{\text{пл}} = 41,63° - 22,72° = 18,91° = 0,3301\ \text{рад}"]),
    ("ω_{max} = v_{max}", r"\omega_{\text{max}} = \frac{v_{\text{max}}}{L} = \frac{0,7}{0,5} = 1,40\ \text{рад/с}"),
    ("t_{р} = 2ψ", r"t_{\text{р}} = \frac{2\psi_{\text{хх}}}{\omega_{\text{max}}} = \frac{2\cdot 0,3065}{1,40} = 0,438\ \text{с}"),
    ("t_{у} = ψ", r"t_{\text{у}} = \frac{\psi_{\text{у}}}{\omega_{\text{max}}} = \frac{0,00483}{1,40} = 0,0034\ \text{с}"),
    ("t_{т} = 2ψ", r"t_{\text{т}} = \frac{2\psi_{\text{пл}}}{\omega_{\text{max}}} = \frac{2\cdot 0,3301}{1,40} = 0,472\ \text{с}"),
    ("ε_{р} = 1,40", r"\varepsilon_{\text{р}} = \frac{1,40}{0,438} = 3,20\ \text{рад/с}^{2},\qquad \varepsilon_{\text{т}} = -\frac{1,40}{0,472} = -2,97\ \text{рад/с}^{2}"),
    ("t_{рх} =", r"t_{\text{рх}} = 0,438 + 0,003 + 0,472 = 0,913\ \text{с}"),
    ("проверка: ψ", r"\text{проверка:}\quad \psi = \frac{1}{2}\cdot 1,40\cdot 0,438 + 1,40\cdot 0,0034 + \frac{1}{2}\cdot 1,40\cdot 0,472 ="),
    ("= 0,641", r"= 0,641\ \text{рад} = 36,75°"),
    ("T_{ц} =", r"T_{\text{ц}} = \frac{60}{Q} = \frac{60}{6} = 10\ \text{с}"),
    # 11.2
    ("A_{пр} =", r"A_{\text{пр}} = n\cdot A\cdot\ln\frac{D_{k}}{D_{\text{обж}}} = 2,0\cdot 19,61\cdot 0,1154 = 4,529\ \text{мм}^{2}"),
    ("F_{т} = σ_{т}", r"F_{\text{т}} = \sigma_{\text{т}}\cdot A_{\text{пр}} = 415\cdot 4,529 = 1880\ \text{Н}"),
    ("F_{ук} = 1,05", r"F_{\text{ук}} = 1,05\cdot\sigma_{\text{т}}\cdot A_{\text{пр}} = 435,75\cdot 4,529 = 1974\ \text{Н}"),
    ("δ(φ) = e", r"\delta(\varphi) = e\cdot\left(\operatorname{tg}\varphi_{\text{об}} - \operatorname{tg}\varphi\right),\qquad \delta_{\text{у}} = 0,109\ \text{мм (п. 9.2)}"),
    ("F(φ) = 0,", r"F(\varphi) = \begin{cases} 0, & \varphi > \varphi_{\text{об}} = 41,91°;\\ C\cdot\delta(\varphi), & \varphi_{\text{у}} \le \varphi \le \varphi_{\text{об}};\\"
                 r" F_{\text{т}} + k\cdot\left(\delta(\varphi) - \delta_{\text{у}}\right), & \varphi_{\text{к}} \le \varphi < \varphi_{\text{у}} = 41,63°. \end{cases}"),
    ("F(φ) = C·δ", None),
    ("F(φ) = F_{т}", None),
    ("C = F_{т}", r"C = \frac{F_{\text{т}}}{\delta_{\text{у}}} = \frac{1880}{0,1087} \approx 17\,300\ \text{Н/мм}"),
    ("k = (F_{ук}", r"k = \frac{F_{\text{ук}} - F_{\text{т}}}{S_{\text{об}} - \delta_{\text{у}}} = \frac{94}{5,891} \approx 16,0\ \text{Н/мм}"),
    # 11.3–11.7
    ("M_{M}(F)", r"M_{M}(F) = F_{y}\cdot x + F_{x}\cdot y"),
    ("O: (x_{M}", r"O\colon\ (x_{M};\ y_{M}),\qquad D\colon\ (X_{D};\ Y_{D}) = (x_{M} + e;\ \ y_{M} - e\cdot\operatorname{tg}\varphi)"),
    ("K: (X_{K}", r"K\colon\ (X_{K};\ Y_{K}) = (x_{M} + L\cos\varphi;\ \ y_{M} - L\sin\varphi)"),
    ("ΣF_{x}:   R_{10}^{x} + R_{12}^{N}·cos(φ + 90°) = 0", r"\Sigma F_{x}\colon\quad R_{10}^{x} + R_{12}^{N}\cos(\varphi + 90°) = 0"),
    ("ΣF_{y}:   R_{10}^{y} + R_{12}^{N}·sin(φ + 90°) − P = 0", r"\Sigma F_{y}\colon\quad R_{10}^{y} + R_{12}^{N}\sin(\varphi + 90°) - P = 0"),
    ("ΣM_{M}:   R_{10}^{x}·y_{M}", r"\Sigma M_{M}\colon\quad R_{10}^{x}\cdot y_{M} + R_{10}^{y}\cdot x_{M} + R_{12}^{N}\cdot a(\varphi) + M_{12} - P\cdot X_{K} = 0"),
    ("ΣF_{x}:   R_{12}^{N}", r"\Sigma F_{x}\colon\quad R_{12}^{N}\cos(\varphi - 90°) + R_{23}^{x} = 0"),
    ("ΣF_{y}:   R_{12}^{N}", r"\Sigma F_{y}\colon\quad R_{12}^{N}\sin(\varphi - 90°) + R_{23}^{y} = 0"),
    ("ΣM_{M}:   −R_{12}^{N}", r"\Sigma M_{M}\colon\quad -R_{12}^{N}\cdot a(\varphi) - M_{12} + R_{23}^{x}\cdot Y_{D} + R_{23}^{y}\cdot X_{D} = 0"),
    ("ΣF_{x}:   −R_{23}^{x}", r"\Sigma F_{x}\colon\quad -R_{23}^{x} + R_{30}^{N} = 0"),
    ("ΣF_{y}:   −R_{23}^{y} + F_{ук}", r"\Sigma F_{y}\colon\quad -R_{23}^{y} + F_{\text{ук}} = 0"),
    ("ΣM_{M}:   −R_{23}^{x}·Y_{D}", r"\Sigma M_{M}\colon\quad -R_{23}^{x}\cdot Y_{D} - R_{23}^{y}\cdot X_{D} + R_{30}^{N}\cdot Y_{D} + M_{30} + F_{\text{ук}}\cdot X_{D} = 0"),
    ("R_{12}^{N} = F_{ук}", r"R_{12}^{N} = \frac{F_{\text{ук}}}{\cos\varphi},\qquad R_{23}^{x} = -F_{\text{ук}}\cdot\operatorname{tg}\varphi,\qquad R_{23}^{y} = F_{\text{ук}}"),
    ("R_{30}^{N} = −F_{ук}", r"R_{30}^{N} = -F_{\text{ук}}\cdot\operatorname{tg}\varphi,\qquad M_{12} = M_{30} = 0"),
    ("R_{10}^{x} = F_{ук}", r"R_{10}^{x} = F_{\text{ук}}\cdot\operatorname{tg}\varphi,\qquad R_{10}^{y} = P - F_{\text{ук}}"),
    ("P(φ) = F_{ук}", r"P(\varphi) = \frac{F_{\text{ук}}(\varphi)\cdot e}{L\cos^{3}\varphi}"),
    ("L_{треб}(φ)", r"L_{\text{треб}}(\varphi) = \frac{F_{\text{ук}}(\varphi)\cdot e}{P_{\text{доп}}\cos^{3}\varphi}"),
    # 12
    ("прямоугольник", r"\text{прямоугольник }b\times h\colon\quad A = b\cdot h,\qquad W = \frac{b\cdot h^{2}}{6}"),
    ("круг диаметром", r"\text{круг диаметром }d\colon\quad A = \frac{\pi d^{2}}{4},\qquad W = \frac{\pi d^{3}}{32},\qquad I = \frac{\pi d^{4}}{64}"),
    ("h = [|N|", r"h = \frac{|N| + \sqrt{N^{2} + 24\cdot[\sigma]\cdot b\cdot|M|}}{2\cdot[\sigma]\cdot b}"),
    ("N = −P·sin φ   (сжатие)", r"N = -P\sin\varphi\qquad\text{(сжатие)}"),
    ("участок O–D", r"\text{участок O–D }(0 \le z \le l_{OD})\colon\quad Q = P\cos\varphi - \frac{F_{\text{ук}}}{\cos\varphi},\qquad M(z) = Q\cdot z"),
    ("участок D–K", r"\text{участок D–K }(l_{OD} \le z \le L)\colon\quad Q = P\cos\varphi,\qquad M(z) = P\cos\varphi\cdot(z - L)"),
    ("σ = F_{ук}/A", r"\sigma = \frac{F_{\text{ук}}}{A} \le [\sigma];\qquad \lambda = \frac{\mu\cdot l}{i},\qquad i = \sqrt{\frac{I}{A}} = \frac{d}{4}"),
    ("λ ≥ λ_{пред}", [r"\lambda \ge \lambda_{\text{пред}} = 100\colon\quad F_{\text{кр}} = \frac{\pi^{2}\cdot E\cdot I}{(\mu\cdot l)^{2}};",
                      r"\lambda < 100\colon\quad \sigma_{\text{кр}} = a - b\cdot\lambda \le \sigma_{\text{т}},\qquad F_{\text{кр}} = \sigma_{\text{кр}}\cdot A"]),
    ("n_{у} = F_{кр}", r"n_{\text{у}} = \frac{F_{\text{кр}}}{F_{\text{ук}}} \ge [n_{\text{у}}] = 3"),
    # 13.2
    ("ε = ε_{р} = 3,20", r"\varepsilon = \varepsilon_{\text{р}} = 3,20\ \text{рад/с}^{2},\qquad \omega = \sqrt{2\cdot\varepsilon_{\text{р}}\cdot(\varphi_{\text{н}} - \varphi)}"),
    ("ε = 0,", r"\varepsilon = 0,\qquad \omega = \omega_{\text{max}} = 1,40\ \text{рад/с}"),
    ("ε = ε_{т} = −2,97", r"\varepsilon = \varepsilon_{\text{т}} = -2,97\ \text{рад/с}^{2},\qquad \omega = \sqrt{2\cdot|\varepsilon_{\text{т}}|\cdot(\varphi - \varphi_{\text{к}})}"),
    # 13.3
    ("X_{S} = x_{M}", r"X_{S} = x_{M} + z_{S}\cos\varphi,\qquad Y_{S} = y_{M} - z_{S}\sin\varphi"),
    ("Ф_{1x} = Ф_{1}^{n}", r"\Phi_{1x} = \Phi_{1}^{n}\cos\varphi - \Phi_{1}^{\tau}\sin\varphi,\qquad \Phi_{1y} = \Phi_{1}^{n}\sin\varphi + \Phi_{1}^{\tau}\cos\varphi"),
    ("M_{Ф1} = J_{S}", r"M_{\Phi 1} = J_{S}\cdot\varepsilon\qquad\text{(против часовой стрелки — положительный)}"),
    # 13.4
    ("ΣF_{x}:   R_{10x}", r"\Sigma F_{x}\colon\quad R_{10}^{x} + R_{12}^{N}\cos(\varphi + 90°) + \Phi_{1x} = 0"),
    ("ΣF_{y}:   R_{10y}", r"\Sigma F_{y}\colon\quad R_{10}^{y} + R_{12}^{N}\sin(\varphi + 90°) - P - G_{1} + \Phi_{1y} = 0"),
    ("ΣM_{M}:   R_{10x}", r"\Sigma M_{M}\colon\quad R_{10}^{x}\cdot y_{M} + R_{10}^{y}\cdot x_{M} + R_{12}^{N}\cdot a(\varphi) + M_{12} - P\cdot X_{K} -"),
    ("− G_{1}·X_{S}", r"- G_{1}\cdot X_{S} + \Phi_{1y}\cdot X_{S} + \Phi_{1x}\cdot Y_{S} + M_{\Phi 1} = 0"),
    ("F_{пр} = F_{ук}", r"F_{\text{пр}} = F_{\text{ук}} - G_{3} + \Phi_{3}"),
    ("ΣF_{x}:   −R_{23x}", r"\Sigma F_{x}\colon\quad -R_{23}^{x} + R_{30}^{N} = 0"),
    ("ΣF_{y}:   −R_{23y}", r"\Sigma F_{y}\colon\quad -R_{23}^{y} + F_{\text{пр}} = 0"),
    ("ΣM_{M}:   −R_{23x}", r"\Sigma M_{M}\colon\quad -R_{23}^{x}\cdot Y_{D} - R_{23}^{y}\cdot X_{D} + R_{30}^{N}\cdot Y_{D} + M_{30} + F_{\text{пр}}\cdot X_{D} = 0"),
    # 13.5
    ("R_{12}^{N} = F_{пр}", [r"R_{12}^{N} = \frac{F_{\text{пр}}}{\cos\varphi},\qquad R_{23}^{x} = R_{30}^{N} = -F_{\text{пр}}\cdot\operatorname{tg}\varphi",
                             r"R_{23}^{y} = F_{\text{пр}},\qquad M_{12} = M_{30} = 0"]),
    ("R_{10x} = F_{пр}", r"R_{10}^{x} = F_{\text{пр}}\cdot\operatorname{tg}\varphi - \Phi_{1x},\qquad R_{10}^{y} = P + G_{1} - F_{\text{пр}} - \Phi_{1y}"),
    ("P(φ) = [F_{пр}", r"P(\varphi) = \frac{\dfrac{F_{\text{пр}}\cdot e}{\cos^{2}\varphi} - G_{1}\cdot z_{S}\cos\varphi + J_{O}\cdot\varepsilon}{L\cos\varphi}"),
    ("A_{P} = A_{F}", r"A_{P} = A_{F} - \Delta\Pi,\qquad \Delta\Pi = G_{1}\cdot z_{S}\cdot(\sin\varphi_{\text{н}} - \sin\varphi_{\text{к}}) + G_{3}\cdot S"),
    # 13.7
    ("по нормали к оси", r"\text{по нормали к оси звена:}\quad q_{n}(z) = q\cdot(\varepsilon\cdot z - g\cos\varphi)"),
    ("вдоль оси звена", r"\text{вдоль оси звена:}\quad q_{u}(z) = q\cdot(\omega^{2}\cdot z - g\sin\varphi)"),
    ("N = −P·sin φ + ∫", [r"N = -P\sin\varphi + \int_{l_{OD}}^{L} q_{u}\,dz",
                          r"M_{D} = -P\cos\varphi\cdot(L - l_{OD}) + \int_{l_{OD}}^{L} q_{n}\cdot(z - l_{OD})\,dz"]),
]

# матричная запись системы уточнённого расчёта (вместо таблицы 20); B₃ — отдельной строкой
MATRIX = (r"\begin{pmatrix} 1 & 0 & \cos(\varphi+90°) & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 1 & \sin(\varphi+90°) & 0 & 0 & 0 & 0 & 0 & -1 \\"
          r" y_{M} & x_{M} & a(\varphi) & 1 & 0 & 0 & 0 & 0 & -X_{K} \\ 0 & 0 & \cos(\varphi-90°) & 0 & 1 & 0 & 0 & 0 & 0 \\"
          r" 0 & 0 & \sin(\varphi-90°) & 0 & 0 & 1 & 0 & 0 & 0 \\ 0 & 0 & -a(\varphi) & -1 & Y_{D} & X_{D} & 0 & 0 & 0 \\"
          r" 0 & 0 & 0 & 0 & -1 & 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & -1 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & -Y_{D} & -X_{D} & Y_{D} & 1 & 0 \end{pmatrix}"
          r"\cdot\begin{pmatrix} R_{10}^{x} \\ R_{10}^{y} \\ R_{12}^{N} \\ M_{12} \\ R_{23}^{x} \\ R_{23}^{y} \\ R_{30}^{N} \\ M_{30} \\ P \end{pmatrix}"
          r" = \begin{pmatrix} -\Phi_{1x} \\ G_{1} - \Phi_{1y} \\ B_{3} \\ 0 \\ 0 \\ 0 \\ 0 \\ -F_{\text{пр}} \\ -F_{\text{пр}}\cdot X_{D} \end{pmatrix}")
MATRIX_B3 = r"B_{3} = G_{1}\cdot X_{S} - \Phi_{1y}\cdot X_{S} - \Phi_{1x}\cdot Y_{S} - M_{\Phi 1}"
