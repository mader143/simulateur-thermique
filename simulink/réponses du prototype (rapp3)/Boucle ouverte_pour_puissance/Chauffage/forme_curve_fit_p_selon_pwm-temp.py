import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.model_selection import LeaveOneOut

# --- Données ---
data = pd.DataFrame({
    'pwm': [10,10,10,10,20,20,20,20,30,30,30],
    'temp': [22.8,18,19.5,25,16.4,16.6,19.5,29,15.7,28,32.4],
    'puissance': [0.89,1.6,1.37,0.56,2.74,2.73,2.3,0.91,3.85,2.06,1.39]
})
data['duty'] = data['pwm'] / 255 * 100

X = data[['duty','temp']].values
y = data['puissance'].values

# --- Modèles ---
def model_lineaire(X, a, b, c):
    d, t = X[:,0], X[:,1]
    return a*d + b*t + c

def model_quadratique(X, a, b, c, d, e, f):
    d, t = X[:,0], X[:,1]
    return a*d**2 + b*t**2 + c*d*t + d*d + e*t + f

def model_expo(X, a, b, c, d):
    dcy, t = X[:,0], X[:,1]
    return a*np.exp(b*dcy) + c*t + d

def model_puissance(X, a, b, c, d):
    dcy, t = X[:,0], X[:,1]
    return a*dcy**b + c*t + d

modeles = {
    'Linéaire': model_lineaire,
    'Quadratique': model_quadratique,
    'Exponentiel': model_expo,
    'Puissance': model_puissance
}

# --- Validation croisée ---
loo = LeaveOneOut()

print(f"{'Modèle':<15} {'R² CV':>10} {'RMSE CV':>10}")
print("-"*40)

resultats = {}

for nom, modele in modeles.items():
    y_true = []
    y_pred = []

    for train_idx, test_idx in loo.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        try:
            popt, _ = curve_fit(modele, X_train, y_train, maxfev=10000)
            pred = modele(X_test, *popt)

            y_true.append(y_test[0])
            y_pred.append(pred[0])
        except:
            pass

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    r2 = 1 - np.sum((y_true - y_pred)**2) / np.sum((y_true - np.mean(y_true))**2)
    rmse = np.sqrt(np.mean((y_true - y_pred)**2))

    resultats[nom] = r2

    print(f"{nom:<15} {r2:>10.4f} {rmse:>10.4f}")

# --- Meilleur modèle ---
best = max(resultats, key=resultats.get)
print(f"\n✅ Meilleur modèle (validation croisée) : {best}")