import tkinter as tk
from tkinter import messagebox


class InterfaceProto:
    def __init__(self, root):
        self.root = root
        self.root.title("Contrôle du prototype")
        #self.root.geometry("900x700")
        
        self.temperature_voulue = 35
        self.temperature_ambiante = 21
        
        self.create_widgets()
        
    def create_widgets(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        upload_btn = tk.Button(
            button_frame, text="Démarrage", command=self.demarrer_proto,
            font=("Arial", 14), bg="lightblue", pady=10, width=15
        )
        upload_btn.pack(side=tk.LEFT, padx=10)
        

        frame_temp = tk.Frame(self.root)
        frame_temp.pack(pady=5)

        tk.Label(frame_temp, text="Température ambiante (°C):", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.temperature_entry_amb = tk.Entry(frame_temp, width=10, font=("Arial", 12))
        self.temperature_entry_amb.insert(0, self.temperature_ambiante)
        self.temperature_entry_amb.grid(row=0, column=1, padx=5, pady=5)

        apply_btn_amb = tk.Button(
            frame_temp, text="Appliquer", command=self.valider_temp_ambiante,
            font=("Arial", 12), width=8
        )
        apply_btn_amb.grid(row=0, column=2, padx=5)


        tk.Label(frame_temp, text="Température à atteindre (°C):", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.temperature_entry_att = tk.Entry(frame_temp, width=10, font=("Arial", 12))
        self.temperature_entry_att.insert(0, self.temperature_voulue)
        self.temperature_entry_att.grid(row=1, column=1, padx=5, pady=5)

        apply_btn_att = tk.Button(
            frame_temp, text="Appliquer", command=self.valider_temp_voulue,
            font=("Arial", 12), width=8
        )
        apply_btn_att.grid(row=1, column=2, padx=5)
    

    

    def valider_temp_ambiante(self):
        try:
            value = float(self.temperature_entry_amb.get())
            if -30 <= value <= 60:
                self.temperature_ambiante = value
                if self.temperature_voulue is isinstance(value, (float)):
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
                if self.temperature_ambiante is isinstance(value, (int, float)):
                    self.demarrer_proto()
            else:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour la température à atteindre.")

    def demarrer_proto(self):

        print(f"Température Ambiante: {self.temperature_ambiante} °C")
        print(f"Température à atteindre: {self.temperature_voulue} °C") 

   # def validate_contrast(self):
    #    try:
     #       value = float(self.contrast_entry.get())
      #      if 0 <= value <= 1:
       #         self.contrast_factor = value
        #        self.contrast_value_label.config(text=f"Value: {self.contrast_factor:.2f}")
         #       if self.temperature None:
          #          self.count_colonies()
           # else:
            #    raise ValueError
        #except ValueError:
         #   messagebox.showerror("Erreur", "Veuillez entrer un nombre valide entre 0 et 1.")


def main():
    root = tk.Tk()
    app = InterfaceProto(root)
    root.mainloop()

if __name__ == "__main__":
    main()
