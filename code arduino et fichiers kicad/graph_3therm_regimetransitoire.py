from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

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

# Stocker les températures finales à 300s
final_temps = {}

for file in csv_files:
    print("Lecture :", file)

    data = pd.read_csv(file)

    # ====== Filtrer pour 0 à 300 secondes ======
    data = data[data['temps_s'] <= 300]

    plt.plot(
        data['temps_s'],
        data['temperature_C'],
        marker='o', markersize=1,
        label=file.stem
    )

    # Stocker la dernière température (à 300s max)
    final_temps[file.stem] = data['temperature_C'].iloc[-1]

# ====== TEXTBOX avec valeurs finales ======
plt.text(
    0.05, 0.95,
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
plt.title("T1 à T3 (0-300s)")
plt.legend()
plt.grid(True)

# ====== Sauvegarde DANS T1-3 ======
output_path = DOSSIER_T13 / "comparaison_T1_T3_transitoire.png"

# Crée le dossier T1-3 s'il n'existe pas
DOSSIER_T13.mkdir(parents=True, exist_ok=True)

plt.savefig(output_path, dpi=300)

print("✓ Graphique sauvegardé :", output_path)
plt.show()
