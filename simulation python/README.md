# Simulateur de diffusion de la chaleur

Simulation numérique 2D de la diffusion thermique dans une plaque rectangulaire avec interface graphique.

---

## Avant de commencer

Il faut avoir **Python 3.8 ou plus** installé sur l'ordinateur.

Ensuite, il faut installer les packages nécessaires en ouvrant un terminal et en collant cette commande :

```bash
pip install numpy numba PyQt5 pyqtgraph matplotlib
```

---

## Lancer le simulateur

S'assurer que tous les fichiers du projet sont dans le **même dossier**, puis exécuter :

```bash
python main.py
```

Mettre la fenêtre en plein écran pour voir tous les graphiques.

---

## Utilisation rapide

1. Cliquer sur **Charger les paramètres (json)** pour charger les valeurs par défaut.
2. Ajuster les paramètres ou les positions des thermistances si nécessaire.
3. Cliquer sur **Lancer la simulation** *(quelques secondes de délai normal au premier lancement)*.
4. Une fois terminé, choisir un dossier, entrer un nom de fichier, et cliquer sur **Sauvegarder les résultats**.

Voir le Manuel d'utilisation (.pdf) pour plus de détails.