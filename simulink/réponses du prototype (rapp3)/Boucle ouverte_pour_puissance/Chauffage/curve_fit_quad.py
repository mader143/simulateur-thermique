import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from sklearn.model_selection import LeaveOneOut

# --- Données ---
data = pd.DataFrame({
    'duty':     [3.921568627,3.921568627,3.921568627,3.921568627,
                 7.843137255,7.843137255,7.843137255,7.843137255,
                 11.76470588,11.76470588, 11.76470588],
    'temp':     [22.8,18,19.5,25,16.4,16.6,19.5,29,15.7,28, 32.4],
    'puissance':[0.89,1.6,1.37,0.56,2.74,2.73,2.3,0.91,3.85,2.06, 1.39]
})

X = data[['duty','temp']].values
y = data['puissance'].values

# --- Modèle quadratique ---
def model_quadratique(X, a, b, c, d, e, f):
    duty, temp = X[:,0], X[:,1]
    return a*duty**2 + b*temp**2 + c*duty*temp + d*duty + e*temp + f

# --- Fit ---
popt, _ = curve_fit(model_quadratique, X, y, maxfev=10000)
a, b, c, d, e, f = popt

y_pred = model_quadratique(X, *popt)

r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)

# --- Validation croisée ---
loo = LeaveOneOut()
y_true_cv = []
y_pred_cv = []

for train_idx, test_idx in loo.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    popt_cv, _ = curve_fit(model_quadratique, X_train, y_train, maxfev=10000)
    pred = model_quadratique(X_test, *popt_cv)

    y_true_cv.append(y_test[0])
    y_pred_cv.append(pred[0])

y_true_cv = np.array(y_true_cv)
y_pred_cv = np.array(y_pred_cv)

r2_cv = 1 - np.sum((y_true_cv - y_pred_cv)**2) / np.sum((y_true_cv - np.mean(y_true_cv))**2)

print(f"R² (fit) = {r2:.4f}")
print(f"R² (validation croisée) = {r2_cv:.4f}")

# --- Formule ---
def signe(val):
    return '+' if val >= 0 else '-'

# --- Surface ---
duty_range = np.linspace(data['duty'].min()*0.95, data['duty'].max()*1.05, 60)
temp_range = np.linspace(data['temp'].min()*0.95, data['temp'].max()*1.05, 60)
DC, TEMP = np.meshgrid(duty_range, temp_range)
X_grid = np.column_stack([DC.ravel(), TEMP.ravel()])
Z = model_quadratique(X_grid, *popt).reshape(DC.shape)

# --- Graphique 3D ---
fig = plt.figure(figsize=(13, 8))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(DC, TEMP, Z, cmap='viridis', alpha=0.75, edgecolor='none')
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='Puissance')

ax.scatter(data['duty'], data['temp'], data['puissance'],
           color='red', s=60, zorder=5, label='Mesures', depthshade=False)

for _, row in data.iterrows():
    p_fit = model_quadratique(np.array([[row['duty'], row['temp']]]), *popt)[0]
    ax.plot([row['duty'], row['duty']],
            [row['temp'], row['temp']],
            [row['puissance'], p_fit],
            color='red', linewidth=0.8, alpha=0.6)

ax.set_xlabel("Duty Cycle (%)", labelpad=10)
ax.set_ylabel("Température initiale (°C)", labelpad=10)
ax.set_zlabel("Puissance", labelpad=10)
#ax.set_title("Régression quadratique — Puissance vs DC et Température", fontsize=13, pad=20)
ax.legend(loc='upper left')

# --- Texte affiché ---
texte = (
    f"$R^2 = {r2:.4f}$\n"
    f"$R^2_{{CV}} = {r2_cv:.4f}$\n\n"
    f"$P = {a:.4f}\\cdot DC^2 {signe(b)} {abs(b):.4f}\\cdot T^2 "
    f"{signe(c)} {abs(c):.4f}\\cdot DC\\cdot T$\n"
    f"$\\quad {signe(d)} {abs(d):.4f}\\cdot DC "
    f"{signe(e)} {abs(e):.4f}\\cdot T "
    f"{signe(f)} {abs(f):.4f}$"
)
print(texte)
#fig.text(
 #   0.01, 0.02, texte,
  #  fontsize=10,
   # verticalalignment='bottom',
    #bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))

plt.tight_layout()
#plt.savefig("curve_fit_3d.png", dpi=150, bbox_inches='tight')
plt.show()