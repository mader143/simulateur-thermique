import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter

x = np.array([0.003366437, 0.00336757, 0.003365304, 0.003368705, 0.00336984, 0.003375527, 0.003393857, 0.003392706, 0.003390405, 0.003378949, 0.003376667, 0.003370976, 0.003365304, 0.00336191, 0.003359651, 0.003358522, 0.003357395, 0.003356268, 0.003354016, 0.003352892, 0.003351768, 0.003350645, 0.003349523, 0.003348401, 0.00334728, 0.003346169, 0.003342805, 0.003337227, 0.003331667, 0.003326127, 0.003320604, 0.0033151, 0.003309614, 0.003298697, 0.003293265, 0.003287851, 0.003277077, 0.003266373, 0.003255738, 0.003245173, 0.003234676, 0.003224246])
y = np.array([9.258654232, 9.2623634, 9.25378293, 9.267665439, 9.267948685, 9.282661034, 9.36185902, 9.358156747, 9.35296777, 9.315690888, 9.297068375, 9.27799902, 9.259130536, 9.241839039, 9.236397906, 9.228671329, 9.225327502, 9.220290703, 9.215327913, 9.207837242, 9.202812106, 9.196241448, 9.1942109, 9.192176401, 9.185535253, 9.179881164, 9.169518377, 9.150590368, 9.131729971, 9.106534203, 9.088172738, 9.071078305, 9.05017162, 9.004545459, 8.980927208, 8.956737613, 8.923990745, 8.881836305, 8.839276691, 8.804775259, 8.754634047, 8.720950029])

slope, intercept = np.polyfit(x, y, 1)
y_fit = slope * x + intercept

fig, ax = plt.subplots(figsize=(8, 6))

ax.scatter(x, y, color='black', marker='o', s=20, label='Données expérimentales')
ax.plot(x, y_fit, color='blue', linestyle='dashdot', label=f'Régression : $y = {slope:.2f}x {intercept:.2f}$')

formatter = ScalarFormatter(useMathText=True)
formatter.set_scientific(True)
formatter.set_powerlimits((-3, -3))
ax.xaxis.set_major_formatter(formatter)

ax.set_xlabel('$1/T$ ($K^{-1}$)', fontsize=14)
ax.set_ylabel('$\ln(R)$', fontsize=14)
ax.legend(frameon=True, fontsize=14)
ax.grid(True, linestyle=':', alpha=0.7)
ax.tick_params(axis='both', labelsize=12, direction='in', top=True, right=True)

plt.tight_layout()
fig.savefig("regression_scientifique.png", bbox_inches='tight', dpi=600)
plt.show()