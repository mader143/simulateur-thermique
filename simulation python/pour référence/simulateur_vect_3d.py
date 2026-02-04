import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend non interactif
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import imageio.v2 as imageio
import time

#marche pas très bien

# Dimensions plaque
Lx, Ly, Lz = 117.28e-3, 61.57e-3, 1.61e-3

dx = dy = dz = 1e-4

nx, ny, nz = int(Lx/dx), int(Ly/dy), int(Lz/dz)

# Propriétés matériau (alu)
k = 205
rho = 2700
cp = 900
alpha = k / (rho * cp)

# Temps
t_sim = 50.0
dt = dx**2 / (6 * alpha)   # CFL 3D
nt = int(t_sim / dt)

# Convection
h = 20
T_init = 21 + 273

# Puissance
Pin = 0.5

T = np.full((nx, ny, nz), T_init, dtype=float)

cell_volume = dx * dy * dz
coeff_conv = h * dt / (rho * cp * dx)

# taille actuateur (5x5x1 mm)
rx = ry = 2
rz = 0

nb_cells = (2*rx+1)*(2*ry+1)*(2*rz+1)
P_cell = Pin / nb_cells

therm1 = np.zeros(nt)
therm2 = np.zeros(nt)
therm3 = np.zeros(nt)

t1 = int(14.87e-3 / dx)
t2 = int(59.35e-3 / dx)
t3 = int(104.99e-3 / dx)
ty = int((Ly/2) / dy)
tz = 0

Temps = np.arange(nt) * dt

writer = imageio.get_writer(
    'Temperature_thermistances.mp4',
    fps=30,
    codec='libx264',
    format='FFMPEG',
    macro_block_size=1
)
save_interval = 10
frames = []
#make it go faster
target_frames = nt/save_interval # nombre total de frames

#fiure
fig, axs = plt.subplots(1, 3, figsize=(14,4))

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


start = time.time()

for t in range(nt):

    Tn = T.copy()

    # diffusion 3D
    lap = (
        (Tn[2:,1:-1,1:-1] - 2*Tn[1:-1,1:-1,1:-1] + Tn[:-2,1:-1,1:-1]) / dx**2 +
        (Tn[1:-1,2:,1:-1] - 2*Tn[1:-1,1:-1,1:-1] + Tn[1:-1,:-2,1:-1]) / dy**2 +
        (Tn[1:-1,1:-1,2:] - 2*Tn[1:-1,1:-1,1:-1] + Tn[1:-1,1:-1,:-2]) / dz**2
    )

    T[1:-1,1:-1,1:-1] += alpha * dt * lap

        # faces x
    T[0,:,:]   += coeff_conv * (T_init - T[0,:,:])
    T[-1,:,:]  += coeff_conv * (T_init - T[-1,:,:])

    # faces y
    T[:,0,:]   += coeff_conv * (T_init - T[:,0,:])
    T[:,-1,:]  += coeff_conv * (T_init - T[:,-1,:])

    # faces z
    T[:,:,0]   += coeff_conv * (T_init - T[:,:,0])
    T[:,:,-1]  += coeff_conv * (T_init - T[:,:,-1])

    T[ t1-rx : t1+rx+1, ty-ry : ty+ry+1, tz-rz : tz+rz+1] += (P_cell * dt) / (rho * cp * cell_volume)

    if t % save_interval == 0:
            frames.append(T.copy()[:, :, -1])

    # Enregistrement thermistances
    therm1[t] = T[t1, ty, tz]
    therm2[t] = T[t2, ty, tz]
    therm3[t] = T[t3, ty, tz]


    if t % 500 == 0:
        print(f"{100*t/nt:.1f}%  Tmax = {T.max()-273:.2f} °C")


    if t % save_interval == 0 or t == nt-1:
        #mise a jour graphique
        line1.set_data(Temps[:t+1], therm1[:t+1]-273)
        line2.set_data(Temps[:t+1], therm2[:t+1]-273)
        line3.set_data(Temps[:t+1], therm3[:t+1]-273)

        #mise a jour axes
        axs[0].set_xlim(0, max(Temps[t], 1e-8))
        axs[0].set_ylim(min(therm1[:t+1]-273)-1, max(therm1[:t+1]-273)+1)
        axs[1].set_xlim(0, max(Temps[t], 1e-8))
        axs[1].set_ylim(min(therm2[:t+1]-273)-1, max(therm2[:t+1]-273)+1)
        axs[2].set_xlim(0, max(Temps[t], 1e-8))
        axs[2].set_ylim(min(therm3[:t+1]-273)-1, max(therm3[:t+1]-273)+1)

        #to RGB
        buf, size = fig.canvas.print_to_buffer()
        width, height = size
        image = np.frombuffer(buf, dtype=np.uint8).reshape((height, width, 4))[:, :, :3]
        writer.append_data(image)

        #timer
        elapsed = time.time() - start
        progress = t / nt * 100

writer.close()
print("\nVidéo enregistrée : Temperature_thermistances.mp4")

#graphique diffusion thermique
fig, ax = plt.subplots()
im = ax.imshow(frames[0].T, cmap='hot', origin='lower', 
            extent=[0, Lx, 0, Ly], vmin=T_init, vmax=300)
plt.colorbar(im, label="Température (K)")
ax.set_title("Diffusion thermique")

def update(i):
    im.set_array(frames[i].T)
    return [im]

ani = FuncAnimation(fig, update, frames=len(frames), interval=30, blit=True)
ani.save("diffusion.mp4", writer=FFMpegWriter(fps=30))
print("\nVidéo enregistrée : diffusion.mp4")
