
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import json
import os

# Coefficient de résolution(prend les valeurs entre 1 et 14, mettre 1 pour avoir le code normal)
# res = 2 #4 c'est pas mal le meilleur rapport vitesse/qualité

# Ouvrir le fichier et charger les paramètres
base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, "params_sim.json")

with open(json_path, "r") as f:
    params = json.load(f)

# Extraire les paramètres
longueur = params["longueur"]
largeur = params["largeur"]
epaisseur = params["epaisseur"]
T_init = params["T_init"] + 273.15
t_simulation = params["t_simulation"]
k = params["k"]
rho = params["rho"]
cp = params["cp"]
h_conv = params["h_conv"]
dx = params["dx"]
Pin = params["Pin"]

# Quels paramètres doit-on pouvoir lire dans un fichier json?
alpha = k / (rho * cp)  # 0.000084
dy = dx
dt = dx**2 / (4 * alpha)  # 0.003

nx, ny = int(longueur / dx), int(largeur / dy)
nt = int(t_simulation / dt)

coeff_conv = (h_conv * dt) / (rho * cp * dx)
coeff_face = h_conv * dt / (rho * cp * epaisseur)

T = np.full((nx, ny), T_init, dtype=float)

# Puissance
act_size = 20e-3  # 20 mm
rx = int((act_size/2) / dx)
ry = int((act_size/2) / dy)

cell_volume = dx * dy * epaisseur
nb_cells = (2*rx + 1) * (2*ry + 1)
P_cell = Pin/nb_cells

save_interval = 10
frames = []

thermistance1 = np.zeros(nt)
therm1_locx, therm1_locy = int(14.87e-3/dx), int((largeur/2)/dx)
thermistance2 = np.zeros(nt)
therm2_locx, therm2_locy = int(59.35e-3/dx), int((largeur/2)/dx)
thermistance3 = np.zeros(nt)
therm3_locx, therm3_locy = int(104.99e-3/dx), int((largeur/2)/dx)

x0, y0 = therm1_locx, therm1_locy

# ============= OPTIMISATION: Facteur de vitesse =============
# 1 seconde réelle = SPEED_FACTOR secondes simulées
SPEED_FACTOR = 50  # Changez cette valeur pour accélérer/ralentir
PLOT_UPDATE_INTERVAL = 5000  # Mise à jour tous les X iterations (au lieu de 10)

plt.ion()

# FIGURE 1 : thermistances
figT, axT = plt.subplots(figsize=(6,4))

line1, = axT.plot([], [], label="Thermistance 1", linewidth=2)
line2, = axT.plot([], [], label="Thermistance 2", linewidth=2)
line3, = axT.plot([], [], label="Thermistance 3", linewidth=2)

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

# ============= OPTIMISATION: Créer la surface une seule fois =============
surf = ax3D.plot_surface(
    X, Y, T - 273,
    cmap='inferno',
    rstride=1, cstride=1,
    linewidth=0,
    antialiased=False  # Plus rapide
)

ax3D.set_xlabel("x [m]")
ax3D.set_ylabel("y [m]")
ax3D.set_zlabel("Température [°C]")
ax3D.set_zlim(20, 50)  # Augmenté pour voir la montée en température

plt.show(block=False)

gain_par_pas = (P_cell * dt) / (rho * cp * cell_volume)
print(f"Diagnostic : Chaque itération ajoute +{gain_par_pas:.6f} °C dans la zone active")
print(f"Facteur de vitesse : {SPEED_FACTOR}x (1s réel = {SPEED_FACTOR}s simulés)")
print(f"Nombre total d'itérations : {nt}")

# Timer
start_time = time.time()
last_plot_time = start_time

# ============= OPTIMISATION: Utiliser nt au lieu de 1000 =============
for t in range(nt):
    t_sim = t * dt  # temps simulé à l'étape t

    dT_diff = np.zeros_like(T)
    
    # Equation de diffusion sur les points internes
    dT_diff[1:-1, 1:-1] = dt*alpha*(
        (T[2:, 1:-1] - 2*T[1:-1, 1:-1] + T[:-2, 1:-1]) / dx**2 +
        (T[1:-1, 2:] - 2*T[1:-1, 1:-1] + T[1:-1, :-2]) / dy**2
    )

    # BORDS
    # bord à x=0
    dT_diff[0, 1:-1] = dt*alpha*((T[1, 1:-1] - T[0, 1:-1]) / dx**2 +
        (T[0, 2:] - 2*T[0, 1:-1] + T[0, :-2]) / dy**2)
    # bord à x=-1
    dT_diff[-1, 1:-1] = dt*alpha*((-T[-1, 1:-1] + T[-2, 1:-1]) / dx**2 +
        (T[-1, 2:] - 2*T[-1, 1:-1] + T[-1, :-2]) / dy**2)
    # bord à y=0
    dT_diff[1:-1, 0] = dt*alpha*((T[2:, 0] - 2*T[1:-1, 0] + T[:-2, 0]) / dx**2 +
        (T[1:-1, 1] - T[1:-1, 0]) / dy**2)
    # bord à y=-1
    dT_diff[1:-1, -1] = dt*alpha*((T[2:, -1] - 2*T[1:-1, -1] + T[:-2, -1]) / dx**2 +
        (T[1:-1, -2] - T[1:-1, -1]) / dy**2)
    
    # COINS
    # x=0, y=0
    dT_diff[0, 0] = dt*alpha*((T[1, 0] - T[0, 0]) / dx**2 +
        (T[0, 1] - T[0, 0]) / dy**2)
    # x=0, y=-1
    dT_diff[0, -1] = dt*alpha*((T[1, -1] - T[0, -1]) / dx**2 +
        (T[0, -2] - T[0, -1]) / dy**2)
    # x=-1, y=0
    dT_diff[-1, 0] = dt*alpha*((T[-2, 0] - T[-1, 0]) / dx**2 +
        (T[-1, 1] - T[-1, 0]) / dy**2)
    # x=-1, y=-1
    dT_diff[-1, -1] = dt*alpha*((T[-2, -1] - T[-1, -1] ) / dx**2 +
        (T[-1, -2] - T[-1, -1]) / dy**2)  

    # Convection sur les bords
    dT_conv_lat = np.zeros_like(T)
    dT_conv_lat[0, :]  += coeff_conv * (T_init - T[0, :])
    dT_conv_lat[-1, :] += coeff_conv * (T_init - T[-1, :])
    dT_conv_lat[:, 0]  += coeff_conv * (T_init - T[:, 0])
    dT_conv_lat[:, -1] += coeff_conv * (T_init - T[:, -1])
    
    # Convection sur la face supérieure
    dT_conv_face = np.zeros_like(T)
    dT_conv_face += 2*coeff_face * (T_init - T)

    # Ajout de la puissance sur la zone active
    dT_source = np.zeros_like(T)
    dT_source[x0-rx:x0+rx+1, y0-ry:y0+ry+1] += (P_cell * dt) / (rho * cp * cell_volume)

    T += dT_diff + dT_source + dT_conv_face + dT_conv_lat

    perte_par_pas = coeff_face * (T[x0, y0] - T_init)
    
    if t % 500 == 0:  # On affiche le bilan toutes les 500 itérations
        balance = gain_par_pas - perte_par_pas
        print(f"T_max: {T[x0, y0]-273.15:.2f}°C | Gain: +{gain_par_pas:.6f} | Perte: -{perte_par_pas:.6f} | Net: {balance:.6f}")

    # Stockage des températures aux thermistances
    temps.append(t * dt)
    T1.append(T[therm1_locx, therm1_locy] - 273)
    T2.append(T[therm2_locx, therm2_locy] - 273)
    T3.append(T[therm3_locx, therm3_locy] - 273)

    # ============= OPTIMISATION: Mise à jour moins fréquente + timing réel =============
    current_time = time.time()
    elapsed_real = current_time - start_time
    target_real_time = t_sim / SPEED_FACTOR  # Temps réel cible basé sur le facteur de vitesse
    
    # Mettre à jour les graphiques seulement si:
    # 1. C'est le bon intervalle ET
    # 2. Assez de temps réel s'est écoulé (pour ne pas surcharger)
    if t % PLOT_UPDATE_INTERVAL == 0 and (current_time - last_plot_time) > 0.1:
        # Mise à jour graphique des thermistances
        line1.set_data(temps, T1)
        line2.set_data(temps, T2)
        line3.set_data(temps, T3)
        axT.set_xlim(0, temps[-1])
        axT.set_ylim(min(T1 + T2 + T3) - 1, max(T1 + T2 + T3) + 1)
        figT.canvas.draw()
        figT.canvas.flush_events()

        # ============= OPTIMISATION: Mettre à jour les données au lieu de recréer =============
        surf.remove()
        surf = ax3D.plot_surface(
            X, Y, T - 273,
            cmap='inferno',
            rstride=1, cstride=1,
            linewidth=0,
            antialiased=False
        )
        ax3D.set_title(f"Température de la plaque – t = {t*dt:.2f} s)")
        fig3D.canvas.draw()
        fig3D.canvas.flush_events()
        
        last_plot_time = current_time

    # Timer terminal
    elapsed = time.time() - start_time
    progress = 100 * t / nt
    eta = (elapsed / (t+1)) * (nt - t)
    print(f"Progress: {progress:.1f}% | Temps réel: {elapsed:.1f}s | Temps sim: {t_sim:.1f}s | ETA: {eta:.0f}s", end='\r')

# Timer reste affiché dans le terminal
elapsed = time.time() - start_time
print(f"\nProgress: 100.0% - Temps écoulé: {elapsed:.1f}s - Temps simulé: {t_simulation:.1f}s")
print(f"Ratio réel: {t_simulation/elapsed:.1f}x temps réel")

plt.ioff()
plt.show()
