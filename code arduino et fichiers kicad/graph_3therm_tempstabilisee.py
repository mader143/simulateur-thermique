from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ====== Dossier du script ======
SCRIPT_DIR = Path(__file__).resolve().parent

# ====== Dossier ident_therm ======
DOSSIER_IDENT = SCRIPT_DIR / "ident_therm"

# ====== Dossier T1-3 ======
DOSSIER_T13 = DOSSIER_IDENT / "T1-3"

print("Dossier CSV (recherche récursive) :", DOSSIER_IDENT)
print("Dossier de sauvegarde du graphique :", DOSSIER_T13)

# ====== Recherche récursive des fichiers CSV ======
csv_files = list(DOSSIER_IDENT.rglob("10_30_t[1-3].csv"))

if not csv_files:
    raise FileNotFoundError("Aucun fichier 10_30_t1 à t3 trouvé dans ident_therm ou ses sous-dossiers.")

plt.figure(figsize=(10, 6))

final_means = {}  # moyenne des 60 dernières secondes

for file in csv_files:
    print("Lecture :", file)
    data = pd.read_csv(file)

    data = data.sort_values("temps_s")
    temps = data["temps_s"].values
    temp = data["temperature_C"].values

    # seuil de temps pour les 60 dernières secondes
    t_final = temps.max()
    mask = temps >= (t_final - 120)

    final_mean = temp[mask].mean()
    final_means[file.stem] = final_mean

    # plot
    plt.plot(
        temps,
        temp,
        marker='o', markersize=1,
        label=file.stem
    )

# ====== TEXTBOX ======
plt.text(
    0.05, 0.95,
    f"T1 final mean (120s) = {final_means.get('10_30_t1', np.nan):.2f} °C\n"
    f"T2 final mean (120s) = {final_means.get('10_30_t2', np.nan):.2f} °C\n"
    f"T3 final mean (120s) = {final_means.get('10_30_t3', np.nan):.2f} °C\n",
    transform=plt.gca().transAxes,
    fontsize=12,
    verticalalignment='top',
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
)

plt.xlabel("Temps (s)")
plt.ylabel("Température (°C)")
plt.title("Comparaison T1 à T3")
plt.legend()
plt.grid(True)

# ====== Sauvegarde DANS T1-3 ======
output_path = DOSSIER_T13 / "comparaison_T1_T3_stab.png"
DOSSIER_T13.mkdir(parents=True, exist_ok=True)
plt.savefig(output_path, dpi=300)

print("✓ Graphique sauvegardé :", output_path)
plt.show()

