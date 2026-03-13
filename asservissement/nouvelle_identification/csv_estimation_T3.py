import serial
import csv
from datetime import datetime
import time
import os
import matplotlib.pyplot as plt
import pandas as pd

# ============ CONFIGURATION ============
PORT = 'COM6'
BAUDRATE = 9600

CHEMIN_ENREGISTREMENT = r'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\asservissement\nouvelle_identification\estimation_de_T3'

NOM_FICHIER = f'temperature_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
FICHIER_COMPLET = os.path.join(CHEMIN_ENREGISTREMENT, NOM_FICHIER)
# =======================================

print(f"Connexion au port {PORT}...")
ser = serial.Serial(PORT, BAUDRATE, timeout=1)
time.sleep(2)

print(f"Enregistrement dans :\n{FICHIER_COMPLET}\n")
print("Appuyez sur Ctrl+C pour arrêter\n")

entete_ecrit = False

with open(FICHIER_COMPLET, 'w', newline='', encoding='utf-8') as fichier:
    writer = csv.writer(fichier)

    try:
        while True:
            if ser.in_waiting > 0:
                ligne = ser.readline().decode('utf-8').strip()

                if ligne:
                    print(ligne)

                    if ligne == "FIN":
                        print("\n✓ Enregistrement terminé!")
                        break

                    if '\t' in ligne:
                        continue

                    # 7 colonnes : temps_s, T1_C, T2_C, T3_mesuree, T3_estimT2, T3_estimT1, T3_moy
                    if ligne.count(',') == 6:
                        parties = ligne.split(',')

                        if len(parties) == 7 and all(p.strip() for p in parties):
                            try:
                                [float(p) for p in parties]
                                writer.writerow(parties)
                                fichier.flush()
                            except ValueError:
                                if not entete_ecrit:
                                    writer.writerow(parties)
                                    fichier.flush()
                                    entete_ecrit = True

    except KeyboardInterrupt:
        print("\n\n⚠ Arrêt manuel")
    finally:
        ser.close()
        print(f"\n✓ Fichier sauvegardé dans :\n{FICHIER_COMPLET}")

# ============ TRACÉ DU GRAPHIQUE ============
print("\nGénération du graphique...")

try:
    data = pd.read_csv(FICHIER_COMPLET, header=None,
                       names=['temps_s', 'T1_C', 'T2_C', 'T3_mesuree', 'T3_estimT2', 'T3_estimT1', 'T3_moy'])
    data = data[pd.to_numeric(data['temps_s'], errors='coerce').notna()].astype(float).reset_index(drop=True)

    if len(data) == 0:
        print("❌ Aucune donnée à tracer!")
    else:
        print(f"✓ {len(data)} lignes chargées")

        fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        fig.suptitle('Températures mesurées et estimations de T3', fontsize=14, fontweight='bold')

        # ── Graphique 1 : T1, T2, T3 mesurées ──
        axes[0].plot(data['temps_s'], data['T1_C'],
                     color='#2196F3', linewidth=1.5, label='T1 mesurée')
        axes[0].plot(data['temps_s'], data['T2_C'],
                     color='#FF9800', linewidth=1.5, label='T2 mesurée')
        axes[0].plot(data['temps_s'], data['T3_mesuree'],
                     color='#F44336', linewidth=1.5, label='T3 mesurée')
        axes[0].set_ylabel('Température (°C)')
        axes[0].set_title('T1, T2, T3 mesurées')
        axes[0].legend(fontsize=10)
        axes[0].grid(True, alpha=0.3)

        # ── Graphique 2 : T3 mesurée vs estimations ──
        axes[1].plot(data['temps_s'], data['T3_mesuree'],
                     color='#F44336', linewidth=1.5, label='T3 mesurée')
        axes[1].plot(data['temps_s'], data['T3_estimT2'],
                     color='#FF9800', linewidth=1.5, linestyle='--', label='T3_estimT2')
        axes[1].plot(data['temps_s'], data['T3_estimT1'],
                     color='#9C27B0', linewidth=1.5, linestyle='-.', label='T3_estimT1')
        axes[1].plot(data['temps_s'], data['T3_moy'],
                     color='#4CAF50', linewidth=1.5, linestyle=':', label='T3_moy')
        axes[1].set_ylabel('Température (°C)')
        axes[1].set_xlabel('Temps (s)')
        axes[1].set_title('T3 mesurée vs estimations')
        axes[1].legend(fontsize=10)
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()

        nom_image = FICHIER_COMPLET.replace('.csv', '_graphiques.png')
        plt.savefig(nom_image, dpi=300, bbox_inches='tight')
        print(f"✓ Graphique sauvegardé : {nom_image}")
        plt.show()

        print("\n✓ Terminé!")

except Exception as e:
    print(f"\n❌ Erreur lors de la génération du graphique : {e}")
    print("Vérifiez le contenu du fichier CSV.")