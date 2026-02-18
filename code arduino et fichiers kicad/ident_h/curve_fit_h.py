import numpy as np
import scipy.optimize as sp
import matplotlib.pyplot as plt

file = open("/Users/mayadery/Desktop/H26/design 2/simulateur-thermique-1/code arduino et fichiers kicad/ident_h/temperature_20260216_172323.csv", 'r')
line = file.readline()

temps = []
Temp = []

i = 0
for line in file:
    i += 1
    if i > 1:
        data = line.split(",")
        temps.append(float(data[0]))
        Temp.append(float(data[1]))

t = np.array(temps)
T = np.array(Temp)
print(T)
t -= t[0]

def exponentielle(t, tau, a, c):
    return a*np.exp(-t/tau) + c

tau0 = (t[-1] - t[0]) / 5
c0 = T[-1]
a0 = T[0] - c0

p0 = [tau0, a0, c0]

popt, pcov = sp.curve_fit(exponentielle, t, T, p0=p0)
print(popt[0])

plt.figure()
plt.plot(t, T, '.b', label='Données expérimentales')
plt.plot(t, exponentielle(t, popt[0], popt[1], popt[2]), 'r-', label='Fit exp')
plt.xlabel('temps')
plt.ylabel('temperature')
plt.show()