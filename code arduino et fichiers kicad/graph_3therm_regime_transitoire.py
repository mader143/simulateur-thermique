from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# dossiers
SCRIPT_DIR = Path(__file__).resolve().parent
DOSSIER_IDENT = SCRIPT_DIR / "ident_therm"
DOSSIER_T13 = DOSSIER_IDENT / "T1-3"

# Changer le nom du fichier ici
csv_files = list(DOSSIER_IDENT.rglob("10_30_t[1-3].csv"))

if not csv_files:
    raise FileNotFoundError("Aucun fichier 10_30_t1 à t3 trouvé dans ident_therm ou ses sous-dossiers.")

pwd_name = csv_files[0].name[:5].replace("_", "-")


plt.figure(figsize=(10, 6))

# température à 300s
final_temps = {}

for file in csv_files:
    print("Lecture :", file)

    data = pd.read_csv(file)

    # ====== Filtrer pour 0 à 300 secondes ======
    data = data[data['temps_s'] <= 300]

    label = 'T' + file.stem[-1]
    plt.plot(
        data['temps_s'],
        data['temperature_C'],
        marker='o', markersize=1,
        label=label
    )

    # Stocker la dernière température (à 300s max)
    final_temps[file.stem] = data['temperature_C'].iloc[-1]

# ====== TEXTBOX avec valeurs finales ======
plt.text(
    0.8, 0.18,
    f" T1f = {final_temps.get('10_30_t1', float('nan')):.2f} °C\n"
    f" T2f = {final_temps.get('10_30_t2', float('nan')):.2f} °C\n"
    f" T3f = {final_temps.get('10_30_t3', float('nan')):.2f} °C",
    transform=plt.gca().transAxes,
    fontsize=12,
    verticalalignment='top',
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
)

plt.xlabel("Temps (s)")
plt.ylabel("Température (°C)")
plt.title(f"Température des thermistances 1 à 3 pour 300s pour un PWD de {pwd_name}")
plt.legend(loc="upper left")
plt.grid(True)

# sauvegarde
output_path = DOSSIER_T13 / "T1_T2_T3_transitoire.png"

plt.savefig(output_path, dpi=300)

print("Graphique sauvegardé :", output_path)
plt.show()
