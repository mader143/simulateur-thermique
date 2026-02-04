import time
from matplotlib.animation import FuncAnimation, FFMpegWriter
import matplotlib.pyplot as plt
import numpy as np


# Classe pour faire la simulation thermique depuis l'interface graphique


class SimulationThermique:

    def __init__(self):

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


    def simuler_diffusion(self):
        # Simuler la diffusion de la chaleur (à séparer dans plusieurs méthodes?)

        alpha = self.k / (self.rho * self.cp)
        dy = self.dx
        dt = self.dx ** 2 / (4 * alpha)

        nx, ny = int(self.longueur / self.dx), int(self.largeur / dy)
        nt = int(self.t_simulation / dt)
        # résolution

        coeff_conv = (self.h_conv * dt) / (self.rho * self.cp * self.dx)
        coeff_face = 2 * self.h_conv * dt / (self.rho * self.cp * self.epaisseur)

        T = np.full((nx, ny), self.T_init, dtype=float)

        # puissance

        act_size = 20e-3  # 5 mm
        rx = int((act_size / 2) / self.dx)
        ry = int((act_size / 2) / dy)

        epaisseur = 1.61e-3
        cell_volume = self.dx * dy * epaisseur

        nb_cells = (2 * rx + 1) * (2 * ry + 1)
        P_cell = self.Pin / nb_cells

        save_interval = 10
        frames = []

        thermistance1 = np.zeros(nt)
        therm1_locx, therm1_locy = int(14.87e-3 / self.dx), int((self.largeur / 2) / self.dx)  # j'ai mis position en y a mi chemin
        thermistance2 = np.zeros(nt)
        therm2_locx, therm2_locy = int(59.35e-3 / self.dx), int((self.largeur / 2) / self.dx)
        thermistance3 = np.zeros(nt)
        therm3_locx, therm3_locy = int(104.99e-3 / self.dx), int((self.largeur / 2) / self.dx)

        x0, y0 = therm1_locx, therm1_locy

        Temps = np.arange(nt) * dt

        # make it go faster
        target_frames = nt / save_interval  # nombre total de frames

        # fiure
        fig, axs = plt.subplots(1, 3, figsize=(14, 4))

        line1, = axs[0].plot([], [])
        axs[0].set_title("Température à la thermistance 1")
        axs[0].set_xlabel("Temps [s]")
        axs[0].set_ylabel("Température [°C]")
        axs[0].grid(True)

        line2, = axs[1].plot([], [])
        axs[1].set_title("Température à la thermistance 2")
        axs[1].set_xlabel("Temps [s]")
        axs[1].set_ylabel("Température [°C]")
        axs[1].grid(True)

        line3, = axs[2].plot([], [])
        axs[2].set_title("Température à la thermistance 3")
        axs[2].set_xlabel("Temps [s]")
        axs[2].set_ylabel("Température [°C]")
        axs[2].grid(True)

        fig.tight_layout()

        # timer
        start_time = time.time()

        for t in range(nt):

            T_new = T.copy()

            # equation de diffusion sur les points internes... cest quand meme compliqué
            laplacien = (
                    (T_new[2:, 1:-1] - 2 * T_new[1:-1, 1:-1] + T_new[:-2, 1:-1]) / self.dx ** 2 +
                    (T_new[1:-1, 2:] - 2 * T_new[1:-1, 1:-1] + T_new[1:-1, :-2]) / dy ** 2
            )

            T[1:-1, 1:-1] += dt * alpha * laplacien

            # convection sur les bords
            T[0, :] += coeff_conv * (self.T_init - T[0, :])
            T[-1, :] += coeff_conv * (self.T_init - T[-1, :])
            T[:, 0] += coeff_conv * (self.T_init - T[:, 0])
            T[:, -1] += coeff_conv * (self.T_init - T[:, -1])

            # convection face supérieure
            T += coeff_face * (self.T_init - T)

            # puissance
            # T[Pin_loc_y, Pin_loc_x] += (Pin * dt) / (rho * cp *dx**2*1.61e-3)
            T[x0 - rx:x0 + rx + 1, y0 - ry:y0 + ry + 1] += (P_cell * dt) / (self.rho * self.cp * cell_volume)

            if t % 100 == 0: print(f"Progression : {100 * t / nt:.1f}%")

            # on prends les frames de T pour le graphique de diffusion thermique
            if t % save_interval == 0:
                frames.append(T.copy())

            # update les graphiques des thermistances
            thermistance1[t] = T[therm1_locx, therm1_locy]
            thermistance2[t] = T[therm2_locx, therm2_locy]
            thermistance3[t] = T[therm3_locx, therm3_locy]

            if t % save_interval == 0 or t == nt - 1:
                # mise a jour graphique
                line1.set_data(Temps[:t + 1], thermistance1[:t + 1] - 273)
                line2.set_data(Temps[:t + 1], thermistance2[:t + 1] - 273)
                line3.set_data(Temps[:t + 1], thermistance3[:t + 1] - 273)

                # mise a jour axes
                axs[0].set_xlim(0, max(Temps[t], 1e-8))
                axs[0].set_ylim(min(thermistance1[:t + 1] - 273) - 1, max(thermistance1[:t + 1] - 273) + 1)
                axs[1].set_xlim(0, max(Temps[t], 1e-8))
                axs[1].set_ylim(min(thermistance2[:t + 1] - 273) - 1, max(thermistance2[:t + 1] - 273) + 1)
                axs[2].set_xlim(0, max(Temps[t], 1e-8))
                axs[2].set_ylim(min(thermistance3[:t + 1] - 273) - 1, max(thermistance3[:t + 1] - 273) + 1)

        # graphique diffusion thermique
        fig, ax = plt.subplots()
        im = ax.imshow(frames[0].T, cmap='hot', origin='lower',
                       extent=[0, self.longueur, 0, self.largeur], vmin=self.T_init, vmax=300)
        plt.colorbar(im, label="Température (K)")
        ax.set_title("Diffusion thermique")

        def update(i):
            im.set_array(frames[i].T)
            return [im]

        ani = FuncAnimation(fig, update, frames=len(frames), interval=30, blit=True)
        ani.save("diffusion.mp4", writer=FFMpegWriter(fps=30))
        print("\nVidéo enregistrée : diffusion.mp4")