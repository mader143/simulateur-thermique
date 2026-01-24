import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

#La simulation avec les boucles va FREAKING lentement cest insane alors jai regardé comment le faire en vectorisé


longueur, largeur = 117.28e-3, 61.57e-3
T_init = 21 + 273
t_simulation = 2.0
k, rho, cp = 205, 2700, 900
alpha = k / (rho * cp) 
h_conv = 20
dx = 1e-3
dy = dx
dt = dx**2 / (4 * alpha)

nx, ny = int(longueur / dx), int(largeur / dy)
nt = int(t_simulation / dt)

vol = dx * dy * dx
s_top = dx * dy
s_side = dx * dx
coeff_conv = (h_conv * dt) / (rho * cp * dx)

T = np.full((nx, ny), T_init, dtype=float)
Pin = 0.5

Pin_loc_y = 0
Pin_loc_x = int(round((largeur / 2) / dy))

save_interval = 10
frames = []

print(nt)

for t in range(nt):

    T_new = T.copy()
    
    # equation de diffusion sur les points internes
    laplacien = (
        (T_new[2:, 1:-1] - 2*T_new[1:-1, 1:-1] + T_new[:-2, 1:-1]) / dx**2 +
        (T_new[1:-1, 2:] - 2*T_new[1:-1, 1:-1] + T_new[1:-1, :-2]) / dy**2
    )
    
    T[1:-1, 1:-1] += dt * alpha * laplacien

    # convection sur les bords
    T[0, :]  += coeff_conv * (T_init - T[0, :])
    T[-1, :] += coeff_conv * (T_init - T[-1, :])
    T[:, 0]  += coeff_conv * (T_init - T[:, 0])
    T[:, -1] += coeff_conv * (T_init - T[:, -1])
    
    # convection face supérieure et inférieure
    T += 2 * coeff_conv * (T_init - T) # 2 faces

    # puissance
    T[Pin_loc_y, Pin_loc_x] += (Pin * dt) / (rho * cp * vol)

    if t % save_interval == 0:
        frames.append(T.copy())
        if t % 5000 == 0: print(f"Progression : {100*t/nt:.1f}%")


fig, ax = plt.subplots()
im = ax.imshow(frames[0].T, cmap='hot', origin='lower', 
               extent=[0, longueur, 0, largeur], vmin=T_init, vmax=330)
plt.colorbar(im, label="Température (K)")
ax.set_title("Diffusion thermique")

def update(i):
    im.set_array(frames[i].T)
    return [im]

ani = FuncAnimation(fig, update, frames=len(frames), interval=30, blit=True)
ani.save("diffusion.mp4", writer=FFMpegWriter(fps=30))
plt.show()