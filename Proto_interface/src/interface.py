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
        
        tk.Label(self.root, text="Température à ambiante (°C):", font=("Arial", 12)).pack(pady=5)
        self.temperature_entry_amb = tk.Entry(self.root, width=10, font=("Arial", 12))
        self.temperature_entry_amb.insert(0, self.temperature_ambiante)
        self.temperature_entry_amb.pack(pady=5)
       
        
        tk.Label(self.root, text="Température à atteindre (°C):", font=("Arial", 12)).pack(pady=5)
        self.temperature_entry_att = tk.Entry(self.root, width=10, font=("Arial", 12))
        self.temperature_entry_att.insert(0, self.temperature_voulue)
        self.temperature_entry_att.pack(pady=5)


        contrast_frame = tk.Frame(self.root)
        contrast_frame.pack(pady=10)

       

        self.contrast_value_label = tk.Label(
            contrast_frame, text=f"Value: N/A",
            font=("Arial", 12), bg="lightyellow", relief="solid", borderwidth=1, padx=10
        )
        self.contrast_value_label.pack(side=tk.LEFT, padx=5)
        
        self.count_label = tk.Label(self.root, bg="white", relief="solid", borderwidth=2, fg="darkblue")
  

    def valider_temp_ambiante(self):
        try:
            value = float(self.temperature_ambiante.get())
            if -30 <= value <= 60:
                self.temperature_ambiante = value
                self.contrast_value_label.config(text=f"Value: {self.temperature_ambiante:.2f}")
                if self.temperature_voulue is not None:
                    self.demarrer_proto()
            
            else:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour la température ambiante.")

    def valider_temp_voulue(self):
        try:
            value = float(self.temperature_voulue.get())
            self.temperature_voulue = value
            if self.temperature_ambiante is not None:
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
