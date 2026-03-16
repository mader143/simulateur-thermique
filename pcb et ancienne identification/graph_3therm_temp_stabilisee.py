from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# aller chercher + identifier dossiers
SCRIPT_DIR = Path(__file__).resolve().parent
DOSSIER_IDENT = SCRIPT_DIR / "ident_therm"
DOSSIER_T13 = DOSSIER_IDENT / "T1-3"

# nom du fichier à changer
csv_files = list(DOSSIER_IDENT.rglob("10_30_t[1-3].csv"))

if not csv_files:
    raise FileNotFoundError("Aucun fichier 10_30_t1 à t3 trouvé dans ident_therm ou ses sous-dossiers.")

plt.figure(figsize=(10, 6))

final_means = {}  # moyenne des 120 dernières secondes

pwd_name = csv_files[0].name[:5].replace("_", "-")


for file in csv_files:
    print("Lecture :", file)
    data = pd.read_csv(file)

    data = data.sort_values("temps_s")
    temps = data["temps_s"].values
    temp = data["temperature_C"].values

    # température finale (moy des 120 dernières secondes)
    t_final = temps.max()
    mask = temps >= (t_final - 120)

    final_mean = temp[mask].mean()
    final_means[file.stem] = final_mean


    label = 'T' + file.stem[-1]
    # plot
    plt.plot(
        temps,
        temp,
        marker='o', markersize=1,
        label=label
    )

# text graph
plt.text(
    0.8, 0.05,
    "T1f = "
    f"{final_means.get('10_30_t1', np.nan):.2f} °C\n"
    "T2f = "
    f"{final_means.get('10_30_t2', np.nan):.2f} °C\n"
    "T3f = "
    f"{final_means.get('10_30_t3', np.nan):.2f} °C",
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
output_path = DOSSIER_T13 / "T1_T2_T3_stab.png"
DOSSIER_T13.mkdir(parents=True, exist_ok=True)
plt.savefig(output_path, dpi=300)

print("Graphique sauvegardé :", output_path)
plt.show()

