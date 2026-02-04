import serial
import csv
from datetime import datetime
import time
import os

# ============ CONFIGURATION ============
PORT = 'COM3'  # Changez selon votre port série (COM3, COM4, etc.)
BAUDRATE = 9600

# EMPLACEMENT D'ENREGISTREMENT - Modifiez ce chemin selon vos besoins
CHEMIN_ENREGISTREMENT = r'C:\Users\VotreNom\Documents'  # Windows
# CHEMIN_ENREGISTREMENT = '/home/votreuser/Documents'   # Linux
# CHEMIN_ENREGISTREMENT = '/Users/votreuser/Documents'  # Mac

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
                    
                    donnees = ligne.split(',')
                    writer.writerow(donnees)
                    fichier.flush()
                        
    except KeyboardInterrupt:
        print("\n\n⚠ Arrêt manuel")
    finally:
        ser.close()
        print(f"\n✓ Fichier sauvegardé dans :\n{FICHIER_COMPLET}")