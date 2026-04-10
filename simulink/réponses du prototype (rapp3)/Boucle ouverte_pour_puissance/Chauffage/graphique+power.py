from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import numba

# À FAIRE POUR TESTER LA PUISSANCE :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# Choisir le numéro de thermistance à utiliser
thermistance = 1

# Loader le fichier désiré
base_dir = os.path.dirname(os.path.abspath(__file__))
file_name = "20pwm_depuis29.csv"
csv_path = os.path.join(base_dir, file_name)

# Modifier les paramètres pour qu'ils match avec les données expérimentales --------------------------------------
t_simulation = 799.900
essais_puissance = []

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
longueur = 117.28e-3
largeur = 61.57e-3
epaisseur = 1.61e-3
T_init = 32.4 + 273.15
k = 167
rho = 2700
cp = 900
h_conv = 13.65
dx = 0.001

# lecture CSV expérimentale
data = pd.read_csv(csv_path)
data = data.sort_values("Temps (s)")

temps_exp = data["Temps (s)"].values

if thermistance == 1:
    temperature_exp = data["Thermistance 1 - T1 (°C)"].values
elif thermistance == 2:
    temperature_exp = data["Thermistance 2 - T2 (°C)"].values
elif thermistance == 3:
    temperature_exp = data["Thermistance 3 - T3 (°C)"].values

# ULTRA-OPTIMIZED VERSION - Vectorized operations where possible
@numba.jit(nopython=True)
def compute_timestep_ultra(T, T_init, alpha_dt_dx2, alpha_dt_dy2,
                           coeff_conv, coeff_face_2, P_cell_dt_vol,
                           x0, rx, y0, ry, nx, ny):

    T_new = T.copy()

    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            laplacian_x = (T[i + 1, j] - 2 * T[i, j] + T[i - 1, j]) * alpha_dt_dx2
            laplacian_y = (T[i, j + 1] - 2 * T[i, j] + T[i, j - 1]) * alpha_dt_dy2
            T_new[i, j] += laplacian_x + laplacian_y

    for j in range(1, ny - 1):
        T_new[0, j] += alpha_dt_dx2 * (T[1, j] - T[0, j]) + \
                       alpha_dt_dy2 * (T[0, j + 1] - 2 * T[0, j] + T[0, j - 1])
        T_new[nx - 1, j] += alpha_dt_dx2 * (T[nx - 2, j] - T[nx - 1, j]) + \
                            alpha_dt_dy2 * (T[nx - 1, j + 1] - 2 * T[nx - 1, j] + T[nx - 1, j - 1])

    for i in range(1, nx - 1):
        T_new[i, 0] += alpha_dt_dx2 * (T[i + 1, 0] - 2 * T[i, 0] + T[i - 1, 0]) + \
                       alpha_dt_dy2 * (T[i, 1] - T[i, 0])
        T_new[i, ny - 1] += alpha_dt_dx2 * (T[i + 1, ny - 1] - 2 * T[i, ny - 1] + T[i - 1, ny - 1]) + \
                            alpha_dt_dy2 * (T[i, ny - 2] - T[i, ny - 1])

    T_new[0, 0] += alpha_dt_dx2 * (T[1, 0] - T[0, 0]) + alpha_dt_dy2 * (T[0, 1] - T[0, 0])
    T_new[0, ny - 1] += alpha_dt_dx2 * (T[1, ny - 1] - T[0, ny - 1]) + alpha_dt_dy2 * (T[0, ny - 2] - T[0, ny - 1])
    T_new[nx - 1, 0] += alpha_dt_dx2 * (T[nx - 2, 0] - T[nx - 1, 0]) + alpha_dt_dy2 * (T[nx - 1, 1] - T[nx - 1, 0])
    T_new[nx - 1, ny - 1] += alpha_dt_dx2 * (T[nx - 2, ny - 1] - T[nx - 1, ny - 1]) + alpha_dt_dy2 * (
                T[nx - 1, ny - 2] - T[nx - 1, ny - 1])

    T_diff = T_init - T
    for i in range(nx):
        for j in range(ny):
            T_new[i, j] += coeff_face_2 * T_diff[i, j]

    for j in range(ny):
        T_new[0, j] += coeff_conv * T_diff[0, j]
        T_new[nx - 1, j] += coeff_conv * T_diff[nx - 1, j]

    for i in range(nx):
        T_new[i, 0] += coeff_conv * T_diff[i, 0]
        T_new[i, ny - 1] += coeff_conv * T_diff[i, ny - 1]

    for i in range(max(0, x0 - rx), min(nx, x0 + rx + 1)):
        for j in range(max(0, y0 - ry), min(ny, y0 + ry + 1)):
            T_new[i, j] += P_cell_dt_vol

    return T_new

alpha = k / (rho * cp)
dy = dx
dt = dx ** 2 / (4 * alpha)

nx, ny = int(longueur / dx), int(largeur / dy)
nt = int(t_simulation / dt)

alpha_dt_dx2 = alpha * dt / (dx ** 2)
alpha_dt_dy2 = alpha * dt / (dy ** 2)
coeff_conv = (h_conv * dt) / (rho * cp * dx)
coeff_face_2 = 2 * h_conv * dt / (rho * cp * epaisseur)

def simuler_puissance(puissance):
    Pin = puissance
    T = np.full((nx, ny), T_init, dtype=float)

    act_size = 15e-3
    rx = int((act_size / 2) / dx)
    ry = int((act_size / 2) / dy)

    cell_volume = dx * dy * epaisseur
    nb_cells = (2 * rx + 1) * (2 * ry + 1)
    P_cell = Pin / nb_cells
    P_cell_dt_vol = (P_cell * dt) / (rho * cp * cell_volume)

    therm1_locx, therm1_locy = int(14.87e-3 / dx), int((largeur / 2) / dx)
    therm2_locx, therm2_locy = int(59.35e-3 / dx), int((largeur / 2) / dx)
    therm3_locx, therm3_locy = int(104.99e-3 / dx), int((largeur / 2) / dx)

    x0, y0 = therm1_locx, therm1_locy

    temps = []
    T1, T2, T3 = [], [], []

    for t in range(nt):
        T = compute_timestep_ultra(T, T_init, alpha_dt_dx2, alpha_dt_dy2,
                                   coeff_conv, coeff_face_2, P_cell_dt_vol,
                                   x0, rx, y0, ry, nx, ny)

        temps.append(t * dt)
        if thermistance == 1:
            T1.append(T[therm1_locx, therm1_locy] - 273.15)
        if thermistance == 2:
            T2.append(T[therm2_locx, therm2_locy] - 273.15)
        if thermistance == 3:
            T3.append(T[therm3_locx, therm3_locy] - 273.15)

    if thermistance == 1:
        return temps, T1
    elif thermistance == 2:
        return temps, T2
    elif thermistance == 3:
        return temps, T3

fig = plt.figure()
ax1 = fig.add_subplot(111)

for pin in essais_puissance:
    time, temp = simuler_puissance(pin)
    ax1.plot(time, temp, label=f'puissance {pin}')

ax1.plot(temps_exp, temperature_exp, label='exp')

plt.xlabel("Temps [s]")
plt.ylabel("Température [°C]")
plt.title("Température des thermistances")
plt.legend()
plt.show()