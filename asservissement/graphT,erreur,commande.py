import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# ============ CONFIGURATION ============
CHEMIN_ENREGISTREMENT = r'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\asservissement\test_asservissement'
SETPOINT = 28.0
# =======================================

# ── Trouve le CSV le plus récent dans le dossier ──
pattern = os.path.join(CHEMIN_ENREGISTREMENT, 'temperature_*.csv')
fichiers = glob.glob(pattern)

if not fichiers:
    print(f"❌ Aucun fichier temperature_*.csv trouvé dans :\n{CHEMIN_ENREGISTREMENT}")
    exit(1)

FICHIER_COMPLET = max(fichiers, key=os.path.getmtime)
print(f"✓ Fichier chargé : {FICHIER_COMPLET}")

# ── Lecture CSV (pas d'entête) ──
# Colonnes : 0=temps_s, 1=T3, 2=erreur, 3=commande_u
try:
    raw = pd.read_csv(FICHIER_COMPLET, header=None)
    raw = raw[pd.to_numeric(raw[0], errors='coerce').notna()].astype(float).reset_index(drop=True)

    temps      = raw[0]
    T3         = raw[1]
    erreur     = raw[2]
    commande_u = raw[3]

    if len(raw) == 0:
        print("❌ Aucune donnée à tracer!")
        exit(1)

    print(f"✓ {len(raw)} lignes chargées")

except Exception as e:
    print(f"❌ Erreur lecture CSV : {e}")
    exit(1)

# ── Tracé ──
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
fig.suptitle('Contrôleur PID Thermique', fontsize=14, fontweight='bold')

# --- Graphique 1 : T3 + setpoint ---
axes[0].plot(temps, T3, color='#FF9800', linewidth=1.5, label='Température estimée T3')
axes[0].axhline(y=SETPOINT, color='#F44336', linestyle='--',
                linewidth=1.5, label=f'Consigne ({SETPOINT}°C)')
axes[0].set_ylabel('Température (°C)')
axes[0].set_title('Température estimée T3 vs consigne')
axes[0].legend(fontsize=8)
axes[0].grid(True, alpha=0.3)

# --- Graphique 2 : Erreur ---
axes[1].plot(temps, erreur, color='#9C27B0', linewidth=1.5, label='Erreur')
axes[1].axhline(y=0, color='black', linestyle='--', linewidth=0.8)
axes[1].fill_between(temps, erreur, 0,
                     where=(erreur > 0), alpha=0.15, color='#F44336', label='Trop froid')
axes[1].fill_between(temps, erreur, 0,
                     where=(erreur < 0), alpha=0.15, color='#2196F3', label='Trop chaud')
axes[1].set_ylabel('Erreur (°C)')
axes[1].set_title('Erreur du PID')
axes[1].legend(fontsize=8)
axes[1].grid(True, alpha=0.3)

# --- Graphique 3 : Commande u — zoomé sur les vraies valeurs ---
axes[2].plot(temps, commande_u, color='#4CAF50', linewidth=1.5, label='Commande u')
axes[2].axhline(y=0, color='black', linestyle='-', linewidth=0.8)
axes[2].fill_between(temps, commande_u, 0,
                     where=(commande_u > 0), alpha=0.12, color='#F44336', label='Chauffe')
axes[2].fill_between(temps, commande_u, 0,
                     where=(commande_u < 0), alpha=0.12, color='#2196F3', label='Refroidit')
axes[2].set_ylabel('Commande u (PWM)')
axes[2].set_xlabel('Temps (s)')
axes[2].set_title('Commande PWM appliquée')
axes[2].legend(fontsize=8)
axes[2].grid(True, alpha=0.3)

# ✅ Auto-zoom : axe Y calé sur les vraies valeurs + petite marge
margin = max((commande_u.max() - commande_u.min()) * 0.15, 10)
axes[2].set_ylim(commande_u.min() - margin, commande_u.max() + margin)

plt.tight_layout()

# ── Sauvegarde ──
nom_image = FICHIER_COMPLET.replace('.csv', '_graphiques.png')
plt.savefig(nom_image, dpi=300, bbox_inches='tight')
print(f"✓ Graphique sauvegardé : {nom_image}")
plt.show()