import numpy as np
import matplotlib.pyplot as plt
import control as ctrl

# 1. Définition du procédé (3ème ordre)
# Exemple : G(s) = K / ((tau1*s+1)(tau2*s+1)(tau3*s+1))
K = 0.0076447  # Ton gain linéarisé
tau1, tau2, tau3 = 83.68, 32.48, 25.458
G = ctrl.tf([K], np.polymul([tau1, 1], np.polymul([tau2, 1], [tau3, 1])))

# 2. Définition du PIDF
Kp, Ki, Kd, Tf = 156.73, 156.73/99.92, 156.73*16.24, 1.624 # Tes paramètres à tester
C = ctrl.tf([Kd + Kp*Tf, Kp + Ki*Tf, Ki], [Tf, 1, 0])

# # 3. Boucle fermée et Simulation
# sys_cl = ctrl.feedback(C * G, 1)
# t, y = ctrl.step_response(sys_cl)

# plt.plot(t, y)
# plt.title('Réponse en boucle fermée (PIDF)')
# plt.grid()
# plt.show()

# Temps de simulation
t = np.linspace(0, 2000, 10000)

# 1. Réponse à la consigne (Setpoint)
T_consigne = ctrl.feedback(C * G, 1)
t_con, y_con = ctrl.forced_response(T_consigne, t, 1.0) # Consigne de 1.0

# 2. Réponse à la perturbation (Disturbance)
# La fonction de transfert "Perturbation -> Sortie" est G / (1 + G*C)
T_perturb = ctrl.feedback(G, C)
# On déclenche la perturbation à t=5000s
u_perturb = np.where(t >= 1000, 200, 0) # On ajoute 0.5 brusquement
t_per, y_per = ctrl.forced_response(T_perturb, t, u_perturb)

# Sortie totale = Réponse consigne + Réponse perturbation
plt.plot(t, y_con + y_per)
plt.axvline(x=1000, color='r', linestyle='--', label='Perturbation')
plt.title('Réponse du système avec perturbation à t=1000s')
plt.legend()
plt.grid()
plt.show()