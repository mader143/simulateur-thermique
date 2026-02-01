import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import time

# utilisez pas lui il est ass
epaisseur = 1.61e-3
longueur = 117.28e-3 #en m
largeur = 61.57e-3 #en m
T_init = 21 + 273 #T pièce en kelvins
# T_act = 30 + 273
t_simulation = 1 #en secondes
k = 205
rho = 2700
cp = 900
alpha = k / (rho * cp)
h_conv = 20

dx=1e-3
dy = dx
dz = dx
dt = dx**2 / (8 * alpha) #à ajuster

aire_bouts = dy * dz
aire_sides = dx * dz
aire_top = dx * dy
volume = dx * dy * dz

nx, ny, nt = int(longueur / dx), int(largeur / dy), int(round(t_simulation / dt))

#Puissance
Pin = 3
Pin_loc_y = 0
Pin_loc_x = int(round((largeur / 2) / dy))
P = np.zeros((nx, ny))
P[Pin_loc_x, Pin_loc_y] = Pin

T = np.full((nx, ny), T_init)
T_new = np.zeros_like(T)

# thermistance1 = np.zeros(nt)
# therm1_loc = (14.87e-3, largeur/2) #j'ai mis position en y a mi chemin
# thermistance2 = np.zeros(nt)
# therm2_loc = (59.35e-3, largeur/2)
# thermistance3 = np.zeros(nt)
# therm3_loc = (104.99e-3, largeur/2)

save_interval = 10
frames = []

print("Calcul de la diffusion en cours...")

for t in range(nt):
    for i in range(nx):
        for j in range(ny):
            T_new[i, j] = T[i, j]
                
            # différence centrée pour le milieu et regressive/progressive pour les côtés
            if i == 0 and j != 0 and j != ny-1:
                T_new[i, j] += dt*alpha*(((T[i, j] - 2*T[i+1,j] + T[i+2,j]) / dx**2) + ((T[i, j+1] - 2*T[i,j] + T[i,j-1])/dy**2))
                T_new[i, j] += dt/(rho*cp) * h_conv * (T_init - T[i, j]) * aire_bouts / volume

            elif i == nx-1 and j != 0 and j != ny-1:
                T_new[i, j] += dt*alpha*((((T[i, j] - 2*T[i-1,j] + T[i-2,j]) / dx**2)) + ((T[i, j+1] - 2*T[i,j] + T[i,j-1])/dy**2))
                T_new[i, j] += dt/(rho*cp) * h_conv * (T_init - T[i, j]) * aire_bouts / volume

            elif j == 0 and i != 0 and i != nx-1:
                T_new[i, j] += dt*alpha*((((T[i+1, j] - 2*T[i,j] + T[i-1,j]) / dx**2)) + ((T[i, j] - 2*T[i,j+1] + T[i,j+2])/dy**2))
                T_new[i, j] += dt/(rho*cp) * h_conv * (T_init - T[i, j]) * aire_sides / volume

            elif j == ny-1 and i != 0 and i != nx-1:
                T_new[i, j] += dt*alpha*((((T[i+1, j] - 2*T[i,j] + T[i-1,j]) / dx**2)) + ((T[i, j] - 2*T[i,j-1] + T[i,j-2])/dy**2))
                T_new[i, j] += dt/(rho*cp) * h_conv * (T_init - T[i, j]) * aire_sides / volume
                
            # différence regressive/progressive pour les 4 coins
            elif j == 0 and i == 0:
                T_new[i, j] += dt*alpha*((((T[i, j] - 2*T[i+1,j] + T[i+2,j]) / dx**2)) + ((T[i, j] - 2*T[i,j+1] + T[i,j+2])/dy**2))
                T_new[i, j] += dt/(rho*cp) * h_conv * (T_init - T[i, j]) * (aire_sides+aire_bouts) / volume

            elif j == 0 and i == nx-1:
                T_new[i, j] += dt*alpha*((((T[i, j] - 2*T[i-1,j] + T[i-2,j]) / dx**2)) + ((T[i, j] - 2*T[i,j+1] + T[i,j+2])/dy**2))
                T_new[i, j] += dt/(rho*cp) * h_conv * (T_init - T[i, j]) * (aire_sides+aire_bouts) / volume

            elif j == ny-1 and i == 0:
                T_new[i, j] += dt*alpha*((((T[i, j] - 2*T[i+1,j] + T[i+2,j]) / dx**2)) + ((T[i, j] - 2*T[i,j-1] + T[i,j-2])/dy**2))
                T_new[i, j] += dt/(rho*cp) * h_conv * (T_init - T[i, j]) * (aire_sides+aire_bouts) / volume

            elif j == ny-1 and i == nx-1:
                T_new[i, j] += dt*alpha*((((T[i, j] - 2*T[i-1,j] + T[i-2,j]) / dx**2)) + ((T[i, j] - 2*T[i,j-1] + T[i,j-2])/dy**2))
                T_new[i, j] += dt/(rho*cp) * h_conv * (T_init - T[i, j]) * (aire_sides+aire_bouts) / volume

            else:
                T_new[i, j] += dt*alpha*((((T[i+1, j] - 2*T[i,j] + T[i-1,j]) / dx**2)) + ((T[i, j+1] - 2*T[i,j] + T[i,j-1])/dy**2))

            T[i, j] += dt/(rho*cp) * P[i, j] / epaisseur # je comprends pas pkoi on divise par le volume tout le temps....
            T_new[i, j] += dt/(rho*cp) * h_conv * (T_init - T[i, j]) *aire_top / volume
    
    T = T_new.copy()
    if t % save_interval == 0:
        frames.append(T.copy())

    if t%100 == 0:
        print(t)
# ajout des températures des thermistances pour faire un graphique plus tard

# thermistance1[t] = T[therm1_loc, t]
# thermistance2[t] = T[therm2_loc, t]
# thermistance3[t] = T[therm3_loc, t]

#animation
fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(frames[0], cmap='hot', origin='lower', extent=[0, longueur, 0, largeur])
plt.colorbar(im, label='Température (K)')
ax.set_title("Évolution de la température sur la plaque")

def update(i):
    im.set_array(frames[i])
    im.set_clim(T_init, 300)
    return [im]

ani = FuncAnimation(fig, update, frames=len(frames), interval=50, blit=True)

# save
filename = "diffusion_plaque.mp4"
try:
    writer = FFMpegWriter(fps=20)
    ani.save(filename, writer=writer)
    print(f"Vidéo réussie : {filename}")
except Exception as e:
    print(f"Erreur MP4 (FFmpeg) : {e}")
    print("Tentative de sauvegarde en GIF...")
    ani.save("diffusion_plaque.gif", writer='pillow')
    print("Fichier sauvegardé : diffusion_plaque.gif")

plt.show()
