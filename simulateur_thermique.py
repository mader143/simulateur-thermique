import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter, FuncAnimation
from mpl_toolkits.mplot3d import Axes3D


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

nx, ny, nt = int(longueur / dx), int(largeur / dy), int(t_simulation/dt)

#Puissance
Pin = 1
Pin_loc_x = 0
Pin_loc_y = int(round((largeur / 2) / dy))
P = np.zeros((nx, ny))
P[Pin_loc_x, Pin_loc_y] = Pin

T = np.full((nx, ny, nt), T_init)
T[0, :, :] = 300

# #mettre la température de l'actuateur

# plaque[:, :1, :] = T_act

# thermistance1 = np.zeros(nt)
# therm1_loc = (14.87e-3, largeur/2) #j'ai mis position en y a mi chemin
# thermistance2 = np.zeros(nt)
# therm2_loc = (59.35e-3, largeur/2)
# thermistance3 = np.zeros(nt)
# therm3_loc = (104.99e-3, largeur/2)

print(T.shape)
print(T)

for t in range(nt-1):
    for i in range(nx):
        for j in range(ny):
            
            # différence centrée pour le milieu et regressive/progressive pour les côtés
            if i == 0 and j != 0 and j != ny-1:
                T[i, j, t+1] = T[i, j, t] + dt*alpha*(((T[i, j, t] - 2*T[i+1,j,t] + T[i+2,j,t]) / dx**2)) + ((T[i, j+1, t] - 2*T[i,j,t] + T[i,j-1,t])/dy**2)
                T[i, j, t+1] += dt/(rho*cp) * h_conv * (T_init - T[i, j, t]) * aire_bouts / volume

            elif i == nx-1 and j != 0 and j != ny-1:
                T[i, j, t+1] = T[i, j, t] + dt*alpha*(((T[i, j, t] - 2*T[i-1,j,t] + T[i-2,j,t]) / dx**2)) + ((T[i, j+1, t] - 2*T[i,j,t] + T[i,j-1,t])/dy**2)
                T[i, j, t+1] += dt/(rho*cp) * h_conv * (T_init - T[i, j, t]) * aire_bouts / volume

            elif j == 0 and i != 0 and i != nx-1:
                T[i, j, t+1] = T[i, j, t] + dt*alpha*(((T[i+1, j, t] - 2*T[i,j,t] + T[i-1,j,t]) / dx**2)) + ((T[i, j, t] - 2*T[i,j+1,t] + T[i,j+2,t])/dy**2)
                T[i, j, t+1] += dt/(rho*cp) * h_conv * (T_init - T[i, j, t]) * aire_sides / volume

            elif j == ny-1 and i != 0 and i != nx-1:
                T[i, j, t+1] = T[i, j, t] + dt*alpha*(((T[i+1, j, t] - 2*T[i,j,t] + T[i-1,j,t]) / dx**2)) + ((T[i, j, t] - 2*T[i,j-1,t] + T[i,j-2,t])/dy**2)
                T[i, j, t+1] += dt/(rho*cp) * h_conv * (T_init - T[i, j, t]) * aire_sides / volume
            
            # différence regressive/progressive pour les 4 coins
            elif j == 0 and i == 0:
                T[i, j, t+1] = T[i, j, t] + dt*alpha*(((T[i, j, t] - 2*T[i+1,j,t] + T[i+2,j,t]) / dx**2)) + ((T[i, j, t] - 2*T[i,j+1,t] + T[i,j+2,t])/dy**2)
                T[i, j, t+1] += dt/(rho*cp) * h_conv * (T_init - T[i, j, t]) * (aire_sides+aire_bouts) / volume

            elif j == 0 and i == nx-1:
                T[i, j, t+1] = T[i, j, t] + dt*alpha*(((T[i, j, t] - 2*T[i-1,j,t] + T[i-2,j,t]) / dx**2)) + ((T[i, j, t] - 2*T[i,j+1,t] + T[i,j+2,t])/dy**2)
                T[i, j, t+1] += dt/(rho*cp) * h_conv * (T_init - T[i, j, t]) * (aire_sides+aire_bouts) / volume

            elif j == ny-1 and i == 0:
                T[i, j, t+1] = T[i, j, t] + dt*alpha*(((T[i, j, t] - 2*T[i+1,j,t] + T[i+2,j,t]) / dx**2)) + ((T[i, j, t] - 2*T[i,j-1,t] + T[i,j-2,t])/dy**2)
                T[i, j, t+1] += dt/(rho*cp) * h_conv * (T_init - T[i, j, t]) * (aire_sides+aire_bouts) / volume

            elif j == ny-1 and i == nx-1:
                T[i, j, t+1] = T[i, j, t] + dt*alpha*(((T[i, j, t] - 2*T[i-1,j,t] + T[i-2,j,t]) / dx**2)) + ((T[i, j, t] - 2*T[i,j-1,t] + T[i,j-2,t])/dy**2)
                T[i, j, t+1] += dt/(rho*cp) * h_conv * (T_init - T[i, j, t]) * (aire_sides+aire_bouts) / volume

            else:
                T[i, j, t+1] = T[i, j, t] + dt*alpha*(((T[i+1, j, t] - 2*T[i,j,t] + T[i-1,j,t]) / dx**2)) + ((T[i, j+1, t] - 2*T[i,j,t] + T[i,j-1,t])/dy**2)

            #T[i, j, t+1] += dt/(rho*cp) * P[i, j] / volume # je comprends pas pkoi on divise par le volume tout le temps....
            T[i, j, t+1] += dt/(rho*cp) * h_conv * (T_init - T[i, j, t]) * 2*aire_top / volume
    
    if t%100 == 0:
        print(t)

# ajout des températures des thermistances pour faire un graphique plus tard

# thermistance1[t] = T[therm1_loc, t]
# thermistance2[t] = T[therm2_loc, t]
# thermistance3[t] = T[therm3_loc, t]

print(T[:, :, nt-1])

def plotheatmap(u_k, k):
    # Clear the current plot figure
    plt.clf()

    plt.title(f"Temperature at t = {k*dt:.3f} unit time")
    plt.xlabel("x")
    plt.ylabel("y")

    # This is to plot u_k (u at time-step k)
    plt.pcolormesh(u_k, cmap=plt.cm.jet, vmin=0, vmax=100)
    plt.colorbar()

    return plt

anim = animation.FuncAnimation(plt.figure(), plotheatmap(T), interval=1, frames=nt, repeat=False)
anim.save("heat_equation_solution.gif")

print("Done!")
