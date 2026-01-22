import numpy as np
import matplotlib.pyplot as mpl
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation

# longueur (m) = 117.28e-3
# largeur = 61.57e-3
# T_init =
# T_act =
# position_act =
# dimensions_act = 
# diffusivity = 
# dt = 0.5*(dx)**2/diffusivity

def plaque(longueur, largeur, T_init, T_act, position_act, dimensions_act, dx=0.1e-3):
    '''
        Fonction de géométrie pour une plaque 2D qui retourne un array avec les conditions limites
        Arguments: longueur et largeur de la plaque, température initiale (de la pièce et donc de la plaque), 
        température, dimensions et position de l'actuateur, résolution
        Retourne un array de la température dans la plaque
    '''
    dy = dx

    nx, ny = int(longueur / dx), int(largeur / dy)

    plaque = np.full((ny, nx), T_init)

    return plaque