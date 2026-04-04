# Classe pour contrôler l'interface graphique
import json
import os
import numpy as np
import time as time

from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog
from PyQt5 import uic
import pyqtgraph as pqg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from SimulationThermique import SimulationThermique



class SimControl(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        base_path = os.path.join(os.path.dirname(__file__))
        uic.loadUi(os.path.join(base_path, "interface_simulateur.ui"), self)

        self.simulation = SimulationThermique()
        self.simulation.therm_1.connect(self.update_graphs)
        self.simulation.plaque.connect(self.update_plaque)
        self.simulation.progress.connect(self.update_status)


        class MplCanvas(FigureCanvas):
            """A QWidget that contains a Matplotlib figure."""

            def __init__(self, parent=None, width=5, height=4, dpi=100):
                fig = Figure(figsize=(width, height), dpi=dpi)
                fig.tight_layout(h_pad=200)
                self.thermistance = fig.add_subplot(121)
                self.plaque = fig.add_subplot(122, projection='3d')
                self.thermistance.set_xlabel('Temps [s]')
                self.thermistance.set_ylabel('Température [°C]')
                self.plaque.set_xlabel('x [m]')
                self.plaque.set_ylabel('y [m]')
                self.plaque.set_zlabel('T [°C]')



                super().__init__(fig)
                self.setParent(parent)

        self.graphique = MplCanvas(self)
        self.graphique.thermistance.set_title('Température des thermistances')
        self.graphique.plaque.set_title('Température de la plaque')

        self.graph_layout.addWidget(self.graphique)
        self.c_bar = None
        self.stop_simulation = False
        self.folder = ''
        self.time_array = None
        self.T1_array = None
        self.T2_array = None
        self.T3_array = None
        self.T_plaque_array = []
        self.start = None

        # Initialiser les boutons ---------------------------------------------------------------------------

        # Mettre les bonnes positions des thermistances
        self.doubleSpinBox_therm1_x.setValue(self.simulation.therm1_x*1000)
        self.doubleSpinBox_therm1_y.setValue(self.simulation.therm1_y * 1000)
        self.doubleSpinBox_therm2_x.setValue(self.simulation.therm2_x * 1000)
        self.doubleSpinBox_therm2_y.setValue(self.simulation.therm2_y * 1000)
        self.doubleSpinBox_therm3_x.setValue(self.simulation.therm3_x * 1000)
        self.doubleSpinBox_therm3_y.setValue(self.simulation.therm3_y * 1000)
        self.doubleSpinBox_act_x_m.setValue(self.simulation.act_x_m * 1000)
        self.doubleSpinBox_act_y_m.setValue(self.simulation.act_y_m * 1000)
        self.doubleSpinBox_perturb_x.setValue(self.simulation.perturb_x * 1000)
        self.doubleSpinBox_perturb_y.setValue(self.simulation.perturb_y * 1000)

        # Changer les positions des thermistances si les valeurs changent
        self.doubleSpinBox_therm1_x.valueChanged.connect(
            lambda: setattr(self.simulation, 'therm1_x', self.doubleSpinBox_therm1_x.value() / 1000))
        self.doubleSpinBox_therm1_y.valueChanged.connect(
            lambda: setattr(self.simulation, 'therm1_y', self.doubleSpinBox_therm1_y.value() / 1000))
        self.doubleSpinBox_therm2_x.valueChanged.connect(
            lambda: setattr(self.simulation, 'therm2_x', self.doubleSpinBox_therm2_x.value() / 1000))
        self.doubleSpinBox_therm2_y.valueChanged.connect(
            lambda: setattr(self.simulation, 'therm2_y', self.doubleSpinBox_therm2_y.value() / 1000))
        self.doubleSpinBox_therm3_x.valueChanged.connect(
            lambda: setattr(self.simulation, 'therm3_x', self.doubleSpinBox_therm3_x.value() / 1000))
        self.doubleSpinBox_therm3_y.valueChanged.connect(
            lambda: setattr(self.simulation, 'therm3_y', self.doubleSpinBox_therm3_y.value() / 1000))
        self.doubleSpinBox_act_x_m.valueChanged.connect(
            lambda: setattr(self.simulation, 'act_x_m', self.doubleSpinBox_act_x_m.value() / 1000))
        self.doubleSpinBox_act_y_m.valueChanged.connect(
            lambda: setattr(self.simulation, 'act_y_m', self.doubleSpinBox_act_y_m.value() / 1000))
        self.doubleSpinBox_perturb_x.valueChanged.connect(
            lambda: setattr(self.simulation, 'perturb_x', self.doubleSpinBox_perturb_x.value() / 1000))
        self.doubleSpinBox_perturb_y.valueChanged.connect(
            lambda: setattr(self.simulation, 'perturb_y', self.doubleSpinBox_perturb_y.value() / 1000))

        # Pour charger les paramètres depuis le fichier json
        self.pushButton_load_json.clicked.connect(self.load_json)

        # Pour changer les paramètres de la simulation depuis les boutons
        self.doubleSpinBox_longueur.valueChanged.connect(
            lambda : setattr(self.simulation, 'longueur', self.doubleSpinBox_longueur.value()/1000))
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
        self.doubleSpinBox_perturb_W.valueChanged.connect(
            lambda: setattr(self.simulation, 'perturb_W', self.doubleSpinBox_perturb_W.value()))
        self.doubleSpinBox_t_perturb.valueChanged.connect(
            lambda: setattr(self.simulation, 't_perturb', self.doubleSpinBox_t_perturb.value()))
        self.doubleSpinBox_t_start_act.valueChanged.connect(
            lambda: setattr(self.simulation, 't_start_act', self.doubleSpinBox_t_start_act.value()))
        self.doubleSpinBox_t_stop_act.valueChanged.connect(
            lambda: setattr(self.simulation, 't_stop_act', self.doubleSpinBox_t_stop_act.value()))
        
        self.doubleSpinBox_perturb_W.setMinimum(-1000.0)
        self.doubleSpinBox_perturb_W.setMaximum(1000.0)

        # Lancer la simulation thermique
        self.pushButton_start.clicked.connect(self.commencer_simulation)

        # Arrêter la simulation thermique
        self.pushButton_stop.clicked.connect(self.arreter_simulation)

        # Sauvegarder les nouveaux paramètres dans le json
        self.pushButton_save_json.clicked.connect(self.save_json)

        # Choisir la destination du fichier de résultats
        self.pushButton_folder.clicked.connect(self.choisir_folder)

        # Sauvegarder les résultats de la simulation
        self.pushButton_save_results.clicked.connect(self.sauvegarder_resultats)






    def sauvegarder_resultats(self):

        self.filename = self.plainTextEdit_filename.toPlainText()

        if self.filename == '':
            QMessageBox.warning(
                self,
                "Attention",
                "Nom du fichier manquant",
                buttons=QMessageBox.StandardButton.Ok
            )
            return False

        if self.folder == '':
            QMessageBox.warning(
                self,
                "Attention",
                "Dossier manquant",
                buttons=QMessageBox.StandardButton.Ok
            )
            return False

        filepath = self.folder + '/' + self.filename
        try:
            if self.checkBox_figures.isChecked():
                self.graphique.figure.savefig(f'{filepath}_figures.png')


            if self.checkBox_thermistance.isChecked():
                therm_data = np.stack((self.time_array, self.T1_array, self.T2_array, self.T3_array), axis=1)
                np.savetxt(f'{filepath}_thermistances.txt', therm_data,
                           fmt="%.5f",  # 5 decimal places
                           delimiter=",",  # comma-separated
                           header="Time,T1,T2,T3",  # header row
                           comments="")  # no '#' before header

            if self.checkBox_plaque.isChecked():
                with open(f'{filepath}_plaque.txt', 'w') as f:
                    for T_plaque_array, time_sim in self.T_plaque_array:
                        print(time_sim)
                        print(T_plaque_array)
                        f.write(f'\nTemps : {round(time_sim, 2)}\n')
                        plaque_data = np.stack([self.X, self.Y, T_plaque_array - 273.15], axis=-1).reshape(-1, 3)
                        np.savetxt(f, plaque_data,
                               fmt="%.6f",  # 6 decimal places
                               delimiter=",",  # comma-separated
                               header="X,Y,T",  # header row
                               comments="")  # no '#' before header

            self.label_saving_status.setText('Fichiers sauvegardés avec succès!')

        except Exception as e:
            print(e)
            self.label_saving_status.setText('Erreur dans la sauvegarde des fichiers')











    def choisir_folder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontResolveSymlinks
        options |= QFileDialog.ShowDirsOnly
        folder = QFileDialog.getExistingDirectory(self, 'Choose Directory', '', options)

        if folder == '':
            self.label_folder_name.setText('Aucun dossier choisi')
            return True

        else:  # Directory chosen
            self.folder = folder
            self.label_folder_name.setText(self.folder)
            return True




    def save_json(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "params_sim.json")

        params = {"longueur": self.simulation.longueur, "largeur": self.simulation.largeur,
                  "epaisseur": self.simulation.epaisseur, "T_init": self.simulation.T_init - 273.15,
                  "t_simulation": self.simulation.t_simulation, "k" : self.simulation.k, "rho" : self.simulation.rho,
                  "cp" : self.simulation.cp, "h_conv": self.simulation.h_conv, "dx" : self.simulation.dx,
                  "Pin" : self.simulation.Pin, "perturb_W": self.simulation.perturb_W, 
                  "perturb_x": self.simulation.perturb_x,
                  "perturb_y": self.simulation.perturb_y,
                  "t_perturb": self.simulation.t_perturb,
                  "t_start_act": self.simulation.t_start_act,
                  "t_stop_act": self.simulation.t_stop_act}

        with open(json_path, "w") as file:
            json.dump(params, file)





    def arreter_simulation(self):
        self.stop_simulation = True
        self.pushButton_stop.setDisabled(True)

    def update_timer_label(self):
        self.end = time.time()
        self.elapsed = self.end - self.start
        self.label_temps.setText(f"Temps écoulé : {round(self.elapsed)} secondes")

    def commencer_simulation(self):

        try:
            self.start = time.time()

            self.pushButton_stop.setDisabled(False)
            self.label_status.setText('Statut : Simulation débutée')
            self.sim_timer = QTimer()
            self.sim_timer.timeout.connect(self.update_timer_label)
            self.sim_timer.start(1000)

            self.graphique.thermistance.cla()
            self.graphique.plaque.cla()
            self.T_plaque_array = []
            self.simulation.init_simulation()

            dy = self.simulation.dx
            nx, ny = self.simulation.nx, self.simulation.ny
            x = np.linspace(0, self.simulation.longueur, nx)
            y = np.linspace(0, self.simulation.largeur, ny)
            self.X, self.Y = np.meshgrid(x, y, indexing='ij')
        
            self.simulation_runner = QTimer()
            self.simulation.init_simulation()
            self.simulation_runner.timeout.connect(self.step_simulation)
            self.simulation_runner.start(0)

        except TypeError as e0:
            self.label_status.setText('Statut :')
            self.sim_timer.stop()
            self.sim_timer.disconnect()
            self.simulation_runner.stop()
            self.pushButton_stop.setDisabled(True)
            QMessageBox.warning(
                self,
                "Attention",
                "Paramètres de simulation invalides",
                buttons=QMessageBox.StandardButton.Ok
            )


        except Exception as e:
            print('erreur :', e, type(e))


    def step_simulation(self):
        BATCH_SIZE = 5000  # nombre d'itérations par tick

        terminé = self.simulation.step_batch(BATCH_SIZE)

        if self.stop_simulation:
            self.sim_timer.stop()
            self.sim_timer.disconnect()
            self.simulation_runner.stop()
            self.simulation_runner.disconnect()
            self.stop_simulation = False
            self.label_status.setText('Statut : Simulation arrêtée manuellement')

        if terminé:
            self.label_status.setText('Statut : Simulation terminée')
            self.sim_timer.stop()
            self.sim_timer.disconnect()
            self.simulation_runner.stop()
            self.simulation_runner.disconnect()
            self.pushButton_stop.setDisabled(True)




    def update_graphs(self,obj, t, T1, T2, T3):
        self.graphique.thermistance.cla()
        self.graphique.thermistance.set_xlabel('Temps [s]')
        self.graphique.thermistance.set_ylabel('Température [°C]')
        self.time_array, self.T1_array, self.T2_array, self.T3_array = t, T1, T2, T3
        self.graphique.thermistance.set_title('Température des thermistances')
        self.graphique.thermistance.plot(t, T1, color='#4D8DB0', label='Thermistance 1', linewidth=3)
        self.graphique.thermistance.plot(t, T2, color='#B04D6C', label='Thermistance 2', linewidth=3)
        self.graphique.thermistance.plot(t, T3, color='#4DB06B', label='Thermistance 3', linewidth=3)
        self.graphique.thermistance.legend()
        self.graphique.draw()
        self.graphique.flush_events()


    def update_plaque(self, obj, T, sim_time):
        self.graphique.plaque.cla()
        self.graphique.plaque.set_xlabel('x [m]')
        self.graphique.plaque.set_ylabel('y [m]')
        self.graphique.plaque.set_zlabel('T [°C]')

        self.T_plaque_array.append([T, sim_time])
        self.graphique.plaque.set_title('Température de la plaque')
        plaque_data = self.graphique.plaque.plot_surface(
            self.X, self.Y, T - 273,
            cmap='inferno',
            rstride=1, cstride=1,
            linewidth=0,
            antialiased=False
        )
        if self.c_bar:
            self.c_bar.update_normal(plaque_data)
        else:
            self.c_bar = self.graphique.figure.colorbar(plaque_data, ax=self.graphique.plaque)
        self.graphique.draw()
        self.graphique.flush_events()

    def update_status(self, obj, progress):
        self.label_status.setText(f'Statut : {round(progress)} %')


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
        self.simulation.perturb_W = params["perturb_W"]
        self.simulation.t_perturb = params["t_perturb"]
        self.simulation.t_start_act = params["t_start_act"]
        self.simulation.t_stop_act = params["t_stop_act"]

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
        self.doubleSpinBox_perturb_W.setValue(self.simulation.perturb_W)
        self.doubleSpinBox_t_perturb.setValue(self.simulation.t_perturb)
        self.doubleSpinBox_t_start_act.setValue(self.simulation.t_start_act)
        self.doubleSpinBox_t_stop_act.setValue(self.simulation.t_stop_act)



