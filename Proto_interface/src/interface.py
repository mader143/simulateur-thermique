import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import time
import datetime
import pandas as pd
import serial.tools.list_ports

class InterfaceProto:
    def __init__(self, root): 
        self.root = root
        self.root.title("Contrôle du prototype")
        
        #essai
        self.ser = None
        self.running = False
        self.start_time = None

        self.temperature_voulue = 35
        self.temperature_ambiante = 21

        self.times = []
        self.t2_data = []
        self.t3_data = []
        #essai
        
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

        # config. température
        frame_temp = tk.Frame(self.root, bg=FRAME)
        frame_temp.pack(pady=25, padx=20)
        frame_temp.grid_rowconfigure(1, minsize=60)
        frame_temp.grid_rowconfigure(3, minsize=60)

        # température ambiante
        tk.Label(frame_temp, text="Température ambiante (°C):", font=("Arial", 20),
            bg=FRAME).grid(row=1, column=0, padx=10, pady=15, sticky="w")

        self.temperature_entry_amb = tk.Entry(frame_temp, width=10, bg='#F8F8F8', font=("Arial", 20))
        self.temperature_entry_amb.insert(0, self.temperature_ambiante)
        self.temperature_entry_amb.grid(row=1, column=1, padx=5, pady=15)

        apply_btn_amb = tk.Button(
            frame_temp, text="Appliquer", command=self.valider_temp_ambiante, font=("Arial", 20),
            bg=BTN, fg="#E8E3E5", relief="flat", width=10)
        apply_btn_amb.grid(row=1, column=2, padx=5, pady=15)

        # température à atteindre
        tk.Label(frame_temp, text="Température à atteindre (°C):", font=("Arial", 20),
            bg=FRAME).grid(row=3, column=0, padx=10, pady=15, sticky="w")

        self.temperature_entry_att = tk.Entry(frame_temp, width=10, bg='#F8F8F8', font=("Arial", 20))
        self.temperature_entry_att.insert(0, self.temperature_voulue)
        self.temperature_entry_att.grid(row=3, column=1, padx=5, pady=15)

        apply_btn_att = tk.Button(
            frame_temp, text="Appliquer", command=self.valider_temp_voulue, font=("Arial", 20),
            bg=BTN, fg="#F8F8F8", relief="flat", width=10)
        apply_btn_att.grid(row=3, column=2, padx=5, pady=15)

        #graphique
        self.t1_data = []
        self.t2_data = []
        self.y_data = []
        self.fig, self.ax = plt.subplots(figsize=(15, 10))
        self.ax.set_title("Température des thermistances 1 et 2 en temps réel", fontsize=20)
        
        #x
        self.ax.set_xlabel("Temps (s)", fontsize=18)
        self.ax.xaxis.set_tick_params(labelsize=18)
        self.ax.set_xlim(0, 100)

        #y
        self.ax.yaxis.set_tick_params(labelsize=18)
        self.ax.set_ylabel("Température (°C)", fontsize=18)
        self.ax.set_ylim(15, 45)

        #plot
        self.line = self.ax.plot([], [], label="Thermistance 1", color="#A61F08")[0]
        self.line2 = self.ax.plot([], [], label="Thermistance 2", color="#0062DB")[0]
        self.ax.legend(fontsize=18)
        
        #colour
        self.fig.patch.set_facecolor("#ECE4EA")
        self.ax.set_facecolor("#F8F8F8")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(pady=20)
        self.canvas.draw()
        
        #enregistrer
        enregistrer_btn = tk.Button(
            button_frame, text="Enregistrer les données", command=self.demarrer_proto, font=("Arial", 20),
            fg="#E8E3E5", relief="flat", pady=10, width=20, bg=BTN)
        enregistrer_btn.pack(padx=10, side=tk.LEFT)

    def valider_temp_ambiante(self):
        try:
            value = float(self.temperature_entry_amb.get())
            if -30 <= value <= 60:
                self.temperature_ambiante = value
                if isinstance(value, float): #jai changé la syntaxe etait pas bonne je crois
                    self.demarrer_proto()
            
            else:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour la température ambiante.")

    def valider_temp_voulue(self):
        try:
            value = float(self.temperature_entry_att.get())
            if 10 <= value <= 45:
                self.temperature_voulue = value
                if isinstance(value, (int, float)): #same here
                    self.demarrer_proto()
            else:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour la température à atteindre.")

    def trouver_port_arduino(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # On cherche "Arduino", "USB Serial", ou "CH340" (chipset commun)
            if "Arduino" in port.description or "USB Serial" in port.description:
                print(f"Arduino trouvé sur le port : {port.device}")
                return port.device
        return None

    def demarrer_proto(self):
        # chercher le port
        port_auto = self.trouver_port_arduino()
        
        if port_auto is None:
            messagebox.showerror("Erreur", "Arduino introuvable. Vérifiez le branchement USB.")
            return
        
        if not self.running:
            try:
                #de ce que je comprends ça ouvre la connection avec arduino, jai mis que ca trouve le port automatiquement
                self.ser = serial.Serial(port_auto, 9600, timeout=1) 
                time.sleep(2)
            
                self.running = True
                self.start_time = time.time()
                
                self.update_data() #ca commence la boucle qui prends les données d'arduino (le port) et ca va
                #les mettres dans le graphique
                
                print("Communication établie. Réception des données T2 et T3??") 
            except Exception as e:
                messagebox.showerror("Erreur", f"Vérifiez le port USB : {e}")

        print(f"Température Ambiante: {self.temperature_ambiante} °C")
        print(f"Température à atteindre: {self.temperature_voulue} °C") 

    def arreter_proto(self):
        self.running = False
        if self.ser:
            self.ser.close()
        print("Prototype arrêté")

    def update_data(self):
        if self.running and self.ser and self.ser.in_waiting > 0:
            try:
                # lis la ligne d'arduino, ça faut le changer ca depend de comment on le définit dans le code arduino
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    values = line.split(',')
                    if len(values) == 4:
                        t2 = float(values[1])
                        t3 = float(values[2])
                        current_time = time.time() - self.start_time

                        self.times.append(current_time)
                        self.t2_data.append(t2)
                        self.t3_data.append(t3)

                        self.line.set_data(self.times, self.t2_data)
                        self.line2.set_data(self.times, self.t3_data)
                        
                        if current_time > 100:
                            self.ax.set_xlim(current_time - 100, current_time)
                        
                        self.canvas.draw()
            except Exception as e:
                print(f"Read error: {e}")

        if self.running:
            self.root.after(100, self.update_data)
    


def main():
    root = tk.Tk()
    app = InterfaceProto(root)
    root.mainloop()

if __name__ == "__main__":
    main()
