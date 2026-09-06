import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

l1  = 0.5   # кривошип
l2  = 1.5   # шатун
exs = 0.2   # внеосность

phi = np.linspace(0, 2*np.pi, 300)

# Точка A — ось вращения (неподвижна)
Ay, Az = 0.0, 0.0

# Точка B — конец кривошипа (вращается в плоскости YZ вокруг оси X)
By = l1 * np.cos(phi)
Bz = l1 * np.sin(phi)

# Точка C — ползун (движется вдоль Z при фиксированном Y=exs)
Cy = exs
Cz = Bz - np.sqrt(l2**2 - (By - exs)**2)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
fig.suptitle('Внеосный кривошипно-ползунный механизм\n'
             f'l1={l1}, l2={l2}, exs={exs}', fontsize=12)

# --- Левый: анимация механизма ---
ax1.set_xlim(-0.8, 0.8)
ax1.set_ylim(-2.4, 0.8)
ax1.set_aspect('equal')
ax1.set_xlabel('Y (м)')
ax1.set_ylabel('Z (м)')
ax1.set_title('Вид YZ — кривошип крутится вокруг X')
ax1.axvline(x=exs, color='gray', linestyle='--', alpha=0.5, label=f'линия ползуна y={exs}')
ax1.plot(Ay, Az, 'k^', markersize=12, label='опора A')
ax1.legend(loc='upper right', fontsize=8)
ax1.grid(True, alpha=0.3)

crank_ln, = ax1.plot([], [], 'b-',  lw=3,  label='кривошип')
rod_ln,   = ax1.plot([], [], 'g-',  lw=2,  label='шатун')
slider,   = ax1.plot([], [], 'rs',  ms=14, label='ползун')
joint_B,  = ax1.plot([], [], 'bo',  ms=8)

# --- Правый: закон движения ползуна ---
ax2.plot(np.degrees(phi), Cz, 'r-', lw=2)
ax2.set_xlabel('Угол кривошипа φ, °')
ax2.set_ylabel('Координата ползуна z, м')
ax2.set_title('Закон движения ползуна')
ax2.set_xticks(range(0, 361, 30))
ax2.grid(True)
cursor, = ax2.plot([0], [Cz[0]], 'bo', ms=8)
vline = ax2.axvline(x=0, color='blue', lw=1, linestyle='--')

ход = Cz.max() - Cz.min()
ax2.set_title(f'Закон движения ползуна  (ход = {ход:.3f} м)')

def animate(i):
    by, bz = By[i], Bz[i]
    cz = Cz[i]

    crank_ln.set_data([Ay, by], [Az, bz])
    rod_ln.set_data([by, Cy], [bz, cz])
    slider.set_data([Cy], [cz])
    joint_B.set_data([by], [bz])

    deg = np.degrees(phi[i])
    cursor.set_data([deg], [cz])
    vline.set_xdata([deg])
    return crank_ln, rod_ln, slider, joint_B, cursor, vline

ani = animation.FuncAnimation(fig, animate, frames=len(phi),
                              interval=30, blit=True, repeat=True)
plt.tight_layout()
plt.show()
