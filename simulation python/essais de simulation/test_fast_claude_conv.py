import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import json
import os
import numba

# Numba-optimized computation kernel - CORRECTED VERSION
@numba.jit(nopython=True)
def compute_timestep(T, T_init, alpha_dt_dx2, alpha_dt_dy2, 
                     coeff_conv, coeff_face, P_cell_dt_vol,
                     x0, rx, y0, ry, nx, ny, act_x, act_y, 
                    perturb_locx, perturb_locy, perturb_W_dt_vol, px, py):
    """
    Optimized computation of one timestep using Numba JIT compilation.
    CORRECTED: Proper boundary condition handling without double-counting.
    """
    T_new = T.copy()
    
    # ============================================
    # STEP 1: Apply diffusion to ALL interior points
    # ============================================
    for i in range(1, nx-1):
        for j in range(1, ny-1):
            laplacian_x = (T[i+1, j] - 2*T[i, j] + T[i-1, j]) * alpha_dt_dx2
            laplacian_y = (T[i, j+1] - 2*T[i, j] + T[i, j-1]) * alpha_dt_dy2
            T_new[i, j] += laplacian_x + laplacian_y
    
    # ============================================
    # STEP 2: Boundary diffusion (edges and corners)
    # ============================================
    # x=0 edge (excluding corners)
    for j in range(1, ny-1):
        diff = alpha_dt_dx2 * (T[1, j] - T[0, j]) + \
               alpha_dt_dy2 * (T[0, j+1] - 2*T[0, j] + T[0, j-1])
        T_new[0, j] += diff
    
    # x=nx-1 edge (excluding corners)
    for j in range(1, ny-1):
        diff = alpha_dt_dx2 * (T[nx-2, j] - T[nx-1, j]) + \
               alpha_dt_dy2 * (T[nx-1, j+1] - 2*T[nx-1, j] + T[nx-1, j-1])
        T_new[nx-1, j] += diff
    
    # y=0 edge (excluding corners)
    for i in range(1, nx-1):
        diff = alpha_dt_dx2 * (T[i+1, 0] - 2*T[i, 0] + T[i-1, 0]) + \
               alpha_dt_dy2 * (T[i, 1] - T[i, 0])
        T_new[i, 0] += diff
    
    # y=ny-1 edge (excluding corners)
    for i in range(1, nx-1):
        diff = alpha_dt_dx2 * (T[i+1, ny-1] - 2*T[i, ny-1] + T[i-1, ny-1]) + \
               alpha_dt_dy2 * (T[i, ny-2] - T[i, ny-1])
        T_new[i, ny-1] += diff
    
    # Corners
    T_new[0, 0] += alpha_dt_dx2 * (T[1, 0] - T[0, 0]) + \
                   alpha_dt_dy2 * (T[0, 1] - T[0, 0])
    T_new[0, ny-1] += alpha_dt_dx2 * (T[1, ny-1] - T[0, ny-1]) + \
                      alpha_dt_dy2 * (T[0, ny-2] - T[0, ny-1])
    T_new[nx-1, 0] += alpha_dt_dx2 * (T[nx-2, 0] - T[nx-1, 0]) + \
                      alpha_dt_dy2 * (T[nx-1, 1] - T[nx-1, 0])
    T_new[nx-1, ny-1] += alpha_dt_dx2 * (T[nx-2, ny-1] - T[nx-1, ny-1]) + \
                         alpha_dt_dy2 * (T[nx-1, ny-2] - T[nx-1, ny-1])
    
    # ============================================
    # STEP 3: Apply convection to ALL cells
    # ============================================
    # Face convection (top and bottom surfaces) - applies to EVERY cell
    for i in range(nx):
        for j in range(ny):
            T_new[i, j] += 2 * coeff_face * (T_init - T[i, j])
    
    # Lateral edge convection - ONLY on the actual edges
    # x=0 edge
    for j in range(ny):
        T_new[0, j] += coeff_conv * (T_init - T[0, j])
    
    # x=nx-1 edge
    for j in range(ny):
        T_new[nx-1, j] += coeff_conv * (T_init - T[nx-1, j])
    
    # y=0 edge
    for i in range(nx):
        T_new[i, 0] += coeff_conv * (T_init - T[i, 0])
    
    # y=ny-1 edge
    for i in range(nx):
        T_new[i, ny-1] += coeff_conv * (T_init - T[i, ny-1])
    
    # ============================================
    # STEP 4: Add heat source
    # ============================================
    for i in range(max(0, act_x-rx), min(nx, act_x+rx+1)):
        for j in range(max(0, act_y-ry), min(ny, act_y+ry+1)):
            T_new[i, j] += P_cell_dt_vol

    # ============================================
    # STEP 5: Ajout perturbation
    # ============================================
    for i in range(max(0, perturb_locx-px), min(nx, perturb_locx+px+1)):
        for j in range(max(0, perturb_locy-py), min(ny, perturb_locy+py+1)):
            T_new[i, j] += perturb_W_dt_vol
    

    return T_new


# Load parameters
base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, "params_sim.json")

with open(json_path, "r") as f:
    params = json.load(f)

# Extract parameters
longueur = params["longueur"]
largeur = params["largeur"]
epaisseur = params["epaisseur"]
T_init = params["T_init"] + 273.15
t_simulation = params["t_simulation"]
k = params["k"]
rho = params["rho"]
cp = params["cp"]
h_conv = params["h_conv"]
dx = params["dx"]
Pin = params["Pin"]

# Calculate derived parameters
alpha = k / (rho * cp)
dy = dx
dt = dx**2 / (4 * alpha)

nx, ny = int(longueur / dx), int(largeur / dy)
nt = int(t_simulation / dt)

# Pre-calculate constants (OPTIMIZATION)
alpha_dt_dx2 = alpha * dt / (dx**2)
alpha_dt_dy2 = alpha * dt / (dy**2)
coeff_conv = (h_conv * dt) / (rho * cp * dx)
coeff_face = h_conv * dt / (rho * cp * epaisseur)

# Initialize temperature field
T = np.full((nx, ny), T_init, dtype=float)

# Thermistor locations
therm1_locx, therm1_locy = int(14.87e-3/dx), int((largeur/2)/dx)
therm2_locx, therm2_locy = int(59.35e-3/dx), int((largeur/2)/dx)
therm3_locx, therm3_locy = int(104.99e-3/dx), int((largeur/2)/dx)

x0, y0 = therm1_locx, therm1_locy

# Heat source setup
act_size = 20e-3
rx = int((act_size/2) / dx)
ry = int((act_size/2) / dy)
act_pos = (0.06, 0.03)
act_x = int(act_pos[0] / dx)
act_y = int(act_pos[1] / dy)

cell_volume = dx * dy * epaisseur
nb_cells = (2*rx + 1) * (2*ry + 1)
P_cell = Pin / nb_cells
P_cell_dt_vol = (P_cell * dt) / (rho * cp * cell_volume)

# Perturbation
perturb_size = 5e-3
perturb_W = 0.01
perturb_x = 20e-3
perturb_y = 20e-3
perturb_locx = int(perturb_x/dx)
perturb_locy = int(perturb_y/dy)
px = int((perturb_size/2) / dx)
py = int((perturb_size/2) / dy)
p_cells = (2*px + 1) * (2*py + 1)
perturb_cell = perturb_W / p_cells
perturb_W_dt_vol = (perturb_cell * dt)/(rho * cp * cell_volume)

# Storage for thermistor data
temps = []
T1, T2, T3 = [], [], []

print(f"Grid size: {nx} x {ny} = {nx*ny} cells")
print(f"Time steps: {nt}")
print(f"Simulation time: {t_simulation} seconds")
print(f"dt: {dt:.6f} seconds")
print(f"Heat gain per step: +{P_cell_dt_vol:.6f} °C")
print("\nStarting simulation with Numba JIT optimization...")
print("(First iteration will be slow due to JIT compilation)\n")

# Timer
start_time = time.time()

# Main simulation loop - NO PLOTTING
for t in range(nt):
    t_sim = t * dt
    
    # OPTIMIZED: Single function call (Numba-compiled)
    T = compute_timestep(T, T_init, alpha_dt_dx2, alpha_dt_dy2,
                         coeff_conv, coeff_face, P_cell_dt_vol,
                         x0, rx, y0, ry, nx, ny, act_x, act_y,
                         perturb_locx, perturb_locy, perturb_W_dt_vol, px, py)
    
    # Diagnostics (every 5000 steps to not slow down)
    if t % 5000 == 0 and t > 0:
        perte_par_pas = coeff_face * (T[x0, y0] - T_init)
        balance = P_cell_dt_vol - perte_par_pas
        print(f"Step {t}/{nt} | T_max: {T[x0, y0]-273.15:.2f}°C | Net: {balance:.6f} °C/step")
    
    # Store thermistor temperatures
    temps.append(t * dt)
    T1.append(T[therm1_locx, therm1_locy] - 273)
    T2.append(T[therm2_locx, therm2_locy] - 273)
    T3.append(T[therm3_locx, therm3_locy] - 273)
    
    # Progress indicator (every 500 steps)
    if t % 500 == 0:
        elapsed = time.time() - start_time
        progress = 100 * t / nt
        if t > 0:  # Skip first iteration (JIT compilation)
            est_total = elapsed / (t / nt)
            est_remaining = est_total - elapsed
            print(f"Progress: {progress:.1f}% | Elapsed: {elapsed:.1f}s | Est. remaining: {est_remaining:.1f}s", end='\r')
        else:
            print(f"Progress: {progress:.1f}% | Compiling with Numba...", end='\r')

# Final timing
elapsed = time.time() - start_time
print(f"\n\nSimulation complete!")
print(f"Total time: {elapsed:.1f}s")
print(f"Average time per step: {elapsed/nt*1000:.2f}ms")

print("Plots generated. Close the plot windows to exit.\n")

# Figure 1: Thermistors (original style)
figT, axT = plt.subplots(figsize=(6, 4))
line1, = axT.plot(temps, T1, label="Thermistance 1")
line2, = axT.plot(temps, T2, label="Thermistance 2")
line3, = axT.plot(temps, T3, label="Thermistance 3")
axT.set_xlabel("Temps [s]")
axT.set_ylabel("Température [°C]")
axT.set_title("Température des thermistances")
axT.grid(True)
axT.legend()

# Figure 2: 3D surface (original style)
fig3D = plt.figure(figsize=(7, 5))
ax3D = fig3D.add_subplot(111, projection='3d')

x = np.linspace(0, longueur, nx)
y = np.linspace(0, largeur, ny)
X, Y = np.meshgrid(x, y, indexing='ij')

surf = ax3D.plot_surface(
    X, Y, T - 273,
    cmap='inferno',
    rstride=1, cstride=1,
    linewidth=0,
    alpha=0.9
)

# Add thermistor markers - placed ABOVE the surface with vertical lines
therm_temps = [T[therm1_locx, therm1_locy]-273, 
               T[therm2_locx, therm2_locy]-273, 
               T[therm3_locx, therm3_locy]-273]
therm_x = [therm1_locx*dx, therm2_locx*dx, therm3_locx*dx]
therm_y = [therm1_locy*dy, therm2_locy*dy, therm3_locy*dy]

# Draw vertical lines from surface to marker
for i in range(3):
    ax3D.plot([therm_x[i], therm_x[i]], 
              [therm_y[i], therm_y[i]], 
              [T_init-273, therm_temps[i]], 
              'k--', linewidth=2, alpha=0.7)

# Place markers well above the surface
ax3D.scatter(therm_x, therm_y, therm_temps,
             color='yellow', s=200, marker='o', edgecolors='black', linewidths=3,
             label='Thermistances', zorder=1000)

ax3D.set_xlabel("x [m]")
ax3D.set_ylabel("y [m]")
ax3D.set_zlabel("Température [°C]")
ax3D.set_title(f"Température de la plaque – t = {t_simulation:.2f} s")
ax3D.legend()

plt.show()