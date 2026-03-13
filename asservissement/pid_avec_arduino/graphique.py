import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# ============ CONFIGURATION ============
CHEMIN_ENREGISTREMENT = r'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\asservissement\pid_avec_arduino\pid_avec_nouvelle_ident'
SETPOINT = 28.0
T_init   = 23.5

MODE = 'T3'  # 'T3' ou 'ALL'
# =======================================

marge_sup = T_init + (SETPOINT - T_init) * 1.05
marge_inf = T_init + (SETPOINT - T_init) * 0.95

# ── Trouve le CSV ──
pattern = os.path.join(CHEMIN_ENREGISTREMENT, 'consigne28.csv')
fichiers = glob.glob(pattern)

if not fichiers:
    print(f"❌ Aucun fichier consigne28.csv trouvé dans :\n{CHEMIN_ENREGISTREMENT}")
    exit(1)

FICHIER_COMPLET = max(fichiers, key=os.path.getmtime)
print(f"✓ Fichier chargé : {FICHIER_COMPLET}")

# ── Lecture CSV ──
try:
    data = pd.read_csv(FICHIER_COMPLET, header=None,
                       names=['temps_s', 'T1_C', 'T2_C', 'T3_C',
                              'T3_estimT2', 'T3_estimT1', 'T3_moy',
                              'erreur', 'commande_u'])
    data = data[pd.to_numeric(data['temps_s'], errors='coerce').notna()].astype(float).reset_index(drop=True)

    if len(data) == 0:
        print("❌ Aucune donnée à tracer!")
        exit(1)

    print(f"✓ {len(data)} lignes chargées")

except Exception as e:
    print(f"❌ Erreur lecture CSV : {e}")
    exit(1)

# ── Fonction graphique T3 ──
def tracer_T3(ax):
    ax.plot(data['temps_s'], data['T3_C'],
            color='#2196F3', linewidth=1.5, label='T3 mesurée')
    ax.plot(data['temps_s'], data['T3_moy'],
            color='#4CAF50', linewidth=1.5, linestyle='--', label='T3_moy (estimée)')
    ax.axhline(y=SETPOINT,  color='#F44336', linestyle='--', linewidth=1.2,
               label=f'Consigne ({SETPOINT}°C)')
    ax.axhline(y=marge_sup, color='#F44336', linestyle=':', linewidth=0.8,
               label=f'+5% ({marge_sup:.2f}°C)')
    ax.axhline(y=marge_inf, color='#F44336', linestyle=':', linewidth=0.8,
               label=f'-5% ({marge_inf:.2f}°C)')
    ax.fill_between(data['temps_s'], marge_inf, marge_sup,
                    alpha=0.08, color='#F44336', label='Zone ±5%')

    # Calcul et annotation du temps de réponse
    dans_zone = data[(data['T3_moy'] >= marge_inf) & (data['T3_moy'] <= marge_sup)]
    if not dans_zone.empty:
        t_rep = dans_zone['temps_s'].iloc[0]
        ax.axvline(x=t_rep, color='black', linestyle='--', linewidth=1.0)
        ax.annotate(f'Tr = {t_rep:.1f}s',
                    xy=(t_rep, SETPOINT),
                    xytext=(t_rep + 5, SETPOINT - 1.5),
                    fontsize=9, color='black',
                    arrowprops=dict(arrowstyle='->', color='black'))
        print(f"✓ Temps de réponse (±5%) : {t_rep:.1f} s")
    else:
        print("⚠ T3_moy n'entre jamais dans la zone ±5%")

    ax.set_ylabel('Température (°C)')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)


# ── Tracé ──
if MODE == 'T3':

    fig, ax = plt.subplots(figsize=(14, 6))
    tracer_T3(ax)
    ax.set_xlabel('Temps (s)')
    nom_image = FICHIER_COMPLET.replace('.csv', '_T3.png')

elif MODE == 'ALL':

    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

    tracer_T3(axes[0])

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
    axes[2].set_ylim(-270, 270)
    axes[2].legend(fontsize=10)
    axes[2].grid(True, alpha=0.3)

    nom_image = FICHIER_COMPLET.replace('.csv', '_PID.png')

else:
    print(f"❌ MODE invalide : '{MODE}' — choisir 'T3' ou 'ALL'")
    exit(1)

plt.tight_layout()
plt.savefig(nom_image, dpi=300, bbox_inches='tight')
print(f"✓ Graphique sauvegardé : {nom_image}")
plt.show()