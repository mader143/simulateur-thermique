import numpy as np
import matplotlib.pyplot as mpl
from matplotlib.animation import FFMpegWriter, FuncAnimation
from mpl_toolkits.mplot3d import Axes3D


longueur = 117.28e-3 #en m
largeur = 61.57e-3 #en m
T_init = 21 + 273 #T pièce en kelvins
# T_act = 30 + 273
t_simulation = 100 #en secondes
k = 205
rho = 2700
cp = 900
alpha = k / (rho * cp)
h_conv = 20

dx=1e-3
dy = dx
dz = dx
dt = 0.5*(dx)**2/alpha #à ajuster

aire_bouts = dy * dz
aire_sides = dx * dz
aire_top = dx * dy
volume = dx * dy * dz

nx, ny, nt = int(longueur / dx), int(largeur / dy), int(t_simulation/dt)

#Puissance
Pin = 0.5
Pin_loc_x = 0
Pin_loc_y = int(round((largeur / 2) / dy))
P = np.zeros((nx, ny))
P[Pin_loc_x, Pin_loc_y] = Pin

plaque = np.full((ny, nx, nt), T_init)

# #mettre la température de l'actuateur

# plaque[:, :1, :] = T_act

thermistance1 = np.zeros(nt)
therm1_loc = (14.87e-3, largeur/2) #j'ai mis position en y a mi chemin
thermistance2 = np.zeros(nt)
therm2_loc = (59.35e-3, largeur/2)
thermistance3 = np.zeros(nt)
therm3_loc = (104.99e-3, largeur/2)

# for t in range(nt):
#     for i in range(nx):
#         for j in range(ny):

#             if i == 0:
#             plaque[i, j, t+1] = ajout normal
#             plaque[i, j, t+1] = ajout de convection de côté x

#             elif i == nx-1:
#             plaque[i, j, t+1] = ajout normal
#             plaque[i, j, t+1] = ajout de convection de côté x

#             elif j == 0:
#             plaque[i, j, t] = ajout normal
#             plaque[i, j, t] = ajout de convection de côté y

#             elif j == ny-1:
#             plaque[i, j, t+1] = ajout normal
#             plaque[i, j, t+1] = ajout de convection de côté y

#             else:
#             plaque[i, j, t+1] = dt/(rho*cp) * k * (T[i+1] - 2*T[i] + T[i-1]) / dx**2

#             plaque[i, j, t+1] = ajout de convection de haut et bas de la plaque??

# ajout des températures des thermistances pour faire un graphique plus tard

#      thermistance1[t] = plaque[therm1_loc, t]
#      thermistance2[t] = plaque[therm2_loc, t]
#      thermistance3[t] = plaque[therm3_loc, t]
            
