import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# --- Données (PWM converti en duty cycle) ---
data = pd.DataFrame({
    'pwm': [10,10,10,10,20,20,20,20,30,30,30],
    'temp': [22.8,18,19.5,25,16.4,16.6,19.5,29,15.7,28,32.4],
    'puissance': [0.89,1.6,1.37,0.56,2.74,2.73,2.3,0.91,3.85,2.06,1.39]
})
data['duty'] = data['pwm'] / 255 * 100

X = data[['duty','temp']].values
y = data['puissance'].values

# --- Modèles à tester ---
def model_lineaire(X, a, b, c):
    duty, temp = X[:,0], X[:,1]
    return a*duty + b*temp + c

def model_quadratique(X, a, b, c, d, e, f):
    duty, temp = X[:,0], X[:,1]
    return a*duty**2 + b*temp**2 + c*duty*temp + d*duty + e*temp + f

def model_expo_duty(X, a, b, c, d):
    duty, temp = X[:,0], X[:,1]
    return a * np.exp(b*duty) + c*temp + d

def model_puissance_duty(X, a, b, c, d):
    duty, temp = X[:,0], X[:,1]
    return a * duty**b + c*temp + d

modeles = {
    'Linéaire':          model_lineaire,
    'Quadratique':       model_quadratique,
    'Exponentiel(duty)': model_expo_duty,
    'Puissance(duty)':   model_puissance_duty,
}

# --- Fit et évaluation ---
print(f"{'Modèle':<22} {'R²':>8}  {'RMSE':>8}  Paramètres")
print("-"*75)

resultats = {}
for nom, modele in modeles.items():
    try:
        popt, _ = curve_fit(modele, X, y, maxfev=10000)
        y_pred = modele(X, *popt)
        r2   = 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)
        rmse = np.sqrt(np.mean((y - y_pred)**2))
        resultats[nom] = (r2, rmse, popt, modele)
        print(f"{nom:<22} {r2:>8.4f}  {rmse:>8.4f}  {np.round(popt,4)}")
    except Exception as e:
        print(f"{nom:<22}  ÉCHEC: {e}")

# --- Meilleur modèle ---
meilleur = max(resultats, key=lambda k: resultats[k][0])
r2, rmse, popt, modele = resultats[meilleur]
print(f"\n✅ Meilleur modèle: {meilleur}  (R²={r2:.4f})")

# --- Graphique ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle(f"Curve Fit — Meilleur modèle: {meilleur} (R²={r2:.4f})", fontsize=13)

# Graphe 1: valeurs prédites vs réelles
y_pred = modele(X, *popt)
axes[0].scatter(y, y_pred, color='steelblue', s=80, zorder=3)
lim = [min(y.min(), y_pred.min())-0.1, max(y.max(), y_pred.max())+0.1]
axes[0].plot(lim, lim, 'r--', label='Parfait')
axes[0].set_xlabel("Puissance mesurée")
axes[0].set_ylabel("Puissance prédite")
axes[0].set_title("Prédit vs Mesuré")
axes[0].legend(); axes[0].grid(True)

# Graphe 2: contour duty cycle vs température
duty_range = np.linspace(data['duty'].min()*0.95, data['duty'].max()*1.05, 50)
temp_range = np.linspace(data['temp'].min()*0.95, data['temp'].max()*1.05, 50)
DUTY, TEMP = np.meshgrid(duty_range, temp_range)
X_grid = np.column_stack([DUTY.ravel(), TEMP.ravel()])
Z = modele(X_grid, *popt).reshape(DUTY.shape)

cp = axes[1].contourf(DUTY, TEMP, Z, levels=20, cmap='viridis')
plt.colorbar(cp, ax=axes[1], label='Puissance prédite')
axes[1].scatter(data['duty'], data['temp'], c=data['puissance'],
                cmap='viridis', edgecolors='white', s=100, zorder=5)
axes[1].set_xlabel("Duty Cycle (%)")
axes[1].set_ylabel("Température initiale (°C)")
axes[1].set_title("Contour de réponse")

plt.tight_layout()
plt.show()