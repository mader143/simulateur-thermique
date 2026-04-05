from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# nom du fichier à charger
file_name = "-20pwm_depuis22.csv"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(SCRIPT_DIR, "Boucle ouverte", file_name)


plt.figure(figsize=(10, 6))

final_means = {}

pwd_name = os.path.basename(csv_file)[:5].replace("_", "-")

file = csv_file
print("Lecture :", file)
data = pd.read_csv(file)

data = data.sort_values("Temps (s)")
temps = data["Temps (s)"].values
t1 = data["Thermistance 1 - T1 (°C)"].values
t2 = data["Thermistance 2 - T2 (°C)"].values
t3 = data["Thermistance 3 - T3 (°C)"].values

# température finale (moy des 120 dernières secondes)
t_final = temps.max()
mask = temps >= (t_final - 120)

final_means["T1"] = t1[mask].mean()
final_means["T2"] = t2[mask].mean()
final_means["T3"] = t3[mask].mean()

# plot
plt.plot(
    temps,
    t1,
    marker='o', markersize=1,
    label="T1"
)
plt.plot(
    temps,
    t2,
    marker='o', markersize=1,
    label="T2"
)
plt.plot(
    temps,
    t3,
    marker='o', markersize=1,
    label="T3"
)

# text graph
plt.text(
    0.8, 0.05,
    "T1f = "
    f"{final_means.get('T1', np.nan):.2f} °C\n"
    "T2f = "
    f"{final_means.get('T2', np.nan):.2f} °C\n"
    "T3f = "
    f"{final_means.get('T3', np.nan):.2f} °C",
    fontsize=12, transform=plt.gca().transAxes,
    verticalalignment='bottom',
    horizontalalignment='left',
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8, pad=0.4)
)

plt.xlabel("Temps (s)")
plt.ylabel("Température (°C)")
plt.title(f"Températures des thermistance 1 à 3 pour {temps.max():.0f} secondes pour un PWD de {pwd_name}")
plt.legend(loc="upper left")
plt.grid(True)

# sauvegarde
output_dir = os.path.join(SCRIPT_DIR, "Graphiques")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, file_name.replace(".csv", ".png"))
plt.savefig(output_path, dpi=300)

print("Graphique sauvegardé :", output_path)
plt.show()