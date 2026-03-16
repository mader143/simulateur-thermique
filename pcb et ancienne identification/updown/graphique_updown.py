import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

dossier_script = os.path.dirname(os.path.abspath(__file__))
fichier_xlsx = os.path.join(dossier_script, "rechau+refroi.xlsx")

# --- Lecture des données ---
# Expérience A
pol = pd.read_excel(fichier_xlsx, sheet_name=0)
t = pol["temps"].to_numpy()
T = pol["temperature_C"].to_numpy()

plt.plot(t, T)
plt.show()