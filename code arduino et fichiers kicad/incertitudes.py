import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Paramètres du circuit
# -------------------------------------------------------
R_A  = 10.0    # kΩ
R_B  = 5.6     # kΩ
R_C  = 3.3     # kΩ
R_D  = 5.6     # kΩ
R_E  = 6.3     # kΩ
VDD  = 5.0     # V

# Incertitude multimètre (résolution 0.01 kΩ) -- toutes les résistances
u_R = 0.01     # kΩ

# -------------------------------------------------------
# Calibration NTC : deux points de mesure au multimètre
# -------------------------------------------------------
T1_C = 25.0;   R1 = 10.050   # kΩ  (aussi R0 et T0)
T2_C = 35.0;   R2 = 6.666    # kΩ
T0   = T1_C + 273.15          # K
R0   = R1                     # kΩ  (mesuré au multimètre)

# β calculé à partir des deux points
T1 = T1_C + 273.15
T2 = T2_C + 273.15
beta = np.log(R1 / R2) / (1/T1 - 1/T2)
print(f"β calibré = {beta:.4f} K")   # doit donner ~3782.74

# -------------------------------------------------------
# Propagation de l'incertitude sur β
#
#   β = ln(R1/R2) / (1/T1 - 1/T2)
#
#   ∂β/∂R1 =  1/(R1 * (1/T1 - 1/T2))
#   ∂β/∂R2 = -1/(R2 * (1/T1 - 1/T2))
#
# T1, T2 supposées exactes (thermomètre de référence)
# u_R1 = u_R2 = u_R (multimètre)
# -------------------------------------------------------
denom = 1/T1 - 1/T2
dbeta_dR1 =  1.0 / (R1 * denom)
dbeta_dR2 = -1.0 / (R2 * denom)
u_beta = np.sqrt((dbeta_dR1 * u_R)**2 + (dbeta_dR2 * u_R)**2)
print(f"u_β        = ±{u_beta:.4f} K")

# u_R0 = u_R (R0 mesuré au multimètre à T0)
u_R0 = u_R
print(f"u_R0       = ±{u_R0:.4f} kΩ")

# -------------------------------------------------------
# Fonctions NTC
# -------------------------------------------------------

def R_NTC(T_celsius):
    """R_TH en fonction de T (kΩ)"""
    T = T_celsius + 273.15
    return R0 * np.exp(beta * (1/T - 1/T0))

def T_from_R(R_TH):
    """T en fonction de R_TH (°C)"""
    return 1.0 / (1/T0 + np.log(R_TH / R0) / beta) - 273.15

# -------------------------------------------------------
# Fonctions du circuit
# -------------------------------------------------------

def V_ref():
    return VDD * R_B / (R_A + R_B)

def V_plus(R_TH):
    return VDD * R_D / (R_D + R_TH)

def gain():
    return (R_C + R_E) / R_C

def V_out(R_TH):
    return V_plus(R_TH) * gain() - V_ref() * (R_E / R_C)

# -------------------------------------------------------
# Dérivées partielles de V_out par rapport aux résistances
# -------------------------------------------------------

def dVout_dRD(R_TH):
    return gain() * VDD * R_TH / (R_D + R_TH)**2

def dVout_dRTH(R_TH):
    return -gain() * VDD * R_D / (R_D + R_TH)**2

def dVout_dRA():
    return -(R_E / R_C) * VDD * R_B / (R_A + R_B)**2

def dVout_dRB():
    return (R_E / R_C) * VDD * R_A / (R_A + R_B)**2

def dVout_dRC(R_TH):
    return (V_ref() - V_plus(R_TH)) * R_E / R_C**2

def dVout_dRE(R_TH):
    return (V_plus(R_TH) - V_ref()) / R_C

# -------------------------------------------------------
# Incertitude sur V_out (résistances circuit + R_TH)
# -------------------------------------------------------

def u_Vout(R_TH):
    terms = [
        (dVout_dRD(R_TH)  * u_R)**2,
        (dVout_dRTH(R_TH) * u_R)**2,
        (dVout_dRA()      * u_R)**2,
        (dVout_dRB()      * u_R)**2,
        (dVout_dRC(R_TH)  * u_R)**2,
        (dVout_dRE(R_TH)  * u_R)**2,
    ]
    return np.sqrt(sum(terms))

# -------------------------------------------------------
# Dérivées partielles de T par rapport à R_TH, β, R0
#
#   T = [ 1/T0 + ln(R_TH/R0)/β ]^{-1}
#
#   ∂T/∂R_TH = -T² / (β · R_TH)
#   ∂T/∂β    = -T² · ln(R_TH/R0) / β²    =  T² · (1/T - 1/T0) / β
#   ∂T/∂R0   =  T² / (β · R0)
# -------------------------------------------------------

def dT_dRTH(T_celsius):
    T = T_celsius + 273.15
    R_TH = R_NTC(T_celsius)
    return -T**2 / (beta * R_TH)

def dT_dbeta(T_celsius):
    T = T_celsius + 273.15
    R_TH = R_NTC(T_celsius)
    return T**2 * (1/T - 1/T0) / beta
    # équivalent : -T² * ln(R_TH/R0) / beta²

def dT_dR0(T_celsius):
    T = T_celsius + 273.15
    return T**2 / (beta * R0)

# -------------------------------------------------------
# Règle de la chaîne : ∂T/∂Vout = (∂T/∂R_TH) · (∂R_TH/∂Vout)
# -------------------------------------------------------

def dRTH_dVout(R_TH):
    return 1.0 / dVout_dRTH(R_TH)

def dT_dVout(T_celsius):
    R_TH = R_NTC(T_celsius)
    return dT_dRTH(T_celsius) * dRTH_dVout(R_TH)

# -------------------------------------------------------
# Incertitude totale sur T
#
#   u_T² = (∂T/∂Vout · u_Vout)²   ← circuit + R_TH(mesure)
#          + (∂T/∂β   · u_β)²      ← calibration β
#          + (∂T/∂R0  · u_R0)²     ← calibration R0
# -------------------------------------------------------

def u_T(T_celsius):
    R_TH = R_NTC(T_celsius)

    term_circuit = (dT_dVout(T_celsius) * u_Vout(R_TH))**2
    term_beta    = (dT_dbeta(T_celsius) * u_beta)**2
    term_R0      = (dT_dR0(T_celsius)  * u_R0)**2

    return np.sqrt(term_circuit + term_beta + term_R0)

def u_T_circuit_only(T_celsius):
    R_TH = R_NTC(T_celsius)
    return abs(dT_dVout(T_celsius)) * u_Vout(R_TH)

def u_T_beta_only(T_celsius):
    return abs(dT_dbeta(T_celsius)) * u_beta

def u_T_R0_only(T_celsius):
    return abs(dT_dR0(T_celsius)) * u_R0

# -------------------------------------------------------
# Affichage console
# -------------------------------------------------------

T_range = np.linspace(15, 40, 500)

T_ex = 25.0
R_ex = R_NTC(T_ex)
print()
print(f"=== Exemple à {T_ex}°C ===")
print(f"  R_TH              = {R_ex:.4f} kΩ")
print(f"  V_ref             = {V_ref():.4f} V")
print(f"  V+                = {V_plus(R_ex):.4f} V")
print(f"  u_Vout            = {u_Vout(R_ex)*1000:.4f} mV")
print(f"  dT/dVout          = {dT_dVout(T_ex):.4f} °C/V")
print(f"  Contribution circuit : ±{u_T_circuit_only(T_ex):.4f} °C")
print(f"  Contribution β       : ±{u_T_beta_only(T_ex):.4f} °C")
print(f"  Contribution R0      : ±{u_T_R0_only(T_ex):.4f} °C")
print(f"  u_T TOTAL         = ±{u_T(T_ex):.4f} °C")
print()

print(f"{'T [°C]':>8} {'u_circuit':>12} {'u_β':>10} {'u_R0':>10} {'u_T total':>12}")
print("-" * 58)
for T in [15, 20, 25, 30, 35, 40]:
    print(f"{T:>8.0f} {u_T_circuit_only(T):>12.4f} "
          f"{u_T_beta_only(T):>10.4f} "
          f"{u_T_R0_only(T):>10.4f} "
          f"{u_T(T):>12.4f}")

# -------------------------------------------------------
# Graphiques
# -------------------------------------------------------

plt.plot(figsize=(9, 9))

# -- Graphique 1 : u_T total vs T
plt.plot(T_range, u_T(T_range), 'b-', linewidth=2, label='$u_T$ total')
plt.xlabel('Température [°C]')
plt.ylabel('Incertitude $u_T$ [°C]')
plt.grid(True, alpha=0.3)


plt.tight_layout()
plt.savefig(R'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\code arduino et fichiers kicad', dpi=150)
plt.show()
print("Graphique sauvegardé.")