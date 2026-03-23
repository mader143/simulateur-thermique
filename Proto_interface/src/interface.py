import tkinter as tk
from tkinter import messagebox
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
        self.temperature_initiale = self.temperature_ambiante
        self.applied = False

        # pid réchauffement
        self.kp_chaud = 9.2
        self.ti_chaud = 250
        self.td_chaud = 35

        # pid refroidissement
        self.kp_froid = 4.45
        self.ti_froid = 88.64
        self.td_froid = 13.04

        self.times = []
        self.t1_data = []
        self.t2_data = []
        self.t3est_data = []
        self.u_data = []
        self.e_data = []
        self.t3reel_data = []
        self.consigne = []

        self.create_widgets()

    def create_widgets(self):
        BG = "#F5EFF3"
        CARD = "#FFFFFF"
        SURFACE = "#F5EFF3"
        WINE = "#4B0E26"
        MUTED = "#7A5568"
        TEXT = "#1A0A10"
        BORDER = "#D9C8D4"


        self.root.configure(bg=BG)

        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=14, pady=10)

        # ── En-tête ───────────────────────────────────────────────────
        header = tk.Frame(outer, bg=CARD, highlightthickness=1,
                          highlightbackground=BORDER)
        header.pack(fill="x", pady=(0, 6))

        left_h = tk.Frame(header, bg=CARD)
        left_h.pack(side="left", padx=12, pady=6)

        dot = tk.Canvas(left_h, width=20, height=20, bg=CARD,
                        highlightthickness=0)
        dot.create_oval(0, 0, 20, 20, fill=WINE, outline="")
        dot.pack(side="left", padx=(0, 8))

        tk.Label(left_h, text="Contrôleur PID — Prototype thermique — Équipe 5",
                 font=("Arial", 12, "bold"), bg=CARD, fg=TEXT).pack(side="left")

        right_h = tk.Frame(header, bg=CARD)
        right_h.pack(side="right", padx=12)
        self.status_label = tk.Label(
            right_h, text="● En attente",
            font=("Courier", 10), bg="#EAF3DE", fg="#3B6D11",
            relief="flat", padx=8, pady=3
        )
        self.status_label.pack()

        # ── Boutons d'action ──────────────────────────────────────────
        btn_row = tk.Frame(outer, bg=BG)
        btn_row.pack(fill="x", pady=(0, 6))
        for i in range(4):
            btn_row.grid_columnconfigure(i, weight=1, uniform="btn")

        btns = [
            ("Démarrer le prototype", "#174D1C", "#E8F5EA", self.demarrer_proto),
            ("Arrêter le prototype", "#832828", "#FAE8E8", self.arreter_proto),
            ("Ramener à température ambiante", WINE, "#F9EFF4", self.ramener_ambiante),
            ("Enregistrer les données", "#1A3A5C", "#E6F1FB", self.enregistrer_donnees),
        ]
        for i, (txt, bg, fg, cmd) in enumerate(btns):
            tk.Button(
                btn_row, text=txt, command=cmd,
                font=("Arial", 12, "bold"), bg=bg, fg=fg,
                relief="flat", pady=9, cursor="hand2",
                activebackground=bg, activeforeground=fg
            ).grid(row=0, column=i, padx=4, sticky="ew")

        # ── Métriques temps réel ──────────────────────────────────────────────
        metrics_row = tk.Frame(outer, bg=BG)
        metrics_row.pack(fill="x", pady=(0, 6))
        for i in range(4):
            metrics_row.grid_columnconfigure(i, weight=1, uniform="metric")

        metric_defs = [
            ("T1 — Thermistance 1", "metric_t1"),
            ("T2 — Thermistance 2", "metric_t2"),
            ("T3 — Estimée", "metric_t3"),
            ("Erreur courante", "metric_err"),
        ]
        for i, (lbl, attr) in enumerate(metric_defs):
            card = tk.Frame(metrics_row, bg=CARD, highlightthickness=1,
                            highlightbackground=BORDER)
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            tk.Label(card, text=lbl, font=("Arial", 10), bg=CARD,
                     fg=MUTED).pack(anchor="w", padx=10, pady=(6, 0))
            var = tk.StringVar(value="— °C")
            tk.Label(card, textvariable=var,
                     font=("Courier", 16, "bold"), bg=CARD,
                     fg=TEXT).pack(anchor="w", padx=10, pady=(1, 6))
            setattr(self, attr, var)

        # ── Corps ─────────────────────────────────────────────────────────────
        body = tk.Frame(outer, bg=BG)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0, minsize=290)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # ── Colonne gauche ────────────────────────────────────────────────────
        left_col = tk.Frame(body, bg=BG)
        left_col.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        def section_title(parent, text):
            f = tk.Frame(parent, bg=BG)
            f.pack(fill="x", pady=(5, 2))
            tk.Frame(f, bg=WINE, width=3, height=12).pack(side="left",
                                                          padx=(0, 5))
            tk.Label(f, text=text.upper(), font=("Arial", 9, "bold"),
                     bg=BG, fg=WINE).pack(side="left")

        # Carte réglages
        section_title(left_col, "Réglages")
        reglages_card = tk.Frame(left_col, bg=CARD, highlightthickness=1,
                                 highlightbackground=BORDER)
        reglages_card.pack(fill="x", pady=(0, 8))

        inner = tk.Frame(reglages_card, bg=CARD)
        inner.pack(fill="x", padx=12, pady=10)
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_columnconfigure(1, weight=0)

        # Température cible
        tk.Label(inner, text="Température à atteindre (°C) :",
                 font=("Arial", 11), bg=CARD, fg=MUTED) \
            .grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.temperature_entry_att = tk.Entry(
            inner, width=7, font=("Courier", 12),
            bg=SURFACE, fg=TEXT, relief="flat",
            highlightthickness=1, highlightbackground=BORDER, justify="right"
        )
        self.temperature_entry_att.insert(0, self.temperature_voulue)
        self.temperature_entry_att.grid(row=0, column=1, pady=(0, 6))

        # PID réchauffement
        tk.Frame(inner, bg=BORDER, height=1) \
            .grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 6))
        tk.Label(inner, text="PID réchauffement",
                 font=("Arial", 10, "bold"), bg=CARD, fg=WINE) \
            .grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 4))

        for r, (lbl, val, attr) in enumerate([
            ("K — gain proportionnel", str(self.kp_chaud), "a0_chaud_entry"),
            ("Ti — temps intégral", str(self.ti_chaud), "a1_chaud_entry"),
            ("Td — temps dérivé", str(self.td_chaud), "a2_chaud_entry"),
        ]):
            tk.Label(inner, text=lbl, font=("Arial", 10), bg=CARD, fg=MUTED) \
                .grid(row=3 + r, column=0, sticky="w", pady=3)
            e = tk.Entry(inner, width=7, font=("Courier", 11),
                         bg=SURFACE, fg=TEXT, relief="flat",
                         highlightthickness=1, highlightbackground=BORDER,
                         justify="right")
            e.insert(0, val)
            e.grid(row=3 + r, column=1, pady=3)
            setattr(self, attr, e)

        # PID refroidissement
        tk.Frame(inner, bg=BORDER, height=1) \
            .grid(row=6, column=0, columnspan=2, sticky="ew", pady=(6, 6))
        tk.Label(inner, text="PID refroidissement",
                 font=("Arial", 10, "bold"), bg=CARD, fg="#185FA5") \
            .grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 4))

        for r, (lbl, val, attr) in enumerate([
            ("K — gain proportionnel", str(self.kp_froid), "a0_froid_entry"),
            ("Ti — temps intégral", str(self.ti_froid), "a1_froid_entry"),
            ("Td — temps dérivé", str(self.td_froid), "a2_froid_entry"),
        ]):
            tk.Label(inner, text=lbl, font=("Arial", 10), bg=CARD, fg=MUTED) \
                .grid(row=8 + r, column=0, sticky="w", pady=3)
            e = tk.Entry(inner, width=7, font=("Courier", 11),
                         bg=SURFACE, fg=TEXT, relief="flat",
                         highlightthickness=1, highlightbackground=BORDER,
                         justify="right")
            e.insert(0, val)
            e.grid(row=8 + r, column=1, pady=3)
            setattr(self, attr, e)

        # Bouton appliquer
        tk.Frame(inner, bg=BORDER, height=1) \
            .grid(row=11, column=0, columnspan=2, sticky="ew", pady=(6, 6))
        tk.Button(
            inner, text="Appliquer les données",
            command=self.appliquer_config,
            font=("Arial", 11), bg=WINE, fg=CARD,
            relief="flat", cursor="hand2", pady=7,
            activebackground="#7A1A3D", activeforeground=CARD
        ).grid(row=12, column=0, columnspan=2, sticky="ew", pady=(0, 2))

        # Carte stabilité
        section_title(left_col, "Test de stabilité")
        self.timer_frame = tk.Frame(left_col, bg=CARD, highlightthickness=1,
                                    highlightbackground=BORDER)
        self.timer_frame.pack(fill="x")

        tk.Label(self.timer_frame, text="Signal de stabilité",
                 font=("Arial", 10, "bold"), bg=CARD, fg=TEXT) \
            .pack(pady=(4, 1))
        
        self.label_timer = tk.Label(
            self.timer_frame, text="En attente d'un signal",
            font=("Arial", 8), bg=CARD, fg=MUTED)
        self.label_timer.pack(pady=(0, 4))

        # Carte mode manuel
        section_title(left_col, "Mode manuel - Entrez un PWM")
        self.pwm_frame = tk.Frame(left_col, bg=CARD, highlightthickness=1,
                                   highlightbackground=BORDER)
        self.pwm_frame.pack(fill="x", pady=(0, 4))

        pwm_row = tk.Frame(self.pwm_frame, bg=CARD)
        pwm_row.pack(fill="x", padx=8, pady=4)
        
        self.pwm_entry = tk.Entry(pwm_row, width=7, font=("Courier", 10),
                         bg=SURFACE, fg=TEXT, relief="flat",
                         highlightthickness=1, highlightbackground=BORDER,
                         justify="right")
        self.pwm_entry.pack(side="left", padx=(0, 4))
        
        tk.Button(pwm_row, text="Appliquer le PWM",
            command=self.appliquer_pwm,
            font=("Arial", 9), bg=WINE, fg=CARD,
            relief="flat", cursor="hand2", pady=4,
            activebackground="#7A1A3D", activeforeground=CARD
        ).pack(side="left", fill="x", expand=True)

        # ── Graphiques ───────────────────────────────────────
        charts_card = tk.Frame(body, bg=CARD, highlightthickness=1,
                               highlightbackground=BORDER, highlightcolor=BORDER)
        charts_card.grid(row=0, column=1, sticky="nsew")

        title_bar = tk.Frame(charts_card, bg=CARD)
        title_bar.pack(fill="x", padx=12, pady=(8, 2))
        tk.Frame(title_bar, bg=WINE, width=3, height=12) \
            .pack(side="left", padx=(0, 5))
        tk.Label(title_bar, text="VISUALISATION TEMPS RÉEL",
                 font=("Arial", 9, "bold"), bg=CARD, fg=WINE).pack(side="left")

        self.fig = Figure(dpi=100)
        self.fig.patch.set_facecolor(CARD)

        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        self.ax2b = self.ax2.twinx()

        self._setup_axes(CARD, SURFACE, MUTED, BORDER)

        self.fig.subplots_adjust(
            left=0.09, right=0.91,
            top=0.94, bottom=0.08,
            hspace=0.50
        )

        self.canvas = FigureCanvasTkAgg(self.fig, master=charts_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True,
                                         padx=8, pady=(0, 8))
        self.canvas.draw()

    def _setup_axes(self, CARD="#FFFFFF", SURFACE="#F5EFF3",
                    MUTED="#7A5568", BORDER="#D9C8D4"):

        # Graphique 1
        self.ax1.set_facecolor(SURFACE)
        self.ax1.set_title(
            "Températures des thermistances 1 & 2 et T3 estimée",
            fontsize=10, color=MUTED, pad=4)
        self.ax1.set_xlabel("Temps (s)", fontsize=9, color=MUTED)
        self.ax1.set_ylabel("Température (°C)", fontsize=9, color=MUTED)
        self.ax1.set_xlim(0, 100)
        self.ax1.set_ylim(15, 45)
        self.ax1.tick_params(colors=MUTED, labelsize=8)
        for sp in self.ax1.spines.values():
            sp.set_edgecolor(BORDER)
        self.ax1.grid(color="#EAE0E8", linewidth=0.5)

        # Graphique 2
        self.ax2.set_facecolor(SURFACE)
        self.ax2.set_title(
            "Commande et erreur en temps réel",
            fontsize=10, color=MUTED, pad=4)
        self.ax2.set_xlabel("Temps (s)", fontsize=9, color=MUTED)
        self.ax2.set_ylabel("Erreur (°C)", fontsize=9, color="#9B00C2")
        self.ax2.set_xlim(0, 100)
        self.ax2.set_ylim(-15, 15)  # plage initiale symétrique
        self.ax2.tick_params(axis='y', colors="#9B00C2", labelsize=8)
        self.ax2.tick_params(axis='x', colors=MUTED, labelsize=8)
        for sp in self.ax2.spines.values():
            sp.set_edgecolor(BORDER)
        self.ax2.grid(color="#EAE0E8", linewidth=0.5)

        # Graphique 2 axe droit
        self.ax2b.set_facecolor(SURFACE)
        self.ax2b.set_ylabel("Commande (PWM)", fontsize=9, color="#E08000")
        self.ax2b.set_ylim(-80, 80)  # plage fixe ±100
        self.ax2b.tick_params(axis='y', colors="#E08000", labelsize=8)
        for sp in self.ax2b.spines.values():
            sp.set_edgecolor(BORDER)

        self.ax2b.yaxis.set_label_position('right')
        self.ax2b.yaxis.tick_right()

        # Lignes graphique 1
        self.line = self.ax1.plot([], [], label="Thermistance 1",
                                  color="#A61F08", lw=1.5)[0]
        self.line2 = self.ax1.plot([], [], label="Thermistance 2",
                                   color="#0062DB", lw=1.5)[0]
        self.line3 = self.ax1.plot([], [], label="T3 estimée",
                                   color="#1A8A2E", lw=1.5, linestyle="--")[0]

        # Lignes graphique 2
        self.line4, = self.ax2b.plot([], [], label="Commande (PWM)",
                                     color="#E08000", lw=1.5)
        self.line5, = self.ax2.plot([], [], label="Erreur (°C)",
                                    color="#9B00C2", lw=1.5)

        # Légendes
        self.ax1.legend(
            fontsize=8, ncol=1,
            loc="upper left",
            frameon=True,
            framealpha=0.85,
            facecolor=CARD,
            edgecolor=BORDER
        )

        lines2 = [self.line5, self.line4]
        labels2 = [l.get_label() for l in lines2]
        self.ax2.legend(
            lines2, labels2,
            fontsize=8, ncol=1,
            loc="upper left",
            frameon=True,
            framealpha=0.85,
            facecolor=CARD,
            edgecolor=BORDER
        )

    def _sync_zeros(self, e_min, e_max, u_min, u_max):
        # Marge de sécurité
        marge_e = max(abs(e_min), abs(e_max), 1) * 1.20
        marge_u = max(abs(u_min), abs(u_max), 1) * 1.20

        marge_u = max(marge_u, 70)

        f = marge_e / (2 * marge_e)
        total_e = marge_e + marge_e
        total_u = marge_u + marge_u

        self.ax2.set_ylim(-marge_e, marge_e)
        self.ax2b.set_ylim(-marge_u, marge_u)

    def appliquer_pwm(self):
        if self.running:
            messagebox.showerror(
                "Arrêter le prototype avant d'appliquer le PWM")
        else:
            port_auto = self.trouver_port_arduino()
            self.ser = serial.Serial(port_auto, 9600, timeout=1)
            time.sleep(2)

            self.running = True
            self.start_time = time.time()
            self.timer_start = None
            self.timer_termine = False

            self.status_label.config(
                text="● En marche", bg="#EAF3DE", fg="#3B6D11")

            pwm = self.pwm_entry.get()
            try:
                pwm = int(pwm)
            except ValueError:
                messagebox.showerror(
                    "Valeur invalide",
                    f"« {pwm} » n'est pas un nombre valide pour la commande. Sélectionnez un nombre entre -255 et 255.")
                return
            if pwm < -255:
                messagebox.showerror(
                    "PWM trop bas",
                    f"La commande ({pwm}) est trop basse. Entrez un nombre entre -255 et 255.")
                return
            if pwm > 255:
                messagebox.showerror(
                    "PWM trop élevé",
                    f"La commande ({pwm}) est trop élevée. Entrez un nombre entre -255 et 255.")
                return
            
            try:
                cmd = (f"CONFIG_MANUELLE:{pwm}\n")
                self.ser.write(cmd.encode('utf-8'))
                print(f"Config envoyée : {cmd.strip()}")
                self.update_data()
            except Exception as e:
                messagebox.showerror("Erreur",
                                    f"Impossible d'envoyer la config : {e}")

    def appliquer_config(self):
        self.applied = True
        temp_str = self.temperature_entry_att.get().strip()
        try:
            temp = float(temp_str)
        except ValueError:
            messagebox.showerror(
                "Valeur invalide",
                f"« {temp_str} » n'est pas un nombre valide pour la température. Sélectionnez un nombre entre 10 et 35 °C.")
            return
        if temp < 10:
            messagebox.showerror(
                "Température trop basse",
                f"La température cible ({temp} °C) est trop basse. Entrez un nombre entre 10 et 35 °C.")
            return
        if temp > 35:
            messagebox.showerror(
                "Température trop élevée",
                f"La température cible ({temp} °C) est trop élevée. Entrez un nombre entre 10 et 35 °C.")
            return

        pid_champs = [
            (self.a0_chaud_entry, "Kp réchauffement"),
            (self.a1_chaud_entry, "Ti réchauffement"),
            (self.a2_chaud_entry, "Td réchauffement"),
            (self.a0_froid_entry, "Kp refroidissement"),
            (self.a1_froid_entry, "Ti refroidissement"),
            (self.a2_froid_entry, "Td refroidissement"),
        ]
        valeurs_pid = []
        for entree, nom in pid_champs:
            val_str = entree.get().strip()
            try:
                valeurs_pid.append(float(val_str))
            except ValueError:
                messagebox.showerror(
                    "Valeur invalide",
                    f"« {val_str} » n'est pas un nombre valide.")
                return

        self.temperature_voulue = temp
        self.kp_chaud, self.ti_chaud, self.td_chaud = valeurs_pid[0:3]
        self.kp_froid, self.ti_froid, self.td_froid = valeurs_pid[3:6]

        try:
            if self.running:
                self.envoyer_valeurs_arduino()
                # Mise à jour de la ligne de consigne sans toucher aux données
                messagebox.showinfo("Succès", "Configuration envoyée à l'Arduino.\nL'acquisition continue.")
            else:
                messagebox.showinfo(
                    "Succès",
                    "Configuration sauvegardée.\n"
                    "Cliquez sur « Démarrer le prototype » pour lancer.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Problème inattendu : {e}")

    def trouver_port_arduino(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "USB Serial" in port.description:
                print(f"Arduino trouvé sur le port : {port.device}")
                return port.device
        raise serial.SerialException(
            "Arduino non trouvé. Vérifiez le branchement USB.")

    def demarrer_proto(self):
        try:
            self.initialiser_graphiques()

            if not self.running:
                port_auto = self.trouver_port_arduino()
                self.ser = serial.Serial(port_auto, 9600, timeout=1)
                time.sleep(2)

                self.running = True
                self.start_time = time.time()
                self.timer_start = None
                self.timer_termine = False

                self.status_label.config(
                    text="● En marche", bg="#EAF3DE", fg="#3B6D11")

                self.appliquer_config()
                print("Communication établie. Réception des données.")

        except serial.SerialException as e:
            messagebox.showerror("Erreur de connexion", f"{e}")
        except Exception as e:
            messagebox.showerror("Erreur critique",
                                 f"Vérifiez le port USB : {e}")

    def initialiser_graphiques(self):
        self.ax1.cla()
        self.ax2.cla()
        self.ax2b.cla()

        self.times = []
        self.t1_data = []
        self.t2_data = []
        self.t3est_data = []
        self.u_data = []
        self.e_data = []

        self._setup_axes()
        self.fig.subplots_adjust(
            left=0.09, right=0.91,
            top=0.94, bottom=0.08,
            hspace=0.50
        )
        self.canvas.draw()

    def arreter_proto(self):
        self.running = False
        self.appliquer = False
        self.status_label.config(
            text="● Arrêté", bg="#FCEBEB", fg="#A32D2D")

        try:
            cmd = (f"CONFIG:{self.temperature_ambiante},"
                   f"{self.kp_chaud},{self.ti_chaud},{self.td_chaud}\n")
            self.ser.write(cmd.encode('utf-8'))
        except Exception as e:
            messagebox.showerror("Erreur", f"Vérifiez le port USB : {e}")

        if self.ser:
            self.ser.close()
        print("Prototype arrêté")

    def update_data(self):
        if self.running and self.ser:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                print(line)

                if line and not line.startswith("temps") and line != "FIN":
                    values = line.split(',')
                    if len(values) == 9:

                        t1 = float(values[1])
                        t2 = float(values[2])
                        t3 = float(values[6])
                        t3_reel = float(values[3])
                        e = float(values[7])
                        u = float(values[8])
                        current_time = time.time() - self.start_time

                        self.times.append(current_time)
                        self.t1_data.append(t1)
                        self.t2_data.append(t2)
                        self.t3est_data.append(t3)
                        self.u_data.append(u)
                        self.e_data.append(e)
                        self.t3reel_data.append(t3_reel)
                        self.consigne.append(self.temperature_voulue)

                        self.line.set_data(self.times, self.t1_data)
                        self.line2.set_data(self.times, self.t2_data)
                        self.line3.set_data(self.times, self.t3est_data)
                        self.line4.set_data(self.times, self.u_data)
                        self.line5.set_data(self.times, self.e_data)

                        # Métriques
                        self.metric_t1.set(f"{t1:.1f} °C")
                        self.metric_t2.set(f"{t2:.1f} °C")
                        self.metric_t3.set(f"{t3:.1f} °C")
                        self.metric_err.set(f"{e:.1f} °C")

                        # Axe X
                        xlim = max(current_time, 10) if current_time <= 100 \
                            else current_time
                        self.ax1.set_xlim(0, xlim)
                        self.ax2.set_xlim(0, xlim)
                        self.ax2b.set_xlim(0, xlim)

                        # Axe Y graphique 1 — auto
                        if self.t1_data and self.t2_data and self.t3est_data:
                            toutes = self.t1_data + self.t2_data + self.t3est_data
                            ymin, ymax = min(toutes), max(toutes)
                            marge = max((ymax - ymin) * 0.1, 1)
                            self.ax1.set_ylim(ymin - marge, ymax + marge)

                        # Axes Y graphique 2 — zéros synchronisés
                        if self.e_data and self.u_data:
                            self._sync_zeros(
                                min(self.e_data), max(self.e_data),
                                min(self.u_data), max(self.u_data)
                            )

                        if self.applied:
                            self.temperature_initiale = t3
                            self.applied = False

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
            "Temps (s)": self.times,
            "Consigne (°C)": self.consigne,
            "Erreur (°C)": self.e_data,
            "Thermistance 1 - T1 (°C)": self.t1_data,
            "Thermistance 2 - T2 (°C)": self.t2_data,
            "Thermistance 3 - T3 (°C)": self.t3reel_data,
            "T4'": '' * len(self.times),
            "Thermistance 3 estimée - T3_moy (°C)": self.t3est_data,    
            "Commande (PWM)": self.u_data,
       
        })
        df.to_csv(chemin, index=False)
        messagebox.showinfo("Succès",
                            f"Données enregistrées dans :\n{chemin}")

    def ramener_ambiante(self):
        try:
            if not self.running:
                port_auto = self.trouver_port_arduino()
                self.ser = serial.Serial(port_auto, 9600, timeout=1)
                time.sleep(2)
                self.running = True
                self.start_time = time.time()
                self.update_data()  # Redémarre la boucle seulement si elle n'était pas active

            cmd = f"SET_CONSIGNE:{self.temperature_ambiante}\n"
            self.ser.write(cmd.encode('utf-8'))
            print("Commande envoyée pour ramener à température ambiante")

            # Marqueur visuel sans effacer les données
            if self.times:
                t_now = self.times[-1]
                self.ax1.axvline(x=t_now, color="#0062DB", lw=1, linestyle=":")
                self.ax2.axvline(x=t_now, color="#0062DB", lw=1, linestyle=":")
                self.canvas.draw()

        except serial.SerialException as e:
            messagebox.showerror("Erreur de connexion", f"{e}")
        except Exception as e:
            messagebox.showerror("Erreur critique", f"Vérifiez le port USB : {e}")

    def timer(self):

        corridor_bas = (self.temperature_voulue
                        - abs(self.temperature_voulue
                           - self.temperature_initiale) * 0.05)
        corridor_haut = (self.temperature_voulue
                         + abs(self.temperature_voulue
                            - self.temperature_initiale) * 0.05)

        if corridor_bas <= self.t3est_data[-1] <= corridor_haut:
            if self.timer_termine:
                return

            if self.timer_start is None:
                self.timer_start = time.time()
                self.label_timer.config(
                    text="Test de stabilité : 00:00", bg="#F4AD4B")
                self.timer_frame.config(bg="#F4AD4B")
            else:
                ecoule = time.time() - self.timer_start
                restant = max(0, self.duree_cible - ecoule)
                mins, secs = divmod(int(restant), 60)
                self.label_timer.config(
                    text=f"Test de stabilité : {mins:02d}:{secs:02d}",
                    bg="#F4AD4B")
                self.timer_frame.config(bg="#F4AD4B")

                if restant <= 0:
                    self.timer_termine = True
                    self.label_timer.config(
                        text="CIBLE ATTEINTE (5 min) : Système stable",
                        bg="#67EB5B")
                    self.timer_frame.config(bg="#67EB5B")
        else:
            if not self.timer_termine:
                self.timer_start = None
                self.label_timer.config(text="Hors corridor", bg="#EBCDE2")
                self.timer_frame.config(bg="#EBCDE2")

    def envoyer_valeurs_arduino(self):
        try:
            cmd = (f"CONFIG:{self.temperature_voulue},"
                   f"{self.kp_chaud},{self.ti_chaud},{self.td_chaud},"
                   f"{self.kp_froid},{self.ti_froid},{self.td_froid}\n")
            self.ser.write(cmd.encode('utf-8'))
            print(f"Config envoyée : {cmd.strip()}")
            self.update_data()
        except Exception as e:
            messagebox.showerror("Erreur",
                                 f"Impossible d'envoyer la config : {e}")


def main():
    root = tk.Tk()
    app = InterfaceProto(root)
    root.mainloop()


if __name__ == "__main__":
    main()