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

        # timer
        self.timer_start = None
        self.duree_cible = 300
        self.timer_termine = False

        # temp
        self.temperature_voulue = 30
        self.temperature_ambiante = 23.5

        # pid
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

    # ══════════════════════════════════════════════════════════════════════════
    # INTERFACE
    # ══════════════════════════════════════════════════════════════════════════

    def create_widgets(self):
        # ── Palette ───────────────────────────────────────────────────────────
        BG       = "#F5EFF3"
        CARD     = "#FFFFFF"
        SURFACE  = "#F5EFF3"
        WINE     = "#4B0E26"
        MUTED    = "#7A5568"
        TEXT     = "#1A0A10"
        BORDER   = "#D9C8D4"
        AMBER_BG = "#FAEEDA"
        AMBER_FG = "#854F0B"

        self.root.configure(bg=BG)

        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=14, pady=14)

        # ── En-tête ───────────────────────────────────────────────────────────
        header = tk.Frame(outer, bg=CARD, highlightthickness=1,
                          highlightbackground=BORDER)
        header.pack(fill="x", pady=(0, 8))

        left_h = tk.Frame(header, bg=CARD)
        left_h.pack(side="left", padx=14, pady=10)

        dot = tk.Canvas(left_h, width=28, height=28, bg=CARD,
                        highlightthickness=0)
        dot.create_oval(0, 0, 28, 28, fill=WINE, outline="")
        dot.pack(side="left", padx=(0, 10))

        txt_h = tk.Frame(left_h, bg=CARD)
        txt_h.pack(side="left")
        tk.Label(txt_h, text="Contrôleur PID — Prototype thermique",
                 font=("Arial", 13, "bold"), bg=CARD, fg=TEXT).pack(anchor="w")
        tk.Label(txt_h, text="Régulation en temps réel · Interface de commande",
                 font=("Arial", 10), bg=CARD, fg=MUTED).pack(anchor="w")

        right_h = tk.Frame(header, bg=CARD)
        right_h.pack(side="right", padx=14)
        self.status_label = tk.Label(
            right_h, text="● En attente",
            font=("Courier", 10), bg="#EAF3DE", fg="#3B6D11",
            relief="flat", padx=10, pady=4
        )
        self.status_label.pack()

        # ── Boutons d'action ──────────────────────────────────────────────────
        btn_row = tk.Frame(outer, bg=BG)
        btn_row.pack(fill="x", pady=(0, 8))
        for i in range(4):
            btn_row.grid_columnconfigure(i, weight=1)

        btns = [
            ("Démarrer le prototype",   "#174D1C", "#E8F5EA", self.demarrer_proto),
            ("Arrêter le prototype",    "#832828", "#FAE8E8", self.arreter_proto),
            ("Ramener à T ambiante",    WINE,      "#F9EFF4", self.ramener_ambiante),
            ("Enregistrer les données", "#1A3A5C", "#E6F1FB", self.enregistrer_donnees),
        ]
        for i, (txt, bg, fg, cmd) in enumerate(btns):
            tk.Button(
                btn_row, text=txt, command=cmd,
                font=("Arial", 13, "bold"), bg=bg, fg=fg,
                relief="flat", pady=10, cursor="hand2",
                activebackground=bg, activeforeground=fg
            ).grid(row=0, column=i, padx=5, sticky="ew")

        # ── Métriques temps réel ──────────────────────────────────────────────
        metrics_row = tk.Frame(outer, bg=BG)
        metrics_row.pack(fill="x", pady=(0, 8))
        for i in range(4):
            metrics_row.grid_columnconfigure(i, weight=1)

        metric_defs = [
            ("T1 — Thermistance 1", "metric_t1"),
            ("T2 — Thermistance 2", "metric_t2"),
            ("T3 — Estimée",        "metric_t3"),
            ("Erreur courante",     "metric_err"),
        ]
        for i, (lbl, attr) in enumerate(metric_defs):
            card = tk.Frame(metrics_row, bg=CARD, highlightthickness=1,
                            highlightbackground=BORDER)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            tk.Label(card, text=lbl, font=("Arial", 10), bg=CARD,
                     fg=MUTED).pack(anchor="w", padx=12, pady=(8, 0))
            var = tk.StringVar(value="— °C")
            tk.Label(card, textvariable=var,
                     font=("Courier", 17, "bold"), bg=CARD,
                     fg=TEXT).pack(anchor="w", padx=12, pady=(2, 8))
            setattr(self, attr, var)

        # ── Corps : gauche + droite ───────────────────────────────────────────
        body = tk.Frame(outer, bg=BG)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0, minsize=260)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # -- Colonne gauche ----------------------------------------------------
        left_col = tk.Frame(body, bg=BG)
        left_col.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        def section_title(parent, text):
            f = tk.Frame(parent, bg=BG)
            f.pack(fill="x", pady=(6, 2))
            tk.Frame(f, bg=WINE, width=3, height=13).pack(side="left",
                                                            padx=(0, 6))
            tk.Label(f, text=text.upper(), font=("Arial", 9, "bold"),
                     bg=BG, fg=WINE).pack(side="left")

        # Carte consigne
        section_title(left_col, "Consigne")
        consigne_card = tk.Frame(left_col, bg=CARD, highlightthickness=1,
                                 highlightbackground=BORDER)
        consigne_card.pack(fill="x", pady=(0, 8))
        consigne_card.grid_columnconfigure(0, weight=1)
        consigne_card.grid_columnconfigure(1, weight=0)

        tk.Label(consigne_card, text="Température à atteindre (°C) :",
                 font=("Arial", 11), bg=CARD,
                 fg=MUTED).grid(row=0, column=0, sticky="w",
                                padx=12, pady=(10, 4))
        self.temperature_entry_att = tk.Entry(
            consigne_card, width=7, font=("Courier", 12),
            bg=SURFACE, fg=TEXT, relief="flat",
            highlightthickness=1, highlightbackground=BORDER, justify="right"
        )
        self.temperature_entry_att.insert(0, self.temperature_voulue)
        self.temperature_entry_att.grid(row=0, column=1, padx=12, pady=(10, 4))

        apply_btn = tk.Button(
            consigne_card, text="Appliquer les données",
            command=self.envoyer_config_totale,
            font=("Arial", 11), bg=CARD, fg=WINE,
            relief="flat", cursor="hand2", pady=7,
            highlightthickness=1, highlightbackground=WINE,
            activebackground=WINE, activeforeground=CARD
        )
        apply_btn.grid(row=1, column=0, columnspan=2,
                       padx=12, pady=(4, 12), sticky="ew")

        # Carte PID
        section_title(left_col, "Paramètres PID")
        pid_card = tk.Frame(left_col, bg=CARD, highlightthickness=1,
                            highlightbackground=BORDER)
        pid_card.pack(fill="x", pady=(0, 8))
        pid_card.grid_columnconfigure(0, weight=1)
        pid_card.grid_columnconfigure(1, weight=0)

        pid_fields = [
            ("K  (a0) — gain proportionnel", str(self.kp), "a0_entry"),
            ("Ti (a1) — temps intégral",     str(self.ti), "a1_entry"),
            ("Td (a2) — temps dérivé",       str(self.td), "a2_entry"),
        ]
        for r, (lbl, val, attr) in enumerate(pid_fields):
            tk.Label(pid_card, text=lbl, font=("Arial", 11),
                     bg=CARD, fg=MUTED).grid(row=r, column=0, sticky="w",
                                              padx=12, pady=6)
            entry = tk.Entry(
                pid_card, width=7, font=("Courier", 12),
                bg=SURFACE, fg=TEXT, relief="flat",
                highlightthickness=1, highlightbackground=BORDER,
                justify="right"
            )
            entry.insert(0, val)
            entry.grid(row=r, column=1, padx=12, pady=6)
            setattr(self, attr, entry)

        tk.Label(pid_card, bg=CARD, height=1).grid(
            row=len(pid_fields), column=0)

        # Carte test de stabilité
        section_title(left_col, "Test de stabilité")
        self.timer_frame = tk.Frame(left_col, bg=CARD, highlightthickness=1,
                                    highlightbackground=BORDER)
        self.timer_frame.pack(fill="x")

        tk.Label(self.timer_frame, text="〰  Signal de stabilité",
                 font=("Arial", 12, "bold"), bg=CARD,
                 fg=TEXT).pack(pady=(14, 2))
        self.label_timer = tk.Label(
            self.timer_frame, text="En attente d'un signal actif",
            font=("Arial", 10), bg=CARD, fg=MUTED
        )
        self.label_timer.pack()
        self.stabilite_btn = tk.Button(
            self.timer_frame, text="Lancer le test de stabilité",
            command=self.indicateur_stabilite,
            font=("Arial", 11), bg=AMBER_BG, fg=AMBER_FG,
            relief="flat", cursor="hand2", pady=8,
            activebackground="#FAC775", activeforeground=AMBER_FG
        )
        self.stabilite_btn.pack(fill="x", padx=12, pady=12)

        # -- Colonne droite : graphiques empilés -------------------------------
        charts_card = tk.Frame(body, bg=CARD, highlightthickness=1,
                               highlightbackground=BORDER)
        charts_card.grid(row=0, column=1, sticky="nsew")

        title_bar = tk.Frame(charts_card, bg=CARD)
        title_bar.pack(fill="x", padx=14, pady=(10, 4))
        tk.Frame(title_bar, bg=WINE, width=3, height=13).pack(
            side="left", padx=(0, 6))
        tk.Label(title_bar, text="VISUALISATION TEMPS RÉEL",
                 font=("Arial", 9, "bold"), bg=CARD,
                 fg=WINE).pack(side="left")

        self.fig = Figure(figsize=(10, 7), dpi=100)
        self.fig.patch.set_facecolor(CARD)
        self.fig.subplots_adjust(left=0.07, right=0.97,
                                 top=0.93, bottom=0.08, hspace=0.45)

        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)

        for ax, title in [
            (self.ax1, "Températures des thermistances 1 & 2 et T3 estimée"),
            (self.ax2, "Commande u et erreur en temps réel"),
        ]:
            ax.set_facecolor(SURFACE)
            ax.set_title(title, fontsize=10, color=MUTED, pad=6)
            ax.set_xlabel("Temps (s)", fontsize=9, color=MUTED)
            ax.set_ylabel("°C", fontsize=9, color=MUTED)
            ax.set_xlim(0, 100)
            ax.tick_params(colors=MUTED, labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor(BORDER)
            ax.grid(color="#EAE0E8", linewidth=0.5)

        self.ax1.set_ylim(15, 45)
        self.ax2.set_ylim(15, 45)

        self.line  = self.ax1.plot([], [], label="Thermistance 1",
                                   color="#A61F08", lw=1.5)[0]
        self.line2 = self.ax1.plot([], [], label="Thermistance 2",
                                   color="#0062DB", lw=1.5)[0]
        self.line3 = self.ax1.plot([], [], label="T3 estimée (moy)",
                                   color="#1A8A2E", lw=1.5, linestyle="--")[0]
        self.line4 = self.ax2.plot([], [], label="Commande u",
                                   color="#E08000", lw=1.5)[0]
        self.line5 = self.ax2.plot([], [], label="Erreur",
                                   color="#9B00C2", lw=1.5)[0]

        self.ax1.legend(fontsize=8, loc="upper right",
                        facecolor=CARD, edgecolor=BORDER)
        self.ax2.legend(fontsize=8, loc="upper right",
                        facecolor=CARD, edgecolor=BORDER)

        self.canvas = FigureCanvasTkAgg(self.fig, master=charts_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True,
                                         padx=10, pady=(0, 10))
        self.canvas.draw()


    def envoyer_config_totale(self):
        try:
            temp = float(self.temperature_entry_att.get())
            kp   = float(self.a0_entry.get())
            ti   = float(self.a1_entry.get())
            td   = float(self.a2_entry.get())

            if 10 <= temp <= 45:
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
            messagebox.showerror("Erreur",
                "Veuillez entrer des nombres valides dans tous les champs.")
        except serial.SerialException as e:
            messagebox.showerror("Erreur de connexion",
                f"Impossible de trouver l'Arduino : {e}")
        except Exception as e:
            messagebox.showerror("Erreur Inattendue",
                f"Il y a un problème : {e}")

    def trouver_port_arduino(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "USB Serial" in port.description:
                print(f"Arduino trouvé sur le port : {port.device}")
                return port.device
        raise serial.SerialException(
            "Arduino introuvable! Vérifiez le branchement USB.")

    def demarrer_proto(self):
        try:
            self.initialiser_graphiques()
            port_auto = self.trouver_port_arduino()

            if not self.running:
                self.ser = serial.Serial(port_auto, 9600, timeout=1)
                time.sleep(2)

                self.running = True
                self.start_time = time.time()

                # ← mise à jour statut
                self.status_label.config(
                    text="● En marche", bg="#EAF3DE", fg="#3B6D11")

                self.update_data()
                print("Communication établie. Réception des données.")

        except serial.SerialException as e:
            messagebox.showerror("Erreur de connexion", f"{e}")
        except Exception as e:
            messagebox.showerror("Erreur critique",
                f"Vérifiez le port USB : {e}")

    def initialiser_graphiques(self):
        self.ax1.cla()
        self.ax2.cla()

        CARD     = "#FFFFFF"
        SURFACE  = "#F5EFF3"
        MUTED    = "#7A5568"
        BORDER   = "#D9C8D4"


        for ax, title in [
            (self.ax1, "Températures des thermistances 1 & 2 et T3 estimée"),
            (self.ax2, "Commande u et erreur en temps réel"),
        ]:
            ax.set_facecolor(SURFACE)
            ax.set_title(title, fontsize=10, color=MUTED, pad=6)
            ax.set_xlabel("Temps (s)", fontsize=9, color=MUTED)
            ax.set_ylabel("°C", fontsize=9, color=MUTED)
            ax.set_xlim(0, 100)
            ax.tick_params(colors=MUTED, labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor(BORDER)
            ax.grid(color="#EAE0E8", linewidth=0.5)

        self.ax1.set_ylim(15, 45)
        self.ax2.set_ylim(15, 45)

        self.line  = self.ax1.plot([], [], label="Thermistance 1",
                                   color="#A61F08", lw=1.5)[0]
        self.line2 = self.ax1.plot([], [], label="Thermistance 2",
                                   color="#0062DB", lw=1.5)[0]
        self.line3 = self.ax1.plot([], [], label="T3 estimée (moy)",
                                   color="#1A8A2E", lw=1.5, linestyle="--")[0]
        self.line4 = self.ax2.plot([], [], label="Commande u",
                                   color="#E08000", lw=1.5)[0]
        self.line5 = self.ax2.plot([], [], label="Erreur",
                                   color="#9B00C2", lw=1.5)[0]

        self.ax1.legend(fontsize=8, loc="upper right",
                        facecolor=CARD, edgecolor=BORDER)
        self.ax2.legend(fontsize=8, loc="upper right",
                        facecolor=CARD, edgecolor=BORDER)
        self.canvas.draw()

    def arreter_proto(self):
        self.running = False

        self.status_label.config(
            text="● Arrêté", bg="#FCEBEB", fg="#A32D2D")

        try:
            cmd = f"CONFIG:{self.temperature_ambiante},{self.kp},{self.ti},{self.td}\n"
            self.ser.write(cmd.encode('utf-8'))
        except Exception as e:
            messagebox.showerror("Erreur", f"Vérifiez le port USB : {e}")
        print("Commande envoyée pour ramener à T ambiante")

        if self.ser:
            self.ser.close()
        print("Prototype arrêté")

    def update_data(self):
        if self.running and self.ser:
            try:
                line = self.ser.readline().decode('utf-8').strip()

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

                        # ← mise à jour métriques
                        self.metric_t1.set(f"{t1:.1f} °C")
                        self.metric_t2.set(f"{t2:.1f} °C")
                        self.metric_t3.set(f"{t3:.1f} °C")
                        self.metric_err.set(f"{e:.1f} °C")

                        # Axe X
                        if current_time > 100:
                            self.ax1.set_xlim(0, current_time)
                            self.ax2.set_xlim(0, current_time)
                        else:
                            self.ax1.set_xlim(0, max(current_time, 10))
                            self.ax2.set_xlim(0, max(current_time, 10))

                        # Axe Y graphique 1
                        if self.t1_data and self.t2_data and self.t3est_data:
                            toutes = self.t1_data + self.t2_data + self.t3est_data
                            y_min = min(toutes)
                            y_max = max(toutes)
                            marge = max((y_max - y_min) * 0.1, 1)
                            self.ax1.set_ylim(y_min - marge, y_max + marge)

                        # Axe Y graphique 2
                        if self.u_data and self.e_data:
                            toutes2 = self.u_data + self.e_data
                            y_min2 = min(toutes2)
                            y_max2 = max(toutes2)
                            marge2 = max((y_max2 - y_min2) * 0.1, 1)
                            self.ax2.set_ylim(y_min2 - marge2, y_max2 + marge2)

                        self.timer()
                        self.canvas.draw()

            except Exception as ex:
                print(f"Read error: {ex}")

        if self.running:
            self.root.after(100, self.update_data)

    def enregistrer_donnees(self):
        if not self.times:
            messagebox.showwarning("Avertissement",
                "Aucune donnée à enregistrer.")
            return

        nom_defaut = (f"donnees_"
                      f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

        chemin = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv"),
                       ("Tous les fichiers", "*.*")],
            initialfile=nom_defaut,
            title="Enregistrer les données"
        )

        if not chemin:
            return

        df = pd.DataFrame({
            "Temps (s)":                          self.times,
            "Thermistance 1 - T1 (°C)":           self.t1_data,
            "Thermistance 2 - T2 (°C)":           self.t2_data,
            "Thermistance 3 estimée - T3_moy (°C)": self.t3est_data,
            "Erreur (°C)":                         self.e_data,
            "Commande - u":                        self.u_data,
        })

        df.to_csv(chemin, index=False)
        messagebox.showinfo("Succès",
            f"Données enregistrées dans :\n{chemin}")

    def ramener_ambiante(self):        
        try:
            port_auto = self.trouver_port_arduino()
            self.initialiser_graphiques()

            if not self.running:
                self.ser = serial.Serial(port_auto, 9600, timeout=1)
                time.sleep(2)
                
            cmd = f"SET_CONSIGNE:{23.5}\n"
            self.ser.write(cmd.encode('utf-8'))
            print("Commande envoyée pour ramener à T ambiante")
            self.running = True
            self.initialiser_graphiques()

        except serial.SerialException as e:
            messagebox.showerror("Erreur de connexion", f"{e}")
        except Exception as e:
            messagebox.showerror("Erreur critique",
                f"Vérifiez le port USB : {e}")

        #if not self.running or not self.ser or not self.ser.is_open:
         #   messagebox.showwarning("Avertissement",
          #      "Le prototype n'est pas démarré.")
           # return
        #try:
         #   cmd = f"SET_CONSIGNE:{self.temperature_ambiante}\n"
          #  self.ser.write(cmd.encode('utf-8'))
        #except Exception as e:
         #   messagebox.showerror("Erreur", f"Vérifiez le port USB : {e}")
        #print("Commande envoyée pour ramener à T ambiante")

    def timer(self):
        corridor_bas  = (self.temperature_voulue
                         - (self.temperature_voulue - self.temperature_ambiante) * 0.05)
        corridor_haut = (self.temperature_voulue
                         + (self.temperature_voulue - self.temperature_ambiante) * 0.05)

        if corridor_bas <= self.t3est_data[-1] <= corridor_haut:
            if self.timer_termine:
                return

            if self.timer_start is None:
                self.timer_start = time.time()
                self.label_timer.config(text="Test de stabilité : 00:00")
                self.timer_frame.config(bg="#67EB5B")
            else:
                ecoule  = time.time() - self.timer_start
                restant = max(0, self.duree_cible - ecoule)
                mins, secs = divmod(int(restant), 60)
                self.label_timer.config(
                    text=f"Test de stabilité : {mins:02d}:{secs:02d}")
                self.timer_frame.config(bg="#67EB5B")

                if restant <= 0:
                    self.timer_termine = True
                    self.label_timer.config(
                        text="CIBLE ATTEINTE (5 min) : Système stable")
                    self.timer_frame.config(bg="#67EB5B")
        else:
            if not self.timer_termine:
                self.timer_start = None
                self.label_timer.config(text="Hors corridor")
                self.timer_frame.config(bg="#EBCDE2")


    def envoyer_valeurs_arduino(self):
        try:
            cmd = (f"CONFIG:{self.temperature_voulue},"
                   f"{self.kp},{self.ti},{self.td}\n")
            self.ser.write(cmd.encode('utf-8'))
            print(f"Config envoyée : {cmd.strip()}")
        except Exception as e:
            messagebox.showerror("Erreur",
                f"Impossible d'envoyer la config : {e}")


    def indicateur_stabilite(self):
        pass

def main():
    root = tk.Tk()
    app = InterfaceProto(root)
    root.mainloop()


if __name__ == "__main__":
    main()