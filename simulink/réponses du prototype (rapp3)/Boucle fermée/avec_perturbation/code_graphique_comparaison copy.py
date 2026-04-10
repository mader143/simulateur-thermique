import os
import pandas as pd
import matplotlib.pyplot as plt

base_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(base_dir, "Boucle_fermee_avec_perturb.xlsx")

# 🔹 Récupère tous les noms d’onglets
xls = pd.ExcelFile(excel_path)
sheet_names = xls.sheet_names

for sheet_name in sheet_names:
    print(f"Traitement : {sheet_name}")

    csv_path = os.path.join(base_dir, f"{sheet_name}.csv")

    # Vérifie si le CSV existe
    if not os.path.exists(csv_path):
        print(f"CSV manquant pour {sheet_name}, skip")
        continue

    # --- Lecture données ---
    df_excel = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    df_excel.columns = ["Temps", "Thermistance 1", "Thermistance 2", "Thermistance 3"]

    df_csv = pd.read_csv(csv_path)

    # --- Filtre temps ≤ 600 s ---
    df_excel = df_excel[df_excel["Temps"] <= 600]
    df_csv = df_csv[df_csv["Temps (s)"] <= 600]

    # --- Plot ---
    plt.figure()

    # Simulateur
    plt.plot(df_excel["Temps"], df_excel["Thermistance 1"], '--', label="Simulateur - T1", color='red', alpha=0.7)
    plt.plot(df_excel["Temps"], df_excel["Thermistance 2"], '--', label="Simulateur - T2", color='blue', alpha=0.7)
    plt.plot(df_excel["Temps"], df_excel["Thermistance 3"], '--', label="Simulateur - T3", color='green', alpha=0.7)

    # Prototype
    plt.plot(df_csv["Temps (s)"], df_csv["Thermistance 1 - T1 (°C)"], label="Prototype - T1", color='red')
    plt.plot(df_csv["Temps (s)"], df_csv["Thermistance 2 - T2 (°C)"], label="Prototype - T2", color='blue')
    plt.plot(df_csv["Temps (s)"], df_csv["Thermistance 3 - T3 (°C)"], label="Prototype - T3", color='green')

    plt.xlabel("Temps (s)")
    plt.ylabel("Température (°C)")
    plt.title(sheet_name)
    plt.legend()
    plt.grid()

    # --- Sauvegarde ---
    fig_path = os.path.join(base_dir, f"{sheet_name}_bfp.png")
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')

    plt.close()  # évite d’empiler les figures

print("Tous les graphiques ont été générés.")