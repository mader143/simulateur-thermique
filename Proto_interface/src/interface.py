import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import time
import datetime
import pandas as pd
import serial.tools.list_ports
from tkinter import filedialog
from matplotlib.figure import Figure

class InterfaceProto:
    def __init__(self, root): 
        self.root = root
        self.root.title("Contrôle du prototype")
        
        self.ser = None
        self.running = False
        self.start_time = None

        #timer
        self.timer_start = None
        self.duree_cible = 300
        self.timer_termine = False

        #temp
        self.temperature_voulue = 35
        self.temperature_ambiante = 23.5

        #pid
        self.kp = 10.849
        self.ti = 271
        self.td = 0
 
        self.times = []
        self.t1_data = []
        self.t2_data = []
        self.t3est_data = []
        self.u_data = []
        self.e_data = []
        
        self.create_widgets()
        
    def create_widgets(self):
 
        #config. interface
        BG = FRAME = "#ECE4EA"
        self.root.configure(bg=BG)
        BTN = "#4B0E26"
 
        #template boutons
        button_frame = tk.Frame(self.root, bg=BG)
        button_frame.pack(pady=20)
 
        #démarrer
        demarrer_btn = tk.Button(
            button_frame, text="Démarrer le prototype", command=self.demarrer_proto, font=("Arial", 20),
            fg="#E8E3E5", relief="flat", pady=10, width=25, bg="#174D1C")
        demarrer_btn.pack(padx=10, side=tk.LEFT)
 
        #arrêter
        arreter_btn = tk.Button(
            button_frame, text="Arrêter le prototype", command=self.arreter_proto, font=("Arial", 20),
            fg="#E8E3E5", relief="flat", pady=10, width=20, bg="#832828")
        arreter_btn.pack(padx=10, side=tk.LEFT)
 
        #premiere ligne
        ligne_milieu = tk.Frame(self.root, bg=BG)
        ligne_milieu.pack(fill="x", pady=20)

        #boites
        boite1 = tk.Frame(ligne_milieu, bg=FRAME)
        boite1.pack(padx=100, side='left')
        boite2 = tk.Frame(ligne_milieu, bg=FRAME)
        boite2.pack(padx=75, side='left')

        # config. température
        frame_temp = tk.Frame(boite1, bg=FRAME)
        frame_temp.pack(padx=20, pady=10, side='right')
        frame_temp.grid_rowconfigure(1, minsize=10)
        frame_temp.grid_rowconfigure(3, minsize=10)
 

        # température à atteindre
        tk.Label(frame_temp, text="Température à atteindre (°C):", font=("Arial", 20),
            bg=FRAME).grid(row=0, column=0, padx=5, pady=10, sticky="w")
 
        self.temperature_entry_att = tk.Entry(frame_temp, width=6, bg='#F8F8F8', font=("Arial", 20))
        self.temperature_entry_att.insert(0, self.temperature_voulue)
        self.temperature_entry_att.grid(row=1, column=0, padx=5, pady=10)
 
        apply_btn_att = tk.Button(
            frame_temp, text="Appliquer les données", command=self.envoyer_config_totale, font=("Arial", 20),
            bg=BTN, fg="#F8F8F8", relief="flat", width=20)
        apply_btn_att.grid(row=2, column=0, padx=1, pady=10)

        #changer PID
        frame_pid = tk.Frame(boite1, bg=FRAME)
        frame_pid.grid_rowconfigure(1, minsize=1)
        frame_pid.grid_rowconfigure(3, minsize=1)
        frame_pid.pack(side="left", padx=1)

        self.a0_entry = tk.Entry(frame_pid, width=6, bg='#F8F8F8', font=("Arial", 20))
        self.a0_entry.insert(0, self.kp)
        self.a0_entry.grid(row=2, column=1)

        self.a1_entry = tk.Entry(frame_pid, width=6, bg='#F8F8F8', font=("Arial", 20))
        self.a1_entry.insert(0, self.ti)
        self.a1_entry.grid(row=3, column=1)

        self.a2_entry = tk.Entry(frame_pid, width=6, bg='#F8F8F8', font=("Arial", 20))
        self.a2_entry.insert(0, self.td)
        self.a2_entry.grid(row=4, column=1)

        tk.Label(frame_pid, text="Paramètres PID :", font=("Arial", 20),
            bg=FRAME).grid(row=1, column=0, sticky="e")
        tk.Label(frame_pid, text="K (a0):", font=("Arial", 20),
            bg=FRAME).grid(row=2, column=0, sticky="e")
        tk.Label(frame_pid, text="Ti (a1):", font=("Arial", 20),
            bg=FRAME).grid(row=3, column=0, sticky="e")
        tk.Label(frame_pid, text="Td (a2):", font=("Arial", 20),
            bg=FRAME).grid(row=4, column=0, sticky="e")
 
        #timer
        self.timer_frame = tk.Frame(boite2, bg="#EBCDE2", padx=20, pady=10, relief="flat", width=10)
        self.timer_frame.pack(pady=15, side='left')
        self.label_timer = tk.Label(
            self.timer_frame, 
            text="Test de stabilité : En attente", 
            font=("Arial", 20), 
            bg="#EBCDE2",
            fg="#000000"
        )
        self.label_timer.pack()

        #graphique
        self.t1_data = []
        self.t2_data = []
        self.t3est_data = []
        self.y_data = []

        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax1 = self.fig.add_subplot(121) # 1 row, 2 cols, 1st position
        self.ax2 = self.fig.add_subplot(122) # 1 row, 2 cols, 2nd position
        self.ax1.set_title("Température des thermistances 1 et 2 en temps réel\net température estimée de la thermistance 3", fontsize=12)
        self.ax2.set_title("Commande et erreur en temps réel", fontsize=12)

        #x1
        self.ax1.set_xlabel("Temps (s)", fontsize=10)
        self.ax1.xaxis.set_tick_params(labelsize=7)
        self.ax1.set_xlim(0, 100)
 
        #y1
        self.ax1.yaxis.set_tick_params(labelsize=7)
        self.ax1.set_ylabel("Température (°C)", fontsize=10)
        self.ax1.set_ylim(15, 45)

        #x2
        self.ax2.set_xlabel("Temps (s)", fontsize=10)
        self.ax2.xaxis.set_tick_params(labelsize=7)
        self.ax2.set_xlim(0, 100)
 
        #y2
        self.ax2.yaxis.set_tick_params(labelsize=7)
        self.ax2.set_ylabel("Whatever...", fontsize=10)
        self.ax2.set_ylim(15, 45)
 
        #plot
        self.line  = self.ax1.plot([], [], label="Thermistance 1",    color="#A61F08")[0]
        self.line2 = self.ax1.plot([], [], label="Thermistance 2",    color="#0062DB")[0]
        self.line3 = self.ax1.plot([], [], label="T3 estimée (moy)",  color="#1A8A2E")[0]
        self.line4 = self.ax2.plot([], [], label="Commande u",        color="#E08000")[0]
        self.line5 = self.ax2.plot([], [], label="Erreur",            color="#9B00C2")[0]
        self.ax1.legend(fontsize=7)
        self.ax2.legend(fontsize=7)
        self.fig.tight_layout()
        
        #colour
        self.fig.patch.set_facecolor("#ECE4EA")
        self.ax1.set_facecolor("#F8F8F8")
        self.ax2.set_facecolor("#F8F8F8")
 
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(pady=20)
        self.canvas.draw()
 
        #ramener à température ambiante
        ramener_btn = tk.Button(
            button_frame, text="Ramener à T ambiante", command=self.ramener_ambiante, font=("Arial", 20),
            fg="#E8E3E5", relief="flat", pady=10, width=20, bg=BTN)   
        ramener_btn.pack(padx=10, side=tk.LEFT)

        #enregistrer
        enregistrer_btn = tk.Button(
            button_frame, text="Enregistrer les données", command=self.enregistrer_donnees, font=("Arial", 20),
            fg="#E8E3E5", relief="flat", pady=10, width=20, bg=BTN)
        enregistrer_btn.pack(padx=10, side=tk.LEFT)
 
 
    def envoyer_valeurs_arduino(self):
        '''Envoie les valeurs du PID et la température voulue à l'Arduino'''
        if self.ser and self.ser.is_open:
            message = f"CONFIG:{self.temp},{self.kp},{self.ti},{self.td}\n"
            self.ser.write(message.encode('utf-8'))
            print(f"Envoyé → {message.strip()}")
        else:
            messagebox.showwarning("Erreur", "L'Arduino n'est pas connecté.")
 
 
    # def valider_temp_voulue(self):
    #     try:
    #         value = float(self.temperature_entry_att.get())
    #         if 10 <= value <= 45:
    #             self.temperature_voulue = value
    #             if self.running:
    #                 self.envoyer_valeurs_arduino()
    #             else:
    #                 self.demarrer_proto()
    #         else:
    #             raise ValueError
    #     except ValueError:
    #         messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour la température à atteindre.")

    def envoyer_config_totale(self):
        try:
            temp = float(self.temperature_entry_att.get())
            kp = float(self.a0_entry.get())
            ti = float(self.a1_entry.get())
            td = float(self.a2_entry.get())

            if 10 <= temp <= 45 and type(kp) in [float, int] and type(ti) in [float, int] and type(td) in [float, int]:
                self.temperature_voulue = temp
                self.temp = temp
                self.kp = kp
                self.ti = ti
                self.td = td

                if self.running:
                    self.envoyer_valeurs_arduino()
                else:
                    self.demarrer_proto()
            else:
                raise ValueError
                
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des nombres valides dans tous les champs.")
        except serial.SerialException as e:
            messagebox.showerror("Erreur de connexion", f"Impossible de trouver l'Arduino : {e}")
        except Exception as e:
            messagebox.showerror("Erreur Inattendue", f"Il y a un problème : {e}")
 
    def trouver_port_arduino(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "USB Serial" in port.description:
                print(f"Arduino trouvé sur le port : {port.device}")
                return port.device
            
        raise serial.SerialException("Arduino introuvable! Vérifiez le branchement USB.")
 
    def demarrer_proto(self):
        try:
            port_auto = self.trouver_port_arduino()
            
            if not self.running:
                    self.ser = serial.Serial(port_auto, 9600, timeout=1) 
                    time.sleep(2)
                
                    self.running = True
                    self.start_time = time.time()
                    
                    self.update_data()
                    
                    print("Communication établie. Réception des données.")

        except serial.SerialException as e:
            messagebox.showerror("Erreur de connexion", f"{e}")
            
        except Exception as e:
            messagebox.showerror("Erreur critique", f"Vérifiez le port USB : {e}")
 
    def arreter_proto(self):
        self.running = False
        try:
            cmd = f"CONFIG:{self.temperature_ambiante},{self.kp},{self.ti},{self.td}\n"
            self.ser.write(cmd.encode('utf-8'))
        except Exception as e:
            messagebox.showerror("Erreur", f"Vérifiez le port USB : {e}") 
        print(f"Commande envoyée pour ramener à T ambiante")
        
        if self.ser:
            self.ser.close()
        print("Prototype arrêté")

 
    def update_data(self):
        if self.running and self.ser:
            try:
                line = self.ser.readline().decode('utf-8').strip()  # bloque jusqu'à timeout=1s

                if line and not line.startswith("temps") and line != "FIN":
                    values = line.split(',')
                    if len(values) == 9:

                        t1  = float(values[1])
                        t2  = float(values[2])
                        t3  = float(values[6])
                        e   = float(values[7])
                        u   = float(values[8])
                        current_time = time.time() - self.start_time

                        self.times.append(current_time)
                        self.t1_data.append(t1)
                        self.t2_data.append(t2)
                        self.t3est_data.append(t3)
                        self.u_data.append(u)
                        self.e_data.append(e)

                        self.line.set_data(self.times, self.t1_data)
                        self.line2.set_data(self.times, self.t2_data)
                        self.line3.set_data(self.times, self.t3est_data)
                        self.line4.set_data(self.times, self.u_data)
                        self.line5.set_data(self.times, self.e_data)

                        #commencer timer
                        self.timer()

                        if current_time > 100:
                            self.ax.set_xlim(0, max(current_time, 100))

                        toutes_temps1 = self.t1_data + self.t2_data + self.t3est_data
                        y_min1 = min(toutes_temps1)
                        y_max1 = max(toutes_temps1)
                        marge1 = (y_max1 - y_min1) * 0.1 or 1

                        toutes_temps2 = self.u_data + self.e_data
                        y_min2 = min(toutes_temps2)
                        y_max2 = max(toutes_temps2)
                        marge2 = (y_max1 - y_min1) * 0.1 or 1

                        self.ax1.set_ylim(y_min1 - marge1, y_max1 + marge1)
                        self.ax2.set_ylim(y_min2 - marge2, y_max2 + marge2)
                        self.canvas.draw()

            except Exception as ex:
                print(f"Read error: {ex}")

        if self.running:
            self.root.after(100, self.update_data)
        
    
    def enregistrer_donnees(self):
        if not self.times:
            messagebox.showwarning("Avertissement", "Aucune donnée à enregistrer.")
            return
 
        nom_defaut = f"donnees_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        chemin = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")],
            initialfile=nom_defaut,
            title="Enregistrer les données"
        )
        
        if not chemin:
            return
 
        df = pd.DataFrame({
            "Temps (s)": self.times,
            "Thermistance 1 - T1 (°C)": self.t1_data,
            "Thermistance 2 - T2 (°C)": self.t2_data,
            "Thermistance 3 estimée - T3_moy (°C)": self.t3est_data,
            "Erreur (°C)": self.e_data,
            "Commande - u": self.u_data
        })
 
        df.to_csv(chemin, index=False)
        messagebox.showinfo("Succès", f"Données enregistrées dans :\n{chemin}")
 
    def ramener_ambiante(self):
        if not self.running or not self.ser or not self.ser.is_open:
            messagebox.showwarning("Avertissement", "Le prototype n'est pas démarré.")
            return
        try:
            cmd = f"SET_CONSIGNE:{self.temperature_ambiante}\n"
            self.ser.write(cmd.encode('utf-8'))
        except Exception as e:
            messagebox.showerror("Erreur", f"Vérifiez le port USB : {e}") 
        print(f"Commande envoyée pour ramener à T ambiante")

    def timer(self):

        if self.t3est_data[-1] >= self.temperature_voulue - (self.temperature_voulue - self.temperature_ambiante)*0.05 and self.t3est_data[-1] <= self.temperature_voulue + (self.temperature_voulue - self.temperature_ambiante)*0.05:
            if self.timer_termine:
                return
            
            if self.timer_start is None:
                self.timer_start = time.time()
                self.label_timer.config(text="Test de stabilité : 00:00")
                self.timer_frame.config(bg="#67EB5B")

            else:
                #calculer temps écoulé
                ecoule = time.time() - self.timer_start
                restant = max(0, self.duree_cible - ecoule)

                #minutes, secondes
                mins, secs = divmod(int(restant), 60)
                self.label_timer.config(text=f"Test de stabilité : {mins:02d}:{secs:02d}")
                self.timer_frame.config(bg="#67EB5B")

                #quand ça atteint 5min
                if restant <= 0:
                    self.timer_termine = True
                    self.label_timer.config(text="CIBLE ATTEINTE (5 min) : Système stable")
                    self.timer_frame.config(bg="#67EB5B")
        else:
            # sortie du corridor : on reset le timer seulement si on n'avait pas fini
            if not self.timer_termine:
                self.timer_start = None
                self.label_timer.config(text="Hors corridor")
                self.timer_frame.config(bg="#EBCDE2")

    def indicateur_stabilite(self):
        pass


def main():
    root = tk.Tk()
    app = InterfaceProto(root)
    root.mainloop()
 
if __name__ == "__main__":
    main()

#JSON?
#mettre a0, a1, a2 custom dans code C++
#charger des valeurs de pid dans code C++, et donc changer les a

#reset graphique quand on clique sur demarrer