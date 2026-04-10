import os
import pandas as pd
import matplotlib.pyplot as plt

base_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(base_dir, "Boucle_fermee_avec_perturb.xlsx")

xl = pd.ExcelFile(excel_path)
sheet_names = xl.sheet_names

for sheet_name in sheet_names:
    df_excel = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    df_excel.columns = ["Temps", "Thermistance 1", "Thermistance 2", "Thermistance 3"]

    df_excel = df_excel[df_excel["Temps"] <= 600]

    plt.figure()

    plt.plot(df_excel["Temps"], df_excel["Thermistance 1"], '--', label="Simulateur - T1", color='red', alpha=0.7)
    plt.plot(df_excel["Temps"], df_excel["Thermistance 2"], '--', label="Simulateur - T2", color='blue', alpha=0.7)
    plt.plot(df_excel["Temps"], df_excel["Thermistance 3"], '--', label="Simulateur - T3", color='green', alpha=0.7)

    plt.title(sheet_name)
    plt.xlabel("Temps (s)")
    plt.ylabel("Température (°C)")
    plt.legend()
    plt.grid()

    fig_path = os.path.join(base_dir, f"{sheet_name}.simulink_bfp.png")
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] {fig_path}")

print("Terminé.") 