import time
import numba
from PyQt5.QtCore import pyqtSignal, QObject
import numpy as np


# Classe pour faire la simulation thermique depuis l'interface graphique
class SimulationThermique(QObject):
    therm_1 = pyqtSignal(object, object, object, object, object)
    plaque = pyqtSignal(object, object)

    def __init__(self):

        super().__init__()
        # Initialiser les paramètres de la simulation
        self.longueur = None
        self.largeur = None
        self.epaisseur = None
        self.T_init = None
        self.t_simulation = None
        self.k = None
        self.rho = None
        self.cp = None
        self.h_conv = None
        self.dx = None
        self.Pin = None

    # ULTRA-OPTIMIZED VERSION - Vectorized operations where possible
    @staticmethod
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

    def init_simulation(self):
        self.alpha = self.k / (self.rho * self.cp)
        dy = self.dx
        self.dt = self.dx ** 2 / (4 * self.alpha)

        nx, ny = int(self.longueur / self.dx), int(self.largeur / dy)
        self.nt = int(self.t_simulation / self.dt)
        self.t_actuel = 0

        self.alpha_dt_dx2 = self.alpha * self.dt / (self.dx ** 2)
        self.alpha_dt_dy2 = self.alpha * self.dt / (dy ** 2)
        self.coeff_conv = (self.h_conv * self.dt) / (self.rho * self.cp * self.dx)
        self.coeff_face_2 = 2 * self.h_conv * self.dt / (self.rho * self.cp * self.epaisseur)

        self.nx, self.ny = nx, ny
        self.T = np.full((nx, ny), self.T_init, dtype=float)

        act_size = 15e-3
        rx = int((act_size / 2) / self.dx)
        ry = int((act_size / 2) / dy)
        cell_volume = self.dx * dy * self.epaisseur
        nb_cells = (2 * rx + 1) * (2 * ry + 1)
        P_cell = self.Pin / nb_cells
        self.P_cell_dt_vol = (P_cell * self.dt) / (self.rho * self.cp * cell_volume)

        self.therm1_locx = int(14.87e-3 / self.dx)
        self.therm1_locy = int((self.largeur / 2) / self.dx)
        self.therm2_locx = int(59.35e-3 / self.dx)
        self.therm2_locy = int((self.largeur / 2) / self.dx)
        self.therm3_locx = int(104.99e-3 / self.dx)
        self.therm3_locy = int((self.largeur / 2) / self.dx)

        self.x0 = self.therm1_locx
        self.y0 = self.therm1_locy
        self.rx, self.ry = rx, ry

        self.temps = []
        self.T1, self.T2, self.T3 = [], [], []

    def step_batch(self, batch_size):
        """Avance la simulation de batch_size itérations. Retourne True si terminé."""

        end = min(self.t_actuel + batch_size, self.nt)

        for t in range(self.t_actuel, end):
            self.T = self.compute_timestep_ultra(
                self.T, self.T_init, self.alpha_dt_dx2, self.alpha_dt_dy2,
                self.coeff_conv, self.coeff_face_2, self.P_cell_dt_vol,
                self.x0, self.rx, self.y0, self.ry, self.nx, self.ny
            )
            self.temps.append(t * self.dt)
            self.T1.append(self.T[self.therm1_locx, self.therm1_locy] - 273)
            self.T2.append(self.T[self.therm2_locx, self.therm2_locy] - 273)
            self.T3.append(self.T[self.therm3_locx, self.therm3_locy] - 273)

        self.t_actuel = end

        # Émettre les signaux pour update les graphiques
        self.therm_1.emit('Thermistance', self.temps, self.T1, self.T2, self.T3)
        self.plaque.emit('T plaque', self.T)

        return self.t_actuel >= self.nt

