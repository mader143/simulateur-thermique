import serial
import csv
from datetime import datetime
import time
import os
import matplotlib.pyplot as plt
import pandas as pd

# Pour exécuter le script: pip install pyserial pandas matplotlib

# ============ CONFIGURATION ============
PORT = 'COM6'  # Changez au besoin (COM3, COM4, etc.)
BAUDRATE = 9600

# EMPLACEMENT D'ENREGISTREMENT
CHEMIN_ENREGISTREMENT = r'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\code arduino et fichiers kicad\ident_therm' 


# Nom du fichier (avec horodatage automatique)
NOM_FICHIER = f'temperature_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

# Chemin complet
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
                    
                    # Ignorer les lignes avec des tabulations (ancien format)
                    if '\t' in ligne:
                        continue
                    
                    # Écrire seulement les lignes avec UNE SEULE virgule (format CSV valide)
                    if ligne.count(',') == 1:
                        parties = ligne.split(',')
                        
                        # Vérifier que les deux parties existent et ne sont pas vides
                        if len(parties) == 2 and parties[0] and parties[1]:
                            # Essayer de déterminer si c'est l'en-tête ou des données
                            try:
                                # Si on peut convertir en float, ce sont des données
                                float(parties[0])
                                float(parties[1])
                                writer.writerow(parties)
                                fichier.flush()
                            except ValueError:
                                # C'est l'en-tête, l'écrire une seule fois
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
    # Lire le fichier CSV
    data = pd.read_csv(FICHIER_COMPLET)
    
    # Vérifier que le fichier contient des données
    if len(data) == 0:
        print("❌ Aucune donnée à tracer!")
    else:
        # Créer la figure
        plt.figure(figsize=(10, 6))
        plt.plot(data['temps_s'], data['temperature_C'], 'b-', linewidth=2, marker='o', markersize=4)
        
        # Personnalisation du graphique
        plt.xlabel('Temps (s)', fontsize=12)
        plt.ylabel('Température (°C)', fontsize=12)
        plt.title('Évolution de la température en fonction du temps', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # Sauvegarder le graphique
        nom_image = FICHIER_COMPLET.replace('.csv', '.png')
        plt.savefig(nom_image, dpi=300, bbox_inches='tight')
        print(f"✓ Graphique sauvegardé : {nom_image}")
        
        # Afficher le graphique
        plt.show()
        
        print("\n✓ Terminé!")
    
except Exception as e:
    print(f"\n❌ Erreur lors de la génération du graphique : {e}")
    print("Vérifiez le contenu du fichier CSV.")