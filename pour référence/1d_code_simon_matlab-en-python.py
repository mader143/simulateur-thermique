import matplotlib
matplotlib.use("Agg")  # backend non interactif
import matplotlib.pyplot as plt
import numpy as np
import imageio.v2 as imageio
import time

#parametres
TempsTotal = 500
Lx = 120e-3
thickness = 1.5e-3
Nx = 120

k = 205
rho = 2700
cp = 900
alpha = k / (rho * cp)
h_conv = 20

dx = Lx / Nx
dy = thickness
dz = thickness

dt = dx**2 / (8 * alpha)
Nt = int(round(TempsTotal / dt))

aire_bouts = dy * dz
aire_sides = dx * dz
aire_top = dx * dy
volume = dx * dy * dz

Temps = np.arange(Nt) * dt
Position = np.arange(Nx) * dx

#Poower
Pin = 0.5
Pin_loc_x = int(round((Lx / 4) / dx))
P = np.zeros(Nx)
P[Pin_loc_x] = Pin

print(dt/(rho*cp) * P[Pin_loc_x] / volume)

#c.i.
T_piece = 273 + 25
T = T_piece * np.ones(Nx)
Therm_loc_x = int(round((3 * Lx / 4) / dx))


#variables
energy_added = np.zeros(Nt)
energy_loss = np.zeros(Nt)
thermistance = np.zeros(Nt)
T_new = np.zeros_like(T)

#video
writer = imageio.get_writer(
    'TemperatureDistribution1D_fast.mp4',
    fps=30,
    codec='libx264',
    format='FFMPEG',
    macro_block_size=1
)

#make it go faster
target_frames = 200  # nombre total de frames
step = max(1, Nt // target_frames)

#fiure
fig, axs = plt.subplots(1, 3, figsize=(14,4))

line1, = axs[0].plot(Position*1e3, T-273)
axs[0].set_title("Température sur la barre")
axs[0].set_xlabel("Position [mm]")
axs[0].set_ylabel("Température [°C]")
axs[0].grid(True)

line2, = axs[1].plot([], [])
axs[1].set_title("Température à la thermistance")
axs[1].set_xlabel("Temps [s]")
axs[1].set_ylabel("Température [°C]")
axs[1].grid(True)

line3, = axs[2].plot([], [], label="Énergie déposée")
line3_loss, = axs[2].plot([], [], label="Énergie dissipée")
axs[2].legend()
axs[2].set_xlabel("Temps [s]")
axs[2].set_ylabel("Énergie")
axs[2].grid(True)

fig.tight_layout()

#timer
start_time = time.time()


for t in range(Nt):

    #temp
    for i in range(Nx):
        T_new[i] = T[i]

        if i == 0:
            T_new[i] += dt/(rho*cp) * k * (T[i+1] - T[i]) / dx**2
            T_new[i] += dt/(rho*cp) * h_conv * (T_piece - T[i]) * aire_bouts / volume
        elif i == Nx-1:
            T_new[i] += dt/(rho*cp) * k * (-T[i] + T[i-1]) / dx**2
            T_new[i] += dt/(rho*cp) * h_conv * (T_piece - T[i]) * aire_bouts / volume
        else:
            T_new[i] += dt/(rho*cp) * k * (T[i+1] - 2*T[i] + T[i-1]) / dx**2

        T_new[i] += dt/(rho*cp) * P[i] / volume
        T_new[i] += dt/(rho*cp) * h_conv * (T_piece - T[i]) * 2*aire_sides / volume
        T_new[i] += dt/(rho*cp) * h_conv * (T_piece - T[i]) * 2*aire_top / volume

    T = T_new.copy()
    thermistance[t] = T[Therm_loc_x]
    energy_added[t] = np.sum(P) * dt

    energy_loss_sides  = h_conv * np.sum(T - T_piece) * 2*aire_sides * dt
    energy_loss_top    = h_conv * np.sum(T - T_piece) * 2*aire_top * dt
    energy_loss_bout_1 = h_conv * (T[0] - T_piece) * aire_bouts * dt
    energy_loss_bout_2 = h_conv * (T[-1] - T_piece) * aire_bouts * dt
    energy_loss[t] = energy_loss_sides + energy_loss_top + energy_loss_bout_1 + energy_loss_bout_2

    
    
    if t % step == 0 or t == Nt-1:
        #mise a jour graphique
        line1.set_ydata(T-273)
        line2.set_data(Temps[:t+1], thermistance[:t+1]-273)
        line3.set_data(Temps[:t+1], energy_added[:t+1])
        line3_loss.set_data(Temps[:t+1], energy_loss[:t+1])

        #mise a jour axes
        axs[0].set_ylim(min(T-273)-1, max(T-273)+1)
        axs[1].set_xlim(0, max(Temps[t], 1e-8))
        axs[1].set_ylim(min(thermistance[:t+1]-273)-1, max(thermistance[:t+1]-273)+1)
        axs[2].set_xlim(0, max(Temps[t], 1e-8))
        axs[2].set_ylim(min(min(energy_added[:t+1]), min(energy_loss[:t+1]))*0.9,
                        max(max(energy_added[:t+1]), max(energy_loss[:t+1]))*1.1)

        #to RGB
        buf, size = fig.canvas.print_to_buffer()
        width, height = size
        image = np.frombuffer(buf, dtype=np.uint8).reshape((height, width, 4))[:, :, :3]
        writer.append_data(image)

        #timer
        elapsed = time.time() - start_time
        progress = t / Nt * 100
        print(f"Progress: {progress:.1f}% - Elapsed time: {elapsed:.1f}s", end='\r')

writer.close()
print("\nVidéo enregistrée : TemperatureDistribution1D_fast.mp4")

