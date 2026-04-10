import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from sklearn.model_selection import LeaveOneOut

# --- Données ---
data = pd.DataFrame({
    'pwm': [
        -10, -10, -10, -10,
        -20, -20, -20, -20,
        -30, -30, -30, -30
    ],
    'temp': [
        22, 24.6, 25.8, 28.8,
        18.2, 22.6, 26.9, 35.1,
        20.7, 21.8, 33, 36.7
    ],
    'puissance': [
        -0.58, -0.95, -1.12, -1.57,
        -0.59, -1.25, -1.88, -3.08,
        -1.4, -1.57, -3.22, -3.77
    ]
})

data['duty'] = data['pwm'] / 255 * 100

X = data[['duty', 'temp']].values
y = data['puissance'].values


# --- Modèle linéaire ---
def model_lineaire(X, a, b, c):
    d, t = X[:, 0], X[:, 1]
    return a * d + b * t + c


# --- Fit ---
popt, pcov = curve_fit(model_lineaire, X, y)
a, b, c = popt
perr = np.sqrt(np.diag(pcov))

y_pred_full = model_lineaire(X, *popt)
ss_res = np.sum((y - y_pred_full) ** 2)
ss_tot = np.sum((y - np.mean(y)) ** 2)
r2_full  = 1 - ss_res / ss_tot
rmse_full = np.sqrt(np.mean((y - y_pred_full) ** 2))

# --- Validation croisée LOO ---
loo = LeaveOneOut()
y_true_loo, y_pred_loo = [], []

for train_idx, test_idx in loo.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    popt_loo, _ = curve_fit(model_lineaire, X_train, y_train)
    y_true_loo.append(y_test[0])
    y_pred_loo.append(model_lineaire(X_test, *popt_loo)[0])

y_true_loo = np.array(y_true_loo)
y_pred_loo = np.array(y_pred_loo)
r2_loo   = 1 - np.sum((y_true_loo - y_pred_loo)**2) / np.sum((y_true_loo - np.mean(y_true_loo))**2)
rmse_loo = np.sqrt(np.mean((y_true_loo - y_pred_loo)**2))

# --- Résultats console ---
print("=" * 50)
print("  MODÈLE LINÉAIRE : P = a·duty + b·T + c")
print("=" * 50)
print(f"\n{'Paramètre':<12} {'Valeur':>12} {'± Écart-type':>14}")
print("-" * 40)
print(f"{'a (duty)':<12} {a:>12.6f} {'± ' + f'{perr[0]:.6f}':>14}")
print(f"{'b (temp)':<12} {b:>12.6f} {'± ' + f'{perr[1]:.6f}':>14}")
print(f"{'c (cste)':<12} {c:>12.6f} {'± ' + f'{perr[2]:.6f}':>14}")
print(f"\n{'Métrique':<20} {'Fit complet':>12} {'LOO CV':>10}")
print("-" * 44)
print(f"{'R²':<20} {r2_full:>12.4f} {r2_loo:>10.4f}")
print(f"{'RMSE':<20} {rmse_full:>12.4f} {rmse_loo:>10.4f}")

def signe(val):
    return '+' if val >= 0 else '-'

print(f"\n📐 Formule finale :")
print(f"   P = {a:.6f}·duty {signe(b)} {abs(b):.6f}·T {signe(c)} {abs(c):.6f}")

print(f"\n{'PWM':>5} {'Duty%':>7} {'T (°C)':>8} {'P mesuré':>10} {'P prédit':>10} {'Erreur':>8}")
print("-" * 55)
for _, row in data.iterrows():
    d, t = row['duty'], row['temp']
    p_mes  = row['puissance']
    p_pred = a * d + b * t + c
    print(f"{int(row['pwm']):>5} {d:>7.2f} {t:>8.1f} {p_mes:>10.3f} {p_pred:>10.3f} {p_mes-p_pred:>8.4f}")

# --- Surface 3D ---
duty_range = np.linspace(data['duty'].min() * 1.05, data['duty'].max() * 0.95, 60)
temp_range = np.linspace(data['temp'].min() * 0.95, data['temp'].max() * 1.05, 60)
DC, TEMP = np.meshgrid(duty_range, temp_range)
X_grid = np.column_stack([DC.ravel(), TEMP.ravel()])
Z = model_lineaire(X_grid, *popt).reshape(DC.shape)

fig = plt.figure(figsize=(13, 8))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(DC, TEMP, Z, cmap='viridis', alpha=0.75, edgecolor='none')
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='Puissance (W)')

ax.scatter(data['duty'], data['temp'], data['puissance'],
           color='red', s=60, zorder=5, label='Mesures', depthshade=False)

# Résidus verticaux
for _, row in data.iterrows():
    p_fit = model_lineaire(np.array([[row['duty'], row['temp']]]), *popt)[0]
    ax.plot([row['duty'], row['duty']],
            [row['temp'],  row['temp']],
            [row['puissance'], p_fit],
            color='red', linewidth=0.8, alpha=0.6)

ax.set_xlabel("Duty Cycle (%)", labelpad=10)
ax.set_ylabel("Température initiale (°C)", labelpad=10)
ax.set_zlabel("Puissance (W)", labelpad=10)
ax.legend(loc='upper left')

texte = (
    f"$R^2 = {r2_full:.4f}$\n"
    f"$R^2_{{CV}} = {r2_loo:.4f}$\n\n"
    f"$P = {a:.4f}\\cdot DC {signe(b)} {abs(b):.4f}\\cdot T {signe(c)} {abs(c):.4f}$")
print(texte)

plt.tight_layout()
plt.show()