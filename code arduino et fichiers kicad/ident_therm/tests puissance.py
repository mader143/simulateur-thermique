# Lire le fichier csv
# Partir la simulation, pouvoir mettre différentes puissances simultanément?

import numpy as np
import matplotlib.pyplot as plt
import os
import numba

# À FAIRE POUR TESTER LA PUISSANCE :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# Choisir le numéro de thermistance à utiliser
thermistance = 1

# Loader le fichier désiré
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "T1v2/10_30_t1.csv")

# Modifier les paramètres pour qu'ils match avec les données expérimentales --------------------------------------
t_simulation = 800
essais_puissance = [1.67, 1.68]  # Puissances à tester (en watts)


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
longueur = 117.28e-3
largeur = 61.57e-3
epaisseur = 1.61e-3
T_init = 23.37 + 273.15
k = 167
rho = 2700
cp = 900
h_conv = 13.65
dx = 0.001


# Si on veut éventuellement tester d'autres paramètres, on ara juste à changer le 'essais_puissance' par
# une autre donnée (et il faudra changer la boucle for à la fin).




file1 = open(csv_path, "r")
line = file1.readline()

temps_exp = []
temperature_exp = []

i = 0
for line in file1:
    i += 1
    if i > 0:
        words = line.split(",")
        temps_exp.append(float(words[0]))
        temperature_exp.append(float(words[1]))

temps_exp = np.array(temps_exp)
temperature_exp = np.array(temperature_exp)









# ULTRA-OPTIMIZED VERSION - Vectorized operations where possible
@numba.jit(nopython=True)
def compute_timestep_ultra(T, T_init, alpha_dt_dx2, alpha_dt_dy2,
                           coeff_conv, coeff_face_2, P_cell_dt_vol,
                           x0, rx, y0, ry, nx, ny):
    """
    Ultra-optimized with vectorized boundary operations.
    """
    T_new = T.copy()


    # Diffusion - interior points
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            laplacian_x = (T[i + 1, j] - 2 * T[i, j] + T[i - 1, j]) * alpha_dt_dx2
            laplacian_y = (T[i, j + 1] - 2 * T[i, j] + T[i, j - 1]) * alpha_dt_dy2
            T_new[i, j] += laplacian_x + laplacian_y

    # Boundary diffusion - edges
    for j in range(1, ny - 1):
        # x=0 edge
        T_new[0, j] += alpha_dt_dx2 * (T[1, j] - T[0, j]) + \
                       alpha_dt_dy2 * (T[0, j + 1] - 2 * T[0, j] + T[0, j - 1])
        # x=nx-1 edge
        T_new[nx - 1, j] += alpha_dt_dx2 * (T[nx - 2, j] - T[nx - 1, j]) + \
                            alpha_dt_dy2 * (T[nx - 1, j + 1] - 2 * T[nx - 1, j] + T[nx - 1, j - 1])

    for i in range(1, nx - 1):
        # y=0 edge
        T_new[i, 0] += alpha_dt_dx2 * (T[i + 1, 0] - 2 * T[i, 0] + T[i - 1, 0]) + \
                       alpha_dt_dy2 * (T[i, 1] - T[i, 0])
        # y=ny-1 edge
        T_new[i, ny - 1] += alpha_dt_dx2 * (T[i + 1, ny - 1] - 2 * T[i, ny - 1] + T[i - 1, ny - 1]) + \
                            alpha_dt_dy2 * (T[i, ny - 2] - T[i, ny - 1])

    # Corners
    T_new[0, 0] += alpha_dt_dx2 * (T[1, 0] - T[0, 0]) + alpha_dt_dy2 * (T[0, 1] - T[0, 0])
    T_new[0, ny - 1] += alpha_dt_dx2 * (T[1, ny - 1] - T[0, ny - 1]) + alpha_dt_dy2 * (T[0, ny - 2] - T[0, ny - 1])
    T_new[nx - 1, 0] += alpha_dt_dx2 * (T[nx - 2, 0] - T[nx - 1, 0]) + alpha_dt_dy2 * (T[nx - 1, 1] - T[nx - 1, 0])
    T_new[nx - 1, ny - 1] += alpha_dt_dx2 * (T[nx - 2, ny - 1] - T[nx - 1, ny - 1]) + alpha_dt_dy2 * (
                T[nx - 1, ny - 2] - T[nx - 1, ny - 1])

    # Face convection (ALL cells) - vectorized calculation
    T_diff = T_init - T
    for i in range(nx):
        for j in range(ny):
            T_new[i, j] += coeff_face_2 * T_diff[i, j]

    # Lateral edge convection
    for j in range(ny):
        T_new[0, j] += coeff_conv * T_diff[0, j]
        T_new[nx - 1, j] += coeff_conv * T_diff[nx - 1, j]

    for i in range(nx):
        T_new[i, 0] += coeff_conv * T_diff[i, 0]
        T_new[i, ny - 1] += coeff_conv * T_diff[i, ny - 1]

    # Heat source
    for i in range(max(0, x0 - rx), min(nx, x0 + rx + 1)):
        for j in range(max(0, y0 - ry), min(ny, y0 + ry + 1)):
            T_new[i, j] += P_cell_dt_vol
    return T_new







alpha = k / (rho * cp)
dy = dx
dt = dx ** 2 / (4 * alpha)

nx, ny = int(longueur / dx), int(largeur / dy)
nt = int(t_simulation / dt)


# Pre-calculate constants
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

    # ============ REAL-TIME PLOTTING SETUP ============
    PLOT_2D_INTERVAL = 10000  # Update 2D plot every N iterations
    PLOT_3D_INTERVAL = 10000  # Update 3D plot every N iterations (heavier)






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
    elif thermistance ==2:
        return temps, T2
    elif thermistance ==3:

        return temps, T3
    else:
        print('Pas de thermistance choisie, erreur')









fig = plt.figure()
ax1 = fig.add_subplot(111)


for pin in essais_puissance:
    time, temp = simuler_puissance(pin)
    print(f'température intiale: {temp[0]}')
    ax1.plot(time, temp, label=f'puissance {pin}')
    print(f'essai de puissance {pin} terminé')

ax1.plot(temps_exp, temperature_exp, label='exp')




plt.xlabel("Temps [s]")
plt.ylabel("Température [°C]")
plt.title("Température des thermistances")
plt.legend()
plt.show()

