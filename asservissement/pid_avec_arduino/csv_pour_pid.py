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

CHEMIN_ENREGISTREMENT = r'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\asservissement\pid_avec_arduino\pid_avec_nouvelle_ident'

NOM_FICHIER = f'temperature_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
FICHIER_COMPLET = os.path.join(CHEMIN_ENREGISTREMENT, NOM_FICHIER)
# =======================================

# Crée le dossier si inexistant
os.makedirs(CHEMIN_ENREGISTREMENT, exist_ok=True)

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

                    # 9 colonnes
                    if ligne.count(',') == 8:
                        parties = ligne.split(',')

                        if len(parties) == 9 and all(p.strip() for p in parties):
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
                       names=['temps_s', 'T1_C', 'T2_C', 'T3_C',
                              'T3_estimT2', 'T3_estimT1', 'T3_moy',
                              'erreur', 'commande_u'])
    data = data[pd.to_numeric(data['temps_s'], errors='coerce').notna()].astype(float).reset_index(drop=True)

    if len(data) == 0:
        print("❌ Aucune donnée à tracer!")
    else:
        print(f"✓ {len(data)} lignes chargées")

        fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
        fig.suptitle('Contrôleur PID — T3 estimée', fontsize=14, fontweight='bold')

        # ── Graphique 1 : T3 mesurée, estimée, setpoint ──
        axes[0].plot(data['temps_s'], data['T3_C'],
                     color='#2196F3', linewidth=1.5, label='T3 mesurée')
        axes[0].plot(data['temps_s'], data['T3_moy'],
                     color='#4CAF50', linewidth=1.5, linestyle='--', label='T3_moy (estimée)')
        axes[0].axhline(y=30.0, color='#F44336', linestyle='--',
                        linewidth=1.2, label='Consigne (30°C)')
        axes[0].set_ylabel('Température (°C)')
        axes[0].set_title('T3 mesurée vs T3 estimée moyenne')
        axes[0].legend(fontsize=10)
        axes[0].grid(True, alpha=0.3)

        # ── Graphique 2 : Erreur ──
        axes[1].plot(data['temps_s'], data['erreur'],
                     color='#9C27B0', linewidth=1.5, label='Erreur')
        axes[1].axhline(y=0, color='black', linestyle='--', linewidth=0.8)
        axes[1].fill_between(data['temps_s'], data['erreur'], 0,
                             where=(data['erreur'] > 0), alpha=0.15,
                             color='#F44336', label='Trop froid')
        axes[1].fill_between(data['temps_s'], data['erreur'], 0,
                             where=(data['erreur'] < 0), alpha=0.15,
                             color='#2196F3', label='Trop chaud')
        axes[1].set_ylabel('Erreur (°C)')
        axes[1].set_title('Erreur du PID')
        axes[1].legend(fontsize=10)
        axes[1].grid(True, alpha=0.3)

        # ── Graphique 3 : Commande u ──
        axes[2].plot(data['temps_s'], data['commande_u'],
                     color='#FF9800', linewidth=1.5, label='Commande u')
        axes[2].axhline(y= 255, color='#F44336', linestyle=':', linewidth=0.8, label='Sat. +255')
        axes[2].axhline(y=-255, color='#2196F3', linestyle=':', linewidth=0.8, label='Sat. -255')
        axes[2].axhline(y=0,    color='black',   linestyle='-',  linewidth=0.8)
        axes[2].fill_between(data['temps_s'], data['commande_u'], 0,
                             where=(data['commande_u'] > 0), alpha=0.12, color='#F44336')
        axes[2].fill_between(data['temps_s'], data['commande_u'], 0,
                             where=(data['commande_u'] < 0), alpha=0.12, color='#2196F3')
        axes[2].set_ylabel('Commande u (PWM)')
        axes[2].set_xlabel('Temps (s)')
        axes[2].set_title('Commande PWM appliquée')
        axes[2].set_ylim(-270, 270)
        axes[2].legend(fontsize=10)
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()

        nom_image = FICHIER_COMPLET.replace('.csv', '_PID.png')
        plt.savefig(nom_image, dpi=300, bbox_inches='tight')
        print(f"✓ Graphique sauvegardé : {nom_image}")
        plt.show()

        print("\n✓ Terminé!")

except Exception as e:
    print(f"\n❌ Erreur lors de la génération du graphique : {e}")
    print("Vérifiez le contenu du fichier CSV.")