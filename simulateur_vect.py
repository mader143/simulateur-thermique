import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend non interactif
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import imageio.v2 as imageio
import time
import json

# ouvrir le fichier et charger les paramètres
with open("params_sim.json", "r") as f:
    params = json.load(f)

# extraire les paramètres
longueur = params["longueur"]
largeur = params["largeur"]
epaisseur = params["epaisseur"]
T_init = params["T_init"]+ 273.15
t_simulation = params["t_simulation"]
k = params["k"]
rho = params["rho"]
cp = params["cp"]
h_conv = params["h_conv"]
dx = params["dx"]
Pin = params["Pin"]

# quels paramètres doit-on pouvoir lire dans un fichier json?
alpha = k / (rho * cp) 
dy = dx
dt = dx**2 / (4 * alpha)

nx, ny = int(longueur / dx), int(largeur / dy)
nt = int(t_simulation / dt)
#résolution

vol = dx * dy * dx
coeff_conv = (h_conv * dt) / (rho * cp * dx)
coeff_face = 2 * h_conv * dt / (rho * cp * epaisseur)

T = np.full((nx, ny), T_init, dtype=float)

#puissance

act_size = 200e-3  # 5 mm
rx = int((act_size/2) / dx)
ry = int((act_size/2) / dy)

epaisseur = 1.61e-3
cell_volume = dx * dy * epaisseur

nb_cells = (2*rx + 1) * (2*ry + 1)

Pin = 5 # Watts
P_cell = Pin/nb_cells

save_interval = 10
frames = []

thermistance1 = np.zeros(nt)
therm1_locx, therm1_locy = int(14.87e-3/dx), int((largeur/2)/dx) #j'ai mis position en y a mi chemin
thermistance2 = np.zeros(nt)
therm2_locx, therm2_locy = int(59.35e-3/dx), int((largeur/2)/dx)
thermistance3 = np.zeros(nt)
therm3_locx, therm3_locy = int(104.99e-3/dx), int((largeur/2)/dx)

x0, y0 = therm1_locx, therm1_locy

Temps = np.arange(nt) * dt

writer = imageio.get_writer(
    'Temperature_thermistances.mp4',
    fps=30,
    codec='libx264',
    format='FFMPEG',
    macro_block_size=1
)

#make it go faster
target_frames = nt/save_interval # nombre total de frames

#fiure
fig, axs = plt.subplots(1, 3, figsize=(14,4))

line1, = axs[0].plot([], [])
axs[0].set_title("Température à la thermistance 1")
axs[0].set_xlabel("Temps [s]")
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
    
    # convection face supérieure
    T += coeff_face * (T_init - T)

    # puissance
    # T[Pin_loc_y, Pin_loc_x] += (Pin * dt) / (rho * cp *dx**2*1.61e-3) #DEMANDER A SIMON!!!!!
    T[ x0-rx:x0+rx+1, y0-ry:y0+ry+1] += (P_cell * dt) / (rho * cp * cell_volume)

    if t % 100 == 0: print(f"Progression : {100*t/nt:.1f}%")

    #on prends les frames de T pour le graphique de diffusion thermique
    if t % save_interval == 0:
            frames.append(T.copy())

    #update les graphiques des thermistances
    thermistance1[t] = T[therm1_locx, therm1_locy]
    thermistance2[t] = T[therm2_locx, therm2_locy]
    thermistance3[t] = T[therm3_locx, therm3_locy]

    if t % save_interval == 0 or t == nt-1:
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
print("\nVidéo enregistrée : Temperature_thermistances.mp4")

#graphique diffusion thermique
fig, ax = plt.subplots()
im = ax.imshow(frames[0].T, cmap='hot', origin='lower', 
            extent=[0, longueur, 0, largeur], vmin=T_init, vmax=300)
plt.colorbar(im, label="Température (K)")
ax.set_title("Diffusion thermique")

def update(i):
    im.set_array(frames[i].T)
    return [im]

ani = FuncAnimation(fig, update, frames=len(frames), interval=30, blit=True)
ani.save("diffusion.mp4", writer=FFMpegWriter(fps=30))
print("\nVidéo enregistrée : diffusion.mp4")