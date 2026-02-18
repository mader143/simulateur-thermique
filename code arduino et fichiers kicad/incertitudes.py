import numpy as np
import matplotlib.pyplot as plt

# ----- Paramètres capteur et montage -----
R0   = 10_000.0       # ohms @ 25°C
T0K  = 298.15         # K
BETA = 3980.0         # K

# Contributions compactées vers u_R2 (voir LaTeX)
# 2% (NTC) + ~1.7% (diff-amp) + 1% (V1/V2) -> RSS ≈ 2.8%
REL_U_R2 = 0.028      # incertitude relative sur la NTC effective

# ----- Plage de température -----
Tmin_C, Tmax_C, N = 15.0, 40.0, 300
T_C = np.linspace(Tmin_C, Tmax_C, N)
T_K = T_C + 273.15

# ----- Résistance NTC théorique -----
R_T = R0 * np.exp(BETA * (1.0/T_K - 1.0/T0K))

# ----- Incertitude sur R2 -----
u_R2 = REL_U_R2 * R_T

# u_T = (T^2 / (BETA * R)) * u_R
u_T_K = (T_K**2 / (BETA * R_T)) * u_R2
u_T_C = u_T_K  # même échelle en K et °C pour un écart-type

idx_15 = np.argmin(np.abs(T_C - 15.0))
idx_25 = np.argmin(np.abs(T_C - 25.0))
idx_40 = np.argmin(np.abs(T_C - 40.0))

print(f"u_T @ 15°C ≈ {u_T_C[idx_15]:.2f} °C")
print(f"u_T @ 25°C ≈ {u_T_C[idx_25]:.2f} °C")
print(f"u_T @ 40°C ≈ {u_T_C[idx_40]:.2f} °C")

# --- Figure ---
plt.figure(figsize=(7, 4.5))

# Courbe principale
plt.plot(T_C, u_T_C, color='tab:blue', lw=2, label=r'$u_T$ (1$\sigma$)')

# Point à 25°C
plt.scatter([25], [u_T_C[idx_25]], color='tab:green', zorder=3, label='25°C')

# Ligne pointillée horizontale au niveau u_T(25°C)
y25 = u_T_C[idx_25]
plt.axhline(y=y25, color='tab:green', ls='--', lw=1.5, alpha=0.8)


yticks = list(plt.yticks()[0])
# Ajoute y25 s'il n'existe pas déjà (tolérance)
if not any(abs(t - y25) < 1e-6 for t in yticks):
    yticks.append(y25)
plt.yticks(sorted(yticks))


plt.xlabel('Température [°C]')
plt.ylabel('Incertitude $u_T$ [°C]')
plt.title('Incertitude de température vs température (NTC 10k, β=3980)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()