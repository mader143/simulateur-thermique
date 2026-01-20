import numpy as np
import matplotlib.pyplot as mpl


# fonction de géométrie pour une plaque 2D qui retourne un array avec les conditions limites

def plaque(longueur, largeur, T_init, grid_res=0.1e-3):

    nx = int(longueur / grid_res)
    ny = int(largeur / grid_res) 

    plaque = np.full((ny, nx), T_init)