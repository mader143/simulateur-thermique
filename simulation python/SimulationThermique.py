import time

import numba
from PyQt5.QtCore import pyqtSignal, QObject
from matplotlib.animation import FuncAnimation, FFMpegWriter
import matplotlib.pyplot as plt
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

    def simuler_diffusion(self):
        alpha = self.k / (self.rho * self.cp)
        dy = self.dx
        dt = self.dx ** 2 / (4 * alpha)

        nx, ny = int(self.longueur / self.dx), int(self.largeur / dy)
        nt = int(self.t_simulation / dt)

        # Pre-calculate constants
        alpha_dt_dx2 = alpha * dt / (self.dx ** 2)
        alpha_dt_dy2 = alpha * dt / (dy ** 2)
        coeff_conv = (self.h_conv * dt) / (self.rho * self.cp * self.dx)
        coeff_face_2 = 2 * self.h_conv * dt / (self.rho * self.cp * self.epaisseur)

        T = np.full((nx, ny), self.T_init, dtype=float)

        act_size = 15e-3
        rx = int((act_size / 2) / self.dx)
        ry = int((act_size / 2) / dy)

        cell_volume = self.dx * dy * self.epaisseur
        nb_cells = (2 * rx + 1) * (2 * ry + 1)
        P_cell = self.Pin / nb_cells
        P_cell_dt_vol = (P_cell * dt) / (self.rho * self.cp * cell_volume)

        therm1_locx, therm1_locy = int(14.87e-3 / self.dx), int((self.largeur / 2) / self.dx)
        therm2_locx, therm2_locy = int(59.35e-3 / self.dx), int((self.largeur / 2) / self.dx)
        therm3_locx, therm3_locy = int(104.99e-3 / self.dx), int((self.largeur / 2) / self.dx)

        x0, y0 = therm1_locx, therm1_locy

        temps = []
        T1, T2, T3 = [], [], []

        # ============ REAL-TIME PLOTTING SETUP ============
        PLOT_2D_INTERVAL = 10000  # Update 2D plot every N iterations
        PLOT_3D_INTERVAL = 10000  # Update 3D plot every N iterations (heavier)

        #plt.ion()  # Enable interactive mode




        # Figure 2: 3D surface
        fig3D = plt.figure(figsize=(7, 5))
        ax3D = fig3D.add_subplot(111, projection='3d')

        x = np.linspace(0, self.longueur, nx)
        y = np.linspace(0, self.largeur, ny)
        X, Y = np.meshgrid(x, y, indexing='ij')

        surf = ax3D.plot_surface(
            X, Y, T - 273,
            cmap='inferno',
            rstride=1, cstride=1,
            linewidth=0,
            antialiased=False
        )

        ax3D.set_xlabel("x [m]")
        ax3D.set_ylabel("y [m]")
        ax3D.set_zlabel("Température [°C]")
        ax3D.set_zlim(self.T_init - 273 - 1, self.T_init - 273 + 15)

        #plt.show(block=False)

        print(f"Grid size: {nx} x {ny} = {nx * ny} cells")
        print(f"Time steps: {nt}")
        print(f"Simulation time: {self.t_simulation} seconds")
        print(f"dt: {dt:.6f} seconds")
        print("\nStarting REAL-TIME simulation...")
        print("(First iteration will be slow due to JIT compilation)\n")

        start_time = time.time()
        last_2d_update = start_time
        last_3d_update = start_time

        for t in range(nt):
            T = self.compute_timestep_ultra(T, self.T_init, alpha_dt_dx2, alpha_dt_dy2,
                                       coeff_conv, coeff_face_2, P_cell_dt_vol,
                                       x0, rx, y0, ry, nx, ny)

            temps.append(t * dt)
            T1.append(T[therm1_locx, therm1_locy] - 273)
            T2.append(T[therm2_locx, therm2_locy] - 273)
            T3.append(T[therm3_locx, therm3_locy] - 273)

            current_time = time.time()

            # Update 2D plot
            if t % PLOT_2D_INTERVAL == 0 and (current_time - last_2d_update) > 0.05:

                self.therm_1.emit('Thermistance',temps, T1, T2, T3)
                last_2d_update = current_time

            # Update 3D plot
            if t % PLOT_3D_INTERVAL == 0 and (current_time - last_3d_update) > 0.1:
                self.plaque.emit('T plaque', T)
                surf.remove()
                surf = ax3D.plot_surface(
                    X, Y, T - 273,
                    cmap='inferno',
                    rstride=1, cstride=1,
                    linewidth=0,
                    antialiased=False
                )
                ax3D.set_title(f"Température de la plaque – t = {t * dt:.2f} s")
                fig3D.canvas.draw()
                fig3D.canvas.flush_events()
                last_3d_update = current_time

            # Progress indicator
            if t % 500 == 0:
                elapsed = time.time() - start_time
                progress = 100 * t / nt
                if t > 0:
                    est_total = elapsed / (t / nt)
                    est_remaining = est_total - elapsed
                    speed = (t * dt) / elapsed if elapsed > 0 else 0
                    print(
                        f"Progress: {progress:.1f}% | Elapsed: {elapsed:.1f}s | ETA: {est_remaining:.1f}s | Speed: {speed:.1f}x",
                        end='\r')
                else:
                    print(f"Progress: {progress:.1f}% | Compiling...", end='\r')

        elapsed = time.time() - start_time
        print(f"\n\nSimulation complete!")
        print(f"Total time: {elapsed:.1f}s")
        print(f"Average time per step: {elapsed / nt * 1000:.2f}ms")
        print(f"Speed factor: {self.t_simulation / elapsed:.1f}x real-time")

        # Final update to make sure we show the end state
        surf.remove()
        surf = ax3D.plot_surface(
            X, Y, T - 273,
            cmap='inferno',
            rstride=1, cstride=1,
            linewidth=0,
            antialiased=False
        )
        ax3D.set_title(f"Température finale – t = {self.t_simulation:.2f} s")
        fig3D.canvas.draw()

        #plt.ioff()
        #plt.show()