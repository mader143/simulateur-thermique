import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import os
import numba
import csv
import random

# ------------------- ULTRA-OPTIMIZED FUNCTION -------------------
@numba.jit(nopython=True)
def compute_timestep_ultra(T, T_init, alpha_dt_dx2, alpha_dt_dy2, 
                          coeff_conv, coeff_face_2, P_cell_dt_vol,
                          x0, rx, y0, ry, nx, ny):
    T_new = T.copy()
    
    # Diffusion - interior points
    for i in range(1, nx-1):
        for j in range(1, ny-1):
            laplacian_x = (T[i+1, j] - 2*T[i, j] + T[i-1, j]) * alpha_dt_dx2
            laplacian_y = (T[i, j+1] - 2*T[i, j] + T[i, j-1]) * alpha_dt_dy2
            T_new[i, j] += laplacian_x + laplacian_y
    
    # Boundary diffusion - edges
    for j in range(1, ny-1):
        T_new[0, j] += alpha_dt_dx2 * (T[1, j] - T[0, j]) + alpha_dt_dy2 * (T[0, j+1] - 2*T[0, j] + T[0, j-1])
        T_new[nx-1, j] += alpha_dt_dx2 * (T[nx-2, j] - T[nx-1, j]) + alpha_dt_dy2 * (T[nx-1, j+1] - 2*T[nx-1, j] + T[nx-1, j-1])
    for i in range(1, nx-1):
        T_new[i, 0] += alpha_dt_dx2 * (T[i+1, 0] - 2*T[i, 0] + T[i-1, 0]) + alpha_dt_dy2 * (T[i, 1] - T[i, 0])
        T_new[i, ny-1] += alpha_dt_dx2 * (T[i+1, ny-1] - 2*T[i, ny-1] + T[i-1, ny-1]) + alpha_dt_dy2 * (T[i, ny-2] - T[i, ny-1])
    
    # Corners
    T_new[0, 0] += alpha_dt_dx2 * (T[1, 0] - T[0, 0]) + alpha_dt_dy2 * (T[0, 1] - T[0, 0])
    T_new[0, ny-1] += alpha_dt_dx2 * (T[1, ny-1] - T[0, ny-1]) + alpha_dt_dy2 * (T[0, ny-2] - T[0, ny-1])
    T_new[nx-1, 0] += alpha_dt_dx2 * (T[nx-2, 0] - T[nx-1, 0]) + alpha_dt_dy2 * (T[nx-1, 1] - T[nx-1, 0])
    T_new[nx-1, ny-1] += alpha_dt_dx2 * (T[nx-2, ny-1] - T[nx-1, ny-1]) + alpha_dt_dy2 * (T[nx-1, ny-2] - T[nx-1, ny-1])
    
    # Face convection
    T_diff = T_init - T
    for i in range(nx):
        for j in range(ny):
            T_new[i, j] += coeff_face_2 * T_diff[i, j]
    
    # Lateral edge convection
    for j in range(ny):
        T_new[0, j] += coeff_conv * T_diff[0, j]
        T_new[nx-1, j] += coeff_conv * T_diff[nx-1, j]
    for i in range(nx):
        T_new[i, 0] += coeff_conv * T_diff[i, 0]
        T_new[i, ny-1] += coeff_conv * T_diff[i, ny-1]
    
    # Heat source
    for i in range(max(0, x0-rx), min(nx, x0+rx+1)):
        for j in range(max(0, y0-ry), min(ny, y0+ry+1)):
            T_new[i, j] += P_cell_dt_vol
    
    return T_new

# ------------------- PARAMETERS -------------------
longueur = 117.28e-3
largeur = 61.57e-3
epaisseur = 01.61e-3
T_init = 24.31 + 273.15
t_simulation = 240
k = 167
rho = 2700
cp = 900
dx = 0.001
h_conv = 13.65
Pin = 1.68

#tt = 100
# Paramètres aléatoires (modifiable facilement)
#Pin_min, Pin_max = 1.55, 1.70
#Pin    = random.randrange(int(Pin_min*tt), int(Pin_max*tt)+1) / tt


# ------------------- DERIVED -------------------
alpha = k / (rho * cp)
dy = dx
dt = dx**2 / (4*alpha)
nx, ny = int(longueur/dx), int(largeur/dy)
nt = int(t_simulation/dt)

alpha_dt_dx2 = alpha * dt / (dx**2)
alpha_dt_dy2 = alpha * dt / (dy**2)
coeff_conv = (h_conv * dt)/(rho*cp*dx)
coeff_face_2 = 2 * h_conv * dt / (rho*cp*epaisseur)

T = np.full((nx, ny), T_init)
act_size = 0.02
rx = int((act_size/2)/dx)
ry = int((act_size/2)/dy)
cell_volume = dx*dy*epaisseur
nb_cells = (2*rx+1)*(2*ry+1)
P_cell = Pin/nb_cells
P_cell_dt_vol = P_cell*dt/(rho*cp*cell_volume)

# Thermistor locations
therm1_locx, therm1_locy = int(14.87e-3/dx), int((largeur/2)/dx)
therm2_locx, therm2_locy = int(59.35e-3/dx), int((largeur/2)/dx)
therm3_locx, therm3_locy = int(104.99e-3/dx), int((largeur/2)/dx)
x0, y0 = therm1_locx, therm1_locy

# ------------------- SIMULATION -------------------
temps, T1, T2, T3 = [], [], [], []
start_time = time.time()

for t in range(nt):
    T = compute_timestep_ultra(T, T_init, alpha_dt_dx2, alpha_dt_dy2,
                               coeff_conv, coeff_face_2, P_cell_dt_vol,
                               x0, rx, y0, ry, nx, ny)
    temps.append(t*dt)
    T1.append(T[therm1_locx, therm1_locy]-273)
    T2.append(T[therm2_locx, therm2_locy]-273)
    T3.append(T[therm3_locx, therm3_locy]-273)
    
    if t % 500 == 0:
        elapsed = time.time() - start_time
        progress = 100 * t / nt
        print(f"Progress: {progress:.1f}% | Elapsed: {elapsed:.1f}s", end='\r')

elapsed = time.time() - start_time
print(f"\nSimulation complete! Total time: {elapsed:.1f}s")

# ------------------- MOYENNES -------------------
derniers_100s = int(100/dt)
T1_moyenne = np.mean(T1[-derniers_100s:])
T2_moyenne = np.mean(T2[-derniers_100s:])
T3_moyenne = np.mean(T3[-derniers_100s:])

print(f"\nTempératures moyennes pour h = {h_conv:.2f} et Pin = {Pin:.2f}:")
print(f"T1: {T1_moyenne:.2f}, T2: {T2_moyenne:.2f}, T3: {T3_moyenne:.2f}")

# ------------------- SAUVEGARDE CSV -------------------
base_dir = os.getcwd()
csv_path = os.path.join(base_dir, "resultats_simulation.csv")

# Crée l’en-tête si nécessaire
if not os.path.exists(csv_path):
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["h_conv", "Pin", "T1_moyenne", "T2_moyenne", "T3_moyenne"])

# Écriture des données avec 3 chiffres après la virgule
donnees = [
    f"{h_conv:.3f}",
    f"{Pin:.3f}",
    f"{T1_moyenne:.3f}",
    f"{T2_moyenne:.3f}",
    f"{T3_moyenne:.3f}"
]

with open(csv_path, mode='a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(donnees)

print(f"Données sauvegardées dans {csv_path}")
