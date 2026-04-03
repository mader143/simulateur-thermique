import pandas as pd
import matplotlib.pyplot as plt

CHEMIN_CSV = r'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\simulink\validation simulation\comparaison.csv'

df = pd.read_csv(CHEMIN_CSV, header=None, sep=r'\s+')

t_arduino = df[0].values
T_arduino = df[1].values
t_sim     = df[2].values
T_sim     = df[3].values

# Cut to same length
n = min(len(t_arduino), len(t_sim))
t_arduino, T_arduino = t_arduino[:n], T_arduino[:n]
t_sim,     T_sim     = t_sim[:n],     T_sim[:n]

plt.figure()
plt.plot(t_arduino, T_arduino, label='Arduino')
plt.plot(t_sim,     T_sim,     label='Simulink')
plt.xlabel('Temps (s)')
plt.ylabel('Température (°C)')
plt.legend()
plt.xlim(0, 450)
plt.grid(True)
plt.tight_layout()
nom_image1 = CHEMIN_CSV.replace('.csv', 'graphique.png')
plt.savefig(nom_image1, dpi=300, bbox_inches='tight')
print(f"✓ Graphique sauvegardé : {nom_image1}")
plt.show()


plt.figure()
plt.plot(t_arduino, T_arduino - T_sim, label='Erreur (Arduino - Simulink)', color='red')
plt.xlabel('Temps (s)')
plt.ylabel('Écart (°C)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.xlim(0, 450)

nom_image2 = CHEMIN_CSV.replace('.csv', 'écart.png')
plt.savefig(nom_image2, dpi=300, bbox_inches='tight')
print(f"✓ Graphique écart sauvegardé : {nom_image2}")
plt.show()
