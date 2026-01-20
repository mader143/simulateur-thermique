import numpy as np
import matplotlib.pyplot as mpl

# longueur =
# largeur = 
# T_init =
# T_act =
# position_act =
# dimensions_act = 
# diffusivity = 
# dx =
# dy = dx
# dt = 0.5*(dx)**2/diffusivity

def plaque(longueur, largeur, T_init, T_act, position_act, dimensions_act, grid_res=0.1e-3):
    '''
        Fonction de géométrie pour une plaque 2D qui retourne un array avec les conditions limites
        Arguments: longueur et largeur de la plaque, température initiale (de la pièce et donc de la plaque), 
        température, dimensions et position de l'actuateur, résolution
        Retourne un array de la température dans la plaque
    '''

    nx = int(longueur / grid_res)
    ny = int(largeur / grid_res) 

    plaque = np.full((ny, nx), T_init)

    return plaque