import numpy as np
import matplotlib.pyplot as plt
import imageio.v2 as imageio
import time

#paramètres simulation
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
dy = dz = thickness
dt = dx**2 / (8*alpha)
Nt = int(round(TempsTotal/dt))

#Convection
aire_bouts = dy*dz
aire_sides = dx*dz
aire_top = dx*dy
volume = dx*dy*dz

Temps = np.arange(Nt)*dt
Position = np.arange(Nx)*dx

#power actuator
Pin = 0.5
Pin_loc_x = round((Lx/4)/dx)
P = np.zeros(Nx, dtype=float)
P[Pin_loc_x] = Pin

# c.i.
T_piece = 273 + 25
T = np.full(Nx, T_piece, dtype=float)
T_new = np.zeros(Nx, dtype=float)
Therm_loc_x = round((3*Lx/4)/dx)

#variables
thermistance = np.zeros(Nt, dtype=float)
energy_added = np.zeros(Nt, dtype=float)
energy_loss = np.zeros(Nt, dtype=float)

#video
writer = imageio.get_writer(
    'TemperatureDistribution1D_fast.mp4',
    fps=30,
    codec='libx264',
    macro_block_size=1
)

#temps réel - graphique
plt.ion()
fig, axs = plt.subplots(1,3, figsize=(14,4))

# Graphique 1 - température sur la barre
line1, = axs[0].plot(Position, T-273)
axs[0].set_xlabel("Position [m]")
axs[0].set_ylabel("Température [°C]")
axs[0].grid(True)

# Graphique 2 - température à la thermistance
line2, = axs[1].plot([0], [T[Therm_loc_x]-273])
axs[1].set_xlabel("Temps [s]")
axs[1].set_ylabel("Température [°C]")
axs[1].grid(True)

# Graphique 3 - énergie
line3_added, = axs[2].plot([0], [0])
line3_loss, = axs[2].plot([0], [0])
axs[2].set_xlabel("Temps [s]")
axs[2].set_ylabel("Énergie [J]")
axs[2].grid(True)
axs[2].legend(['Energie déposée','Energie dissipée par convection'])

fig.canvas.draw()
fig.canvas.flush_events()

start_time = time.time()
step_plot = max(1, Nt // 200)  



for t in range(Nt):
    T_new[:] = T[:]

    # conduction vectorisée
    T_new[1:-1] += dt/(rho*cp) * k*(T[2:] - 2*T[1:-1] + T[:-2])/dx**2
    T_new[0] += dt/(rho*cp)*(k*(T[1]-T[0])/dx**2 + h_conv*(T_piece - T[0])*aire_bouts/volume)
    T_new[-1] += dt/(rho*cp)*(k*(T[-2]-T[-1])/dx**2 + h_conv*(T_piece - T[-1])*aire_bouts/volume)

    # puissance + convection
    T_new += dt/(rho*cp) * P/volume
    T_new += dt/(rho*cp) * h_conv*(T_piece - T)*2*aire_sides/volume
    T_new += dt/(rho*cp) * h_conv*(T_piece - T)*2*aire_top/volume

    T[:] = T_new[:]
    thermistance[t] = T[Therm_loc_x]

    # bilan d'énergie
    energy_added[t] = np.sum(P)*dt
    energy_loss[t] = (h_conv*np.sum(T - T_piece)*2*aire_sides*dt +
                      h_conv*np.sum(T - T_piece)*2*aire_top*dt +
                      h_conv*(T[0]-T_piece)*aire_bouts*dt +
                      h_conv*(T[-1]-T_piece)*aire_bouts*dt)

    #mise à jour graphique  
    if t % step_plot == 0 or t == Nt-1:
        # graphique 1 : barre
        line1.set_ydata(T-273)
        axs[0].relim()
        axs[0].autoscale_view()

        # graphique 2 : thermistance
        line2.set_data(Temps[:t+1], thermistance[:t+1]-273)
        axs[1].set_xlim(0, max(Temps[t], 1e-6))
        axs[1].set_ylim(np.min(thermistance[:t+1]-273)-1, np.max(thermistance[:t+1]-273)+1)

        # graphique 3 : énergie
        line3_added.set_data(Temps[:t+1], energy_added[:t+1])
        line3_loss.set_data(Temps[:t+1], energy_loss[:t+1])
        axs[2].set_xlim(0, max(Temps[t], 1e-6))
        axs[2].set_ylim(0, max(np.max(energy_added[:t+1]), np.max(energy_loss[:t+1]))*1.1)

        # redraw
        fig.canvas.draw()
        fig.canvas.flush_events()

        # enregistrer la frame
        buf, size = fig.canvas.print_to_buffer()
        width, height = size
        image = np.frombuffer(buf, dtype=np.uint8).reshape((height, width, 4))[:, :, :3]
        writer.append_data(image)

        # timer console
        elapsed = time.time() - start_time
        progress = t/Nt*100
        print(f"Progress: {progress:.1f}% - Elapsed time: {elapsed:.1f}s", end='\r')

#finiii
plt.ioff()
plt.show()  # reste ouverte
writer.close()
print("\nVidéo enregistrée : TemperatureDistribution1D_temps_reel.mp4")
