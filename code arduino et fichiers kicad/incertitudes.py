import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Paramètres du circuit
# -------------------------------------------------------
R_A  = 9.7591    # kΩ
R_B  = 6.0399    # kΩ
R_C  = 1.9875    # kΩ
R_D  = 6.0351    # kΩ
R_E  = 6.0798    # kΩ
VDD  = 5.0       # V

# Incertitude multimètre (résolution 0.01 kΩ)
u_R = 0.01       # kΩ

# -------------------------------------------------------
# Incertitude Arduino ADC
# -------------------------------------------------------
V_ref_ADC = 5.0
ADC_bits  = 10
LSB       = V_ref_ADC / (2**ADC_bits)   # ≈ 4.88 mV
u_ADC     = LSB / np.sqrt(12)           # ≈ 1.41 mV

# -------------------------------------------------------
# Calibration NTC
# -------------------------------------------------------
T1_C = 25.0;  R1 = 10.050   # kΩ
T2_C = 35.0;  R2 = 6.666    # kΩ
T0   = T1_C + 273.15
R0   = R1

T1 = T1_C + 273.15
T2 = T2_C + 273.15
beta = 3782.74

# -------------------------------------------------------
# Propagation incertitude sur β
# -------------------------------------------------------
denom     = 1/T1 - 1/T2
dbeta_dR1 =  1.0 / (R1 * denom)
dbeta_dR2 = -1.0 / (R2 * denom)
u_beta    = np.sqrt((dbeta_dR1 * u_R)**2 + (dbeta_dR2 * u_R)**2)
u_R0      = u_R

print(f"u_β        = ±{u_beta:.4f} K")
print(f"u_R0       = ±{u_R0:.4f} kΩ")
print(f"u_ADC      = ±{u_ADC*1000:.4f} mV")

# -------------------------------------------------------
# Fonctions NTC
# -------------------------------------------------------

def R_NTC(T_celsius):
    T = T_celsius + 273.15
    return R0 * np.exp(beta * (1/T - 1/T0))

def T_from_R(R_TH):
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
# Dérivées partielles de V_out
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
# Incertitude sur V_out (circuit + ADC)
# -------------------------------------------------------

def u_Vout(R_TH):
    terms = [
        (dVout_dRD(R_TH)  * u_R)**2,
        (dVout_dRTH(R_TH) * u_R)**2,
        (dVout_dRA()      * u_R)**2,
        (dVout_dRB()      * u_R)**2,
        (dVout_dRC(R_TH)  * u_R)**2,
        (dVout_dRE(R_TH)  * u_R)**2,
        u_ADC**2,
    ]
    return np.sqrt(sum(terms))

# -------------------------------------------------------
# Dérivées partielles de T
# -------------------------------------------------------

def dT_dRTH(T_celsius):
    T    = T_celsius + 273.15
    R_TH = R_NTC(T_celsius)
    return -T**2 / (beta * R_TH)

def dT_dbeta(T_celsius):
    T    = T_celsius + 273.15
    return T**2 * (1/T - 1/T0) / beta

def dT_dR0(T_celsius):
    T = T_celsius + 273.15
    return T**2 / (beta * R0)

def dRTH_dVout(R_TH):
    return 1.0 / dVout_dRTH(R_TH)

def dT_dVout(T_celsius):
    R_TH = R_NTC(T_celsius)
    return dT_dRTH(T_celsius) * dRTH_dVout(R_TH)

# -------------------------------------------------------
# Incertitude totale sur T
# -------------------------------------------------------

def u_T(T_celsius):
    R_TH         = R_NTC(T_celsius)
    term_circuit = (dT_dVout(T_celsius) * u_Vout(R_TH))**2
    term_beta    = (dT_dbeta(T_celsius) * u_beta)**2
    term_R0      = (dT_dR0(T_celsius)  * u_R0)**2
    return np.sqrt(term_circuit + term_beta + term_R0)

def u_T_circuit_only(T_celsius):
    R_TH  = R_NTC(T_celsius)
    terms = [
        (dVout_dRD(R_TH)  * u_R)**2,
        (dVout_dRTH(R_TH) * u_R)**2,
        (dVout_dRA()      * u_R)**2,
        (dVout_dRB()      * u_R)**2,
        (dVout_dRC(R_TH)  * u_R)**2,
        (dVout_dRE(R_TH)  * u_R)**2,
    ]
    return abs(dT_dVout(T_celsius)) * np.sqrt(sum(terms))

def u_T_ADC_only(T_celsius):
    return abs(dT_dVout(T_celsius)) * u_ADC

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
print(f"  R_TH                 = {R_ex:.4f} kΩ")
print(f"  V_ref                = {V_ref():.4f} V")
print(f"  V+                   = {V_plus(R_ex):.4f} V")
print(f"  u_Vout               = {u_Vout(R_ex)*1000:.4f} mV")
print(f"  dT/dVout             = {dT_dVout(T_ex):.4f} °C/V")
print(f"  Contribution circuit : ±{u_T_circuit_only(T_ex):.4f} °C")
print(f"  Contribution ADC     : ±{u_T_ADC_only(T_ex):.4f} °C")
print(f"  Contribution β       : ±{u_T_beta_only(T_ex):.4f} °C")
print(f"  Contribution R0      : ±{u_T_R0_only(T_ex):.4f} °C")
print(f"  u_T TOTAL            = ±{u_T(T_ex):.4f} °C")
print()

print(f"{'T [°C]':>8} {'u_circuit':>12} {'u_ADC':>10} {'u_β':>10} {'u_R0':>10} {'u_T total':>12}")
print("-" * 68)
for T in [15, 20, 25, 30, 35, 40]:
    print(f"{T:>8.0f} {u_T_circuit_only(T):>12.4f} "
          f"{u_T_ADC_only(T):>10.4f} "
          f"{u_T_beta_only(T):>10.4f} "
          f"{u_T_R0_only(T):>10.4f} "
          f"{u_T(T):>12.4f}")

# -------------------------------------------------------
# Graphiques
# -------------------------------------------------------

# Graphique 1 : u_T total
plt.plot(T_range, u_T(T_range), 'b-', linewidth=2, label='$u_T$ total')
plt.xlabel('Température [°C]')
plt.ylabel('Incertitude $u_T$ [°C]')
plt.grid(True, alpha=0.3)
plt.legend()


plt.tight_layout()
plt.savefig(R'C:\Users\sabri\OneDrive\Desktop\uni\design\simulateur-thermique\code arduino et fichiers kicad', dpi=150)
plt.show()
print("Graphique sauvegardé.")