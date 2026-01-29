import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import json
import os, json

#coefficient de résolution(prend les valeurs entre 1 et 14, mettre 1 pour avoir le code normal)
res = 4 #4 c'est pas mal le meilleur rapport vitesse/qualité


# ouvrir le fichier et charger les paramètres
base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, "params_sim.json")

with open(json_path, "r") as f:
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
dx = params["dx"] * res
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

act_size = 20e-3  # 5 mm
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

#make it go faster
target_frames = nt/save_interval # nombre total de frames

plt.ion()

# FIGURE 1 : thermistances

figT, axT = plt.subplots(figsize=(6,4))

line1, = axT.plot([], [], label="Thermistance 1")
line2, = axT.plot([], [], label="Thermistance 2")
line3, = axT.plot([], [], label="Thermistance 3")

axT.set_xlabel("Temps [s]")
axT.set_ylabel("Température [°C]")
axT.set_title("Température des thermistances")
axT.grid(True)
axT.legend()

temps = []
T1, T2, T3 = [], [], []

# FIGURE 2 : surface 3D T(x,y)

fig3D = plt.figure(figsize=(7,5))
ax3D = fig3D.add_subplot(111, projection='3d')

x = np.linspace(0, longueur, nx)
y = np.linspace(0, largeur, ny)
X, Y = np.meshgrid(x, y, indexing='ij')

surf = ax3D.plot_surface(
    X, Y, T - 273,
    cmap='inferno',
    rstride=1, cstride=1,
    linewidth=0
)

ax3D.set_xlabel("x [m]")
ax3D.set_ylabel("y [m]")
ax3D.set_zlabel("Température [°C]")
ax3D.set_zlim(20, 30)

plt.show()


#timer
start_time = time.time()

for t in range(nt):
    t_sim = t * dt  # temps simulé à l'étape t

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
    
    # convection sur la face supérieure
    T += coeff_face * (T_init - T)

    # ajout de la puissance sur la zone active
    T[ x0-rx:x0+rx+1, y0-ry:y0+ry+1] += (P_cell * dt) / (rho * cp * cell_volume)

    # stockage des températures aux thermistances
    temps.append(t * dt)
    T1.append(T[therm1_locx, therm1_locy] - 273)
    T2.append(T[therm2_locx, therm2_locy] - 273)
    T3.append(T[therm3_locx, therm3_locy] - 273)

    # mise à jour des graphiques toutes les 200 itérations
    if t % 200 == 0:
        # mise à jour graphique des thermistances
        line1.set_data(temps, T1)
        line2.set_data(temps, T2)
        line3.set_data(temps, T3)
        axT.set_xlim(0, temps[-1])
        axT.set_ylim(min(T1 + T2 + T3) - 1, max(T1 + T2 + T3) + 1)
        figT.canvas.draw()
        figT.canvas.flush_events()

        # mise à jour graphique 3D
        surf.remove()
        surf = ax3D.plot_surface(
            X, Y, T - 273,
            cmap='inferno',
            rstride=1, cstride=1,
            linewidth=0
        )
        ax3D.set_title(f"Température de la plaque – t = {t*dt:.2f} s")
        fig3D.canvas.draw()
        fig3D.canvas.flush_events()

    #timer terminal
    elapsed = time.time() - start_time
    progress = 100 * t / nt
    print(f"Progress: {progress:.1f}% - Durée: {elapsed:.1f}s", end='\r')

    #temps réel
    wait = t_sim - elapsed
    if wait > 0:
        time.sleep(wait)

#timer reste affiché dans le terminal
elapsed = time.time() - start_time
print(f"Progress: 100.0% - Elapsed time: {elapsed:.1f}s")

plt.ioff()
plt.show()
