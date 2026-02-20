import matplotlib.pyplot as plt
import numpy as np

P = np.array([0.47, 0.825, 1.17, 1.5, 2.2, 2.78])
PWM = np.array([5, 10, 12.5, 15, 20, 25])
x = np.linspace(0, 25, 100)

plt.figure()
plt.xlabel("PWM")
plt.ylabel("Puissance identifiée [W]")
plt.plot(PWM, P, '.k', markersize=10, label='Données expérimentales')
plt.plot(x, 0.0014*x**2 + 0.0771*x, '-r', label='R\u00b2 = 0.9946')
plt.legend()
plt.show()