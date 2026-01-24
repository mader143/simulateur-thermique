import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend non interactif
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import imageio.v2 as imageio
import time

#La simulation avec les boucles va FREAKING lentement cest insane alors jai regardé comment le faire en vectorisé


longueur, largeur = 117.28e-3, 61.57e-3
T_init = 21 + 273
t_simulation = 10.0
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

thermistance1 = np.zeros(nt)
therm1_locx, therm1_locy = int(14.87e-3/dx), int((largeur/2)/dx) #j'ai mis position en y a mi chemin
thermistance2 = np.zeros(nt)
therm2_locx, therm2_locy = int(59.35e-3/dx), int((largeur/2)/dx)
thermistance3 = np.zeros(nt)
therm3_locx, therm3_locy = int(104.99e-3/dx), int((largeur/2)/dx)

Temps = np.arange(nt) * dt

writer = imageio.get_writer(
    'Temperature_thermistances.mp4',
    fps=30,
    codec='libx264',
    format='FFMPEG',
    macro_block_size=1
)

#make it go faster
target_frames = save_interval*t_simulation  # nombre total de frames
step = nt

#fiure
fig, axs = plt.subplots(1, 3, figsize=(14,4))

line1, = axs[0].plot([], [])
axs[0].set_title("Température à la thermistance 1")
axs[0].set_xlabel("Position [mm]")
axs[0].set_ylabel("Température [°C]")
axs[0].grid(True)

line2, = axs[1].plot([], [])
axs[1].set_title("Température à la thermistance 2")
axs[1].set_xlabel("Temps [s]")
axs[1].set_ylabel("Température [°C]")
axs[1].grid(True)

line3, = axs[2].plot([], [])
axs[2].set_title("Température à la thermistance 3")
axs[2].set_xlabel("Temps [s]")
axs[2].set_ylabel("Température [°C]")
axs[2].grid(True)

fig.tight_layout()

#timer
start_time = time.time()

print(nt)

for t in range(nt):

    T_new = T.copy()
    
    # equation de diffusion sur les points internes... cest quand meme compliqué
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

#update les graphiques des thermistances
    thermistance1[t] = T[therm1_locx, therm1_locy]
    thermistance2[t] = T[therm2_locx, therm2_locy]
    thermistance3[t] = T[therm3_locx, therm3_locy]

    if t % save_interval == 0:
        frames.append(T.copy())
        if t % 5000 == 0: print(f"Progression : {100*t/nt:.1f}%")

    if t % step == 0 or t == nt-1:
        #mise a jour graphique
        line1.set_data(Temps[:t+1], thermistance1[:t+1]-273)
        line2.set_data(Temps[:t+1], thermistance2[:t+1]-273)
        line3.set_data(Temps[:t+1], thermistance3[:t+1]-273)

        #mise a jour axes
        axs[0].set_xlim(0, max(Temps[t], 1e-8))
        axs[0].set_ylim(min(thermistance1[:t+1]-273)-1, max(thermistance1[:t+1]-273)+1)
        axs[1].set_xlim(0, max(Temps[t], 1e-8))
        axs[1].set_ylim(min(thermistance2[:t+1]-273)-1, max(thermistance2[:t+1]-273)+1)
        axs[2].set_xlim(0, max(Temps[t], 1e-8))
        axs[2].set_ylim(min(thermistance3[:t+1]-273)-1, max(thermistance3[:t+1]-273)+1)

        #to RGB
        buf, size = fig.canvas.print_to_buffer()
        width, height = size
        image = np.frombuffer(buf, dtype=np.uint8).reshape((height, width, 4))[:, :, :3]
        writer.append_data(image)

        #timer
        elapsed = time.time() - start_time
        progress = t / nt * 100

writer.close()
print("\nVidéo enregistrée : TemperatureDistribution1D_fast.mp4")

#diffusion thermique
fig, ax = plt.subplots()
im = ax.imshow(frames[0].T, cmap='hot', origin='lower', 
               extent=[0, longueur, 0, largeur], vmin=T_init, vmax=310)
plt.colorbar(im, label="Température (K)")
ax.set_title("Diffusion thermique")

def update(i):
    im.set_array(frames[i].T)
    return [im]

ani = FuncAnimation(fig, update, frames=len(frames), interval=30, blit=True)
ani.save("diffusion.mp4", writer=FFMpegWriter(fps=30))
plt.show()