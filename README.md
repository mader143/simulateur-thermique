# Simulateur Thermique
# Équipe 5 (Da best)

## Description

Simulateur thermique 2D pour modéliser la diffusion de chaleur dans une plaque métallique. Le projet regroupe une simulation numérique en Python avec interface graphique PyQt5, une simulation du système et du régulateur via Simulink (Matlab), du code Arduino pour l'acquisition et la régulation d'un prototype réel, et les données expérimentales pour la validation des différents paramètres identifiés.

## Contenu du projet

**Simulation Python** : Résolution par différences finies de l'équation de diffusion thermique, interface utilisateur interactive, génération de résultats et animations.

**Simulation Simulink** : Division du système/procédé en sous-systèmes et identification des fonctions de transfert de ceux-ci. Ajout d'un régulateur PID pour valider la commande contrôlant le prototype.

**Code Arduino** : Contrôleur PID pour régulation thermique, conditionnement des signaux, identification expérimentale, enregistrement des données.

**Conception PCB** : Schémas et circuits imprimés KiCad avec Arduino Mega 2560, amplificateurs opérationnels, et conditionnement analogique pour la lecture de la température en trois points sur la plaque métallique. 
