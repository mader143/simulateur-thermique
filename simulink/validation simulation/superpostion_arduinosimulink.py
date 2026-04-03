import os
import matplotlib
matplotlib.use('TkAgg')   # ← DOIT être avant pyplot
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============ CONFIGURATION ============
CHEMIN_CSV_ARDUINO   = r'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\simulink\validation simulation\2330.csv'
CHEMIN2_CSV_ARDUINO   = r'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\simulink\validation simulation\temps2330.csv'
CHEMIN_CSV_SIMULINK  = r'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\simulink\validation simulation\donnees2330.csv'

SETPOINT  = 28.0
T_init    = 23.5
LISSAGE   = 5
# =======================================

marge_sup = T_init + (SETPOINT - T_init) * 1.05
marge_inf = T_init + (SETPOINT - T_init) * 0.95

# ── Chargement CSV Arduino ──
try:
    data = pd.read_csv(CHEMIN_CSV_ARDUINO, header=None,
                       names=['temps_s', 'T1_C', 'T2_C', 'T3_C',
                              'T3_estimT2', 'T3_estimT1', 'T3_moy',
                              'erreur', 'commande_u'])
    data = data[pd.to_numeric(data['temps_s'], errors='coerce').notna()].astype(float).reset_index(drop=True)
    data['temps_s'] -= data['temps_s'].iloc[0]
    print(f"✓ Arduino : {len(data)} lignes chargées")
except Exception as e:
    print(f"❌ Erreur lecture CSV Arduino : {e}"); exit(1)

# ── Chargement CSV Simulink ──
try:
    sim = pd.read_csv(CHEMIN_CSV_SIMULINK)
    sim.columns = ['time', 'consigne_sim', 'sortie_sim']
    sim['time'] -= sim['time'].iloc[0]
    print(f"✓ Simulink : {len(sim)} lignes chargées")
except Exception as e:
    print(f"❌ Erreur lecture CSV Simulink : {e}"); exit(1)

# ── Lissage Arduino ──
T3_lisse = data['T3_C'].rolling(window=LISSAGE, center=True).mean()

# ── Calcul temps de réponse Arduino ──
dans_zone = data[(data['T3_moy'] >= marge_inf) & (data['T3_moy'] <= marge_sup)]
t_rep_arduino = dans_zone['temps_s'].iloc[0] if not dans_zone.empty else None

# ── Calcul temps de réponse Simulink ──
sim_in_zone = sim[(sim['sortie_sim'] >= marge_inf) & (sim['sortie_sim'] <= marge_sup)]
t_rep_sim = sim_in_zone['time'].iloc[0] if not sim_in_zone.empty else None

# ══════════════════════════════════════
#  GRAPHIQUE
# ══════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 6))

# --- Consigne ---
ax.axhline(y=SETPOINT, color='#F44336', linestyle='--', linewidth=1.2,
           label=f'Consigne ({SETPOINT}°C)')
ax.axhline(y=marge_sup, color='#F44336', linestyle=':', linewidth=0.8,
           label=f'+5% ({marge_sup:.2f}°C)')
ax.axhline(y=marge_inf, color='#F44336', linestyle=':', linewidth=0.8,
           label=f'-5% ({marge_inf:.2f}°C)')
ax.fill_between(data['temps_s'], marge_inf, marge_sup,
                alpha=0.08, color='#F44336', label='Zone ±5%')

# --- Simulation Simulink ---
ax.plot(sim['time'], sim['sortie_sim'],
        color='#9C27B0', linewidth=2, linestyle='--',
        label='Simulation Simulink')

# --- Arduino brut ---
ax.plot(data['temps_s'], data['T3_C'],
        color='#2196F3', linewidth=2, 
        label='T3 Arduino')

# --- Temps de réponse Arduino ---
if t_rep_arduino:
    ax.axvline(x=t_rep_arduino, color='#2196F3', linestyle='--', linewidth=1.0)
    ax.annotate(f'Tr_exp = {t_rep_arduino:.1f}s',
                xy=(t_rep_arduino, SETPOINT),
                xytext=(t_rep_arduino + 5, SETPOINT - 1.5),
                fontsize=9, color='#2196F3',
                arrowprops=dict(arrowstyle='->', color='#2196F3'))
    print(f"✓ Temps de réponse Arduino (±5%) : {t_rep_arduino:.1f} s")
else:
    print("⚠ T3_moy n'entre jamais dans la zone ±5%")

# --- Temps de réponse Simulink ---
if t_rep_sim:
    ax.axvline(x=t_rep_sim, color='#9C27B0', linestyle='--', linewidth=1.0)
    ax.annotate(f'Tr_sim = {t_rep_sim:.1f}s',
                xy=(t_rep_sim, SETPOINT),
                xytext=(t_rep_sim + 5, SETPOINT + 0.8),
                fontsize=9, color='#9C27B0',
                arrowprops=dict(arrowstyle='->', color='#9C27B0'))
    print(f"✓ Temps de réponse Simulink (±5%) : {t_rep_sim:.1f} s")
else:
    print("⚠ Simulink n'entre jamais dans la zone ±5%")

# --- Mise en forme ---
ax.set_xlabel('Temps (s)', fontsize=12)
ax.set_ylabel('Température (°C)', fontsize=12)
ax.set_title('Réponse à un échelon de température — Simulation vs Expérimental', fontsize=13)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()

# ── Sauvegarde ──
nom_image = CHEMIN_CSV_SIMULINK.replace('.csv', '_vs_arduino.png')
plt.savefig(nom_image, dpi=300, bbox_inches='tight')
print(f"✓ Graphique sauvegardé : {nom_image}")
plt.show()

# ══════════════════════════════════════
#  GRAPHIQUE ÉCART (Simulink - Arduino)
# ══════════════════════════════════════

# Interpoler les valeurs Simulink aux instants Arduino
sortie_sim_interp = np.interp(data['temps_s'], sim['time'], sim['sortie_sim'])

# Calculer l'écart
ecart = sortie_sim_interp - data['T3_C']

fig2, ax2 = plt.subplots(figsize=(14, 5))

ax2.plot(data['temps_s'], ecart, color='#FF9800', linewidth=2, label='Écart (Simulink − Arduino)')
ax2.axhline(y=0, color='gray', linestyle='--', linewidth=1.0, label='Écart nul')
ax2.fill_between(data['temps_s'], ecart, 0, alpha=0.2, color='#FF9800')

ax2.set_xlabel('Temps (s)', fontsize=12)
ax2.set_ylabel('Écart de température (°C)', fontsize=12)
ax2.set_title('Écart entre Simulation Simulink et Mesure Arduino', fontsize=13)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

plt.tight_layout()

# ── Sauvegarde ──
nom_image_ecart = CHEMIN_CSV_SIMULINK.replace('.csv', '_ecart.png')
fig2.savefig(nom_image_ecart, dpi=300, bbox_inches='tight')
print(f"✓ Graphique écart sauvegardé : {nom_image_ecart}")

plt.show()

# ══════════════════════════════════════
#  GRAPHIQUE ÉCART EN POURCENTAGE
# ══════════════════════════════════════

# Interpoler les valeurs Simulink aux instants Arduino
sortie_sim_interp = np.interp(data['temps_s'], sim['time'], sim['sortie_sim'])

# Écart en % par rapport à la mesure Arduino
# On évite la division par zéro si T3_C est très proche de 0
ecart_pct = np.where(
    np.abs(data['T3_C']) > 0.01,
    (sortie_sim_interp - data['T3_C']) / data['T3_C'] * 100,
    np.nan
)

fig3, ax3 = plt.subplots(figsize=(14, 5))

ax3.plot(data['temps_s'], ecart_pct, color='#FF9800', linewidth=2, label='Écart (%)')
ax3.axhline(y=0,   color='gray',    linestyle='--', linewidth=1.0, label='Écart nul')
ax3.axhline(y= 15, color='#F44336', linestyle=':',  linewidth=1.2, label='+15%')
ax3.axhline(y=-15, color='#F44336', linestyle=':',  linewidth=1.2, label='-15%')
ax3.fill_between(data['temps_s'], -15, 15, alpha=0.08, color='#4CAF50', label='Zone ±15%')
ax3.fill_between(data['temps_s'], ecart_pct, 0, alpha=0.2, color='#FF9800')

# Mettre en évidence les zones hors tolérance
hors_zone = np.abs(ecart_pct) > 15
ax3.fill_between(data['temps_s'], ecart_pct, 0,
                 where=hors_zone, alpha=0.4, color='#F44336', label='Hors ±15%')

# Pourcentage du temps dans la zone
pct_dans_zone = np.sum(~hors_zone & ~np.isnan(ecart_pct)) / np.sum(~np.isnan(ecart_pct)) * 100
print(f"✓ Simulation dans la zone ±15% : {pct_dans_zone:.1f}% du temps")

ax3.set_xlabel('Temps (s)', fontsize=12)
ax3.set_ylabel('Écart (%)', fontsize=12)
ax3.set_title('Écart relatif Simulink vs Arduino — Tolérance ±15%', fontsize=13)
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)

# Annoter le % de conformité
ax3.text(0.02, 0.95, f'Conformité : {pct_dans_zone:.1f}% dans ±15%',
         transform=ax3.transAxes, fontsize=11,
         verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()

nom_image_pct = CHEMIN_CSV_SIMULINK.replace('.csv', '_ecart_pct.png')
fig3.savefig(nom_image_pct, dpi=300, bbox_inches='tight')
print(f"✓ Graphique écart % sauvegardé : {nom_image_pct}")

plt.show()