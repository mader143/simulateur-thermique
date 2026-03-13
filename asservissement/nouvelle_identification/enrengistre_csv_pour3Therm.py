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

CHEMIN_ENREGISTREMENT = r'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\asservissement\nouvelle_identification\donnees_mars'

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

                    # Format valide : 4 colonnes (temps_s, T1_C, T2_C, T3_C)
                    if ligne.count(',') == 3:
                        parties = ligne.split(',')

                        if len(parties) == 4 and all(p.strip() for p in parties):
                            try:
                                # Données numériques
                                [float(p) for p in parties]
                                writer.writerow(parties)
                                fichier.flush()
                            except ValueError:
                                # En-tête texte
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
    data = pd.read_csv(FICHIER_COMPLET, header=0)
    data = data[pd.to_numeric(data['temps_s'], errors='coerce').notna()].astype(float).reset_index(drop=True)

    if len(data) == 0:
        print("❌ Aucune donnée à tracer!")
    else:
        print(f"✓ {len(data)} lignes chargées")

        capteurs = [
            ('T1_C', '#2196F3', 'T1'),
            ('T2_C', '#FF9800', 'T2'),
            ('T3_C', '#F44336', 'T3'),
        ]

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.suptitle('Températures mesurées', fontsize=14, fontweight='bold')

        ax.plot(data['temps_s'], data['T1_C'], color='#2196F3', linewidth=1.5, label='T1')
        ax.plot(data['temps_s'], data['T2_C'], color='#FF9800', linewidth=1.5, label='T2')
        ax.plot(data['temps_s'], data['T3_C'], color='#F44336', linewidth=1.5, label='T3')

        ax.set_ylabel('Température (°C)')
        ax.set_xlabel('Temps (s)')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        nom_image = FICHIER_COMPLET.replace('.csv', '_T1_T2_T3.png')
        plt.savefig(nom_image, dpi=300, bbox_inches='tight')
        print(f"✓ Graphique sauvegardé : {nom_image}")
        plt.show()

        print("\n✓ Terminé!")

except Exception as e:
    print(f"\n❌ Erreur lors de la génération du graphique : {e}")
    print("Vérifiez le contenu du fichier CSV.")