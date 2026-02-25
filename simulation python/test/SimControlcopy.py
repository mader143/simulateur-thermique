# Classe pour contrôler l'interface graphique
import json
import os
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal, QObject, QTimer
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from SimulationThermiquecopy import SimulationThermique


class MplCanvas(FigureCanvas):
    """A QWidget that contains a Matplotlib figure."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.thermistance = fig.add_subplot(211)
        self.plaque = fig.add_subplot(212, projection='3d')
        super().__init__(fig)
        self.setParent(parent)


class Simulation_Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation

    def run(self):
        """Long-running task."""
        self.simulation.simuler_diffusion()
        self.finished.emit()


class SimControl(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)
        base_path = os.path.join(os.path.dirname(__file__))
        uic.loadUi(os.path.join(base_path, "interface_simulateur.ui"), self)

        self.simulation = SimulationThermique()
        self.simulation.therm_1.connect(self.update_graphs)
        self.simulation.plaque.connect(self.update_plaque)

        self.graphique = MplCanvas(self)
        self.graphique.thermistance.set_title('Température des thermistances')
        self.graphique.plaque.set_title('Température de la plaque')

        self.graph_layout.addWidget(self.graphique)

        self.temps_ecoule = 0
        self.X = None
        self.Y = None
        self.X2 = None
        self.Y2 = None

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
        self.pushButton_start.clicked.connect(self.commencer_simulation)

    def update_timer_label(self):
        self.temps_ecoule += 1
        self.label_temps.setText(f'Temps écoulé : {self.temps_ecoule} secondes')

    def commencer_simulation(self):

        # Recalculer la grille X/Y ici aussi (pas seulement dans load_json)
        # pour que update_plaque fonctionne même sans avoir cliqué load_json
        if self.simulation.longueur and self.simulation.largeur and self.simulation.dx:
            dy = self.simulation.dx
            nx = int(self.simulation.longueur / self.simulation.dx)
            ny = int(self.simulation.largeur / dy)
            x = np.linspace(0, self.simulation.longueur, nx)
            y = np.linspace(0, self.simulation.largeur, ny)
            self.X, self.Y = np.meshgrid(x, y, indexing='ij')
            self.X2, self.Y2 = self.X[::2, ::2], self.Y[::2, ::2]

        self.temps_ecoule = 0
        self.sim_timer = QTimer()
        self.sim_timer.timeout.connect(self.update_timer_label)
        self.sim_timer.start(1000)

        self.graphique.thermistance.cla()
        self.graphique.plaque.cla()

        try:
            self.thread = QThread()
            self.worker = Simulation_Worker(self.simulation)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.sim_timer.stop)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

        except Exception as e:
            print('Erreur:', e)

    def update_graphs(self,obj, t, T1, T2, T3):
        self.graphique.thermistance.cla()
        self.graphique.thermistance.plot(t, T1, color='#4D8DB0', label='Thermistance 1', linewidth=3)
        self.graphique.thermistance.plot(t, T2, color='#B04D6C', label='Thermistance 2', linewidth=3)
        self.graphique.thermistance.plot(t, T3, color='#4DB06B', label='Thermistance 3', linewidth=3)
        self.graphique.thermistance.legend()
        self.graphique.draw()

        print('plotted')

    def update_plaque(self, obj, T):
        self.graphique.plaque.cla()
        self.graphique.plaque.plot_surface(
            self.X, self.Y, T - 273,
            cmap='inferno',
            rstride=1, cstride=1,
            linewidth=0,
            antialiased=False
        )
        self.graphique.draw()
        print('plaque plotted')

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

        dy = self.simulation.dx
        nx, ny = int(self.simulation.longueur / self.simulation.dx), int(self.simulation.largeur / dy)
        x = np.linspace(0, self.simulation.longueur, nx)
        y = np.linspace(0, self.simulation.largeur, ny)
        self.X, self.Y = np.meshgrid(x, y, indexing='ij')

        # Placer les valeurs sur l'interface
        self.doubleSpinBox_longueur.setValue(self.simulation.longueur*1000)
        self.doubleSpinBox_largeur.setValue(self.simulation.largeur*1000)
        self.doubleSpinBox_epaisseur.setValue(self.simulation.epaisseur*1000)
        self.doubleSpinBox_ti.setValue(self.simulation.T_init - 273.15)
        self.spinBox_temps.setValue(int(self.simulation.t_simulation))
        self.doubleSpinBox_k.setValue(self.simulation.k)
        self.doubleSpinBox_p.setValue(self.simulation.rho)
        self.doubleSpinBox_cp.setValue(self.simulation.cp)
        self.doubleSpinBox_h.setValue(self.simulation.h_conv)
        self.doubleSpinBox_dx.setValue(self.simulation.dx*1000)
        self.doubleSpinBox_pin.setValue(self.simulation.Pin)



