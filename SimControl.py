# Classe pour contrôler l'interface graphique
import json
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

from SimulationThermique import SimulationThermique


class SimControl(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)
        base_path = os.path.join(os.path.dirname(__file__))
        uic.loadUi(os.path.join(base_path, "interface_simulateur.ui"), self)

        self.simulation = SimulationThermique()

        # Initialiser les boutons ---------------------------------------------------------------------------

        # Pour charger les paramètres depuis le fichier json
        self.pushButton_load_json.clicked.connect(self.load_json)

        # Pour changer les paramètres de la simulation depuis les boutons
        self.doubleSpinBox_longueur.valueChanged.connect(
            lambda: setattr(self.simulation, 'longueur', self.doubleSpinBox_longueur.value() / 1000))
        self.doubleSpinBox_largeur.valueChanged.connect(
            lambda: setattr(self.simulation, 'largeur', self.doubleSpinBox_largeur.value() / 1000))
        self.doubleSpinBox_epaisseur.valueChanged.connect(
            lambda: setattr(self.simulation, 'epaisseur', self.doubleSpinBox_epaisseur.value() / 1000))
        self.doubleSpinBox_ti.valueChanged.connect(
            lambda: setattr(self.simulation, 'T_init', self.doubleSpinBox_ti.value() + 273.15))
        self.spinBox_temps.valueChanged.connect(
            lambda: setattr(self.simulation, 't_simulation', int(self.spinBox_temps.value())))
        self.doubleSpinBox_k.valueChanged.connect(
            lambda: setattr(self.simulation, 'k', self.doubleSpinBox_k.value()))
        self.doubleSpinBox_p.valueChanged.connect(
            lambda: setattr(self.simulation, 'rho', self.doubleSpinBox_p.value()))
        self.doubleSpinBox_cp.valueChanged.connect(
            lambda: setattr(self.simulation, 'cp', self.doubleSpinBox_cp.value()))
        self.doubleSpinBox_h.valueChanged.connect(
            lambda: setattr(self.simulation, 'h_conv', self.doubleSpinBox_h.value()))
        self.doubleSpinBox_dx.valueChanged.connect(
            lambda: setattr(self.simulation, 'dx', self.doubleSpinBox_dx.value() / 1000))
        self.doubleSpinBox_pin.valueChanged.connect(
            lambda: setattr(self.simulation, 'Pin', self.doubleSpinBox_pin.value()))

        # Lancer la simulation thermique
        self.pushButton_start.clicked.connect(self.simulation.simuler_diffusion)

        # Charger les paramètres par défaut au démarrage
        self.load_json()

    def test(self):
        print(self.simulation.longueur,
              self.simulation.largeur,
              self.simulation.epaisseur,
              self.simulation.T_init,
              self.simulation.t_simulation,
              self.simulation.k,
              self.simulation.rho,
              self.simulation.cp,
              self.simulation.h_conv,
              self.simulation.dx,
              self.simulation.Pin)

    def load_json(self):

        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "params_sim.json")

        with open(json_path, "r") as f:
            params = json.load(f)

        # Bloquer les signaux pendant le chargement
        widgets = [
            self.doubleSpinBox_longueur,
            self.doubleSpinBox_largeur,
            self.doubleSpinBox_epaisseur,
            self.doubleSpinBox_ti,
            self.spinBox_temps,
            self.doubleSpinBox_k,
            self.doubleSpinBox_p,
            self.doubleSpinBox_cp,
            self.doubleSpinBox_h,
            self.doubleSpinBox_dx,
            self.doubleSpinBox_pin
        ]

        for w in widgets:
            w.blockSignals(True)

        # extraire les paramètres
        self.simulation.longueur = params["longueur"]
        self.simulation.largeur = params["largeur"]
        self.simulation.epaisseur = params["epaisseur"]
        self.simulation.T_init = params["T_init"] + 273.15
        self.simulation.t_simulation = params["t_simulation"]
        self.simulation.k = params["k"]
        self.simulation.rho = params["rho"]
        self.simulation.cp = params["cp"]
        self.simulation.h_conv = params["h_conv"]
        self.simulation.dx = params["dx"]
        self.simulation.Pin = params["Pin"]

        # Placer les valeurs sur l'interface
        self.doubleSpinBox_longueur.setValue(self.simulation.longueur * 1000)
        self.doubleSpinBox_largeur.setValue(self.simulation.largeur * 1000)
        self.doubleSpinBox_epaisseur.setValue(self.simulation.epaisseur * 1000)
        self.doubleSpinBox_ti.setValue(self.simulation.T_init - 273.15)
        self.spinBox_temps.setValue(int(self.simulation.t_simulation))
        self.doubleSpinBox_k.setValue(self.simulation.k)
        self.doubleSpinBox_p.setValue(self.simulation.rho)
        self.doubleSpinBox_cp.setValue(self.simulation.cp)
        self.doubleSpinBox_h.setValue(self.simulation.h_conv)
        self.doubleSpinBox_dx.setValue(self.simulation.dx * 1000)
        self.doubleSpinBox_pin.setValue(self.simulation.Pin)

        # Réactiver les signaux
        for w in widgets:
            w.blockSignals(False)
