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
CHEMIN_ENREGISTREMENT = r'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\asservissement\test_asservissement'
NOM_FICHIER = f'temperature_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
FICHIER_COMPLET = os.path.join(CHEMIN_ENREGISTREMENT, NOM_FICHIER)
SETPOINT = 28.0
# =======================================

print(f"Connexion au port {PORT}...")
ser = serial.Serial(PORT, BAUDRATE, timeout=1)
time.sleep(2)

print(f"Enregistrement dans :\n{FICHIER_COMPLET}\n")
entete_ecrit = False

with open(FICHIER_COMPLET, 'w', newline='', encoding='utf-8') as fichier:
    writer = csv.writer(fichier)

    try:
        while True:
            if ser.in_waiting > 0:
                ligne = ser.readline().decode('utf-8').strip()
                if not ligne:
                    continue

                print(ligne)

                if ligne == "FIN":
                    print("\n✓ Enregistrement terminé!")
                    break

                # Format Arduino : temps_s,temperature_C,erreur,commande_u
                if ligne.count(',') == 3:
                    parties = ligne.split(',')
                    try:
                        float(parties[0])  # données numériques
                        writer.writerow(parties)
                        fichier.flush()
                    except ValueError:
                        # en-tête
                        if not entete_ecrit:
                            writer.writerow(parties)
                            fichier.flush()
                            entete_ecrit = True

    except KeyboardInterrupt:
        print("\n⚠ Arrêt manuel")
    finally:
        ser.close()
        print(f"\n✓ Fichier sauvegardé : {FICHIER_COMPLET}")

# ============ TRACÉ ============
print("\nGénération du graphique...")

try:
    data = pd.read_csv(FICHIER_COMPLET)

    if len(data) == 0:
        print("❌ Aucune donnée à tracer!")
    else:
        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        fig.suptitle('Contrôleur PI Thermique', fontsize=14, fontweight='bold')

        # --- Température + consigne ---
        axes[0].plot(data['temps_s'], data['temperature_C'], 'b-', linewidth=1.5, label='Température mesurée')
        axes[0].axhline(y=SETPOINT, color='r', linestyle='--', linewidth=1.5, label=f'Consigne ({SETPOINT}°C)')
        axes[0].set_ylabel('Température (°C)')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # --- Erreur ---
        axes[1].plot(data['temps_s'], data['erreur'], 'orange', linewidth=1.5)
        axes[1].axhline(y=0, color='k', linestyle='--', linewidth=0.8)
        axes[1].set_ylabel('Erreur (°C)')
        axes[1].grid(True, alpha=0.3)

        # --- Commande u ---
        axes[2].plot(data['temps_s'], data['commande_u'], 'g-', linewidth=1.5)
        axes[2].axhline(y=255,  color='r', linestyle=':', linewidth=0.8, label='Sat. +255')
        axes[2].axhline(y=-255, color='b', linestyle=':', linewidth=0.8, label='Sat. -255')
        axes[2].set_ylabel('Commande u (PWM)')
        axes[2].set_xlabel('Temps (s)')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        nom_image = FICHIER_COMPLET.replace('.csv', '.png')
        plt.savefig(nom_image, dpi=300, bbox_inches='tight')
        print(f"✓ Graphique sauvegardé : {nom_image}")
        plt.show()

except Exception as e:
    print(f"\n❌ Erreur : {e}")