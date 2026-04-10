import numpy as np

# =====================================================
# PARAMÈTRES À REMPLIR (METS TES PLAGES ICI)
# =====================================================

ranges = {
    "Rf": (3000, 8000),
    "Rg": (3000, 6000),
    "R1": (2000, 4000),
    "V1": (1.0, 2.0),
    "V2": (3.8, 5.0)
}

Vmin = 1.0
Vmax = 5.0


# =====================================================
# FONCTION RT
# =====================================================
def compute_RT(Rf, R1, Rg, V1, V2, Vout):
    denom = R1 * Vout + Rf * V1

    if denom <= 0:
        return None  # invalide (ne devrait pas arriver avec des R > 0 et V > 0)

    RT = ((Rf + R1) * Rg * V2) / denom - Rg
    return RT


# =====================================================
# TEST NUMÉRIQUE COMPLET
# =====================================================
def test_numerique():
    print("\n=== TEST NUMÉRIQUE ===")

    N = 10  # augmente pour plus de précision (N^6 combinaisons !)

    Rf_vals  = np.linspace(*ranges["Rf"], N)
    R1_vals  = np.linspace(*ranges["R1"], N)
    Rg_vals  = np.linspace(*ranges["Rg"], N)
    V1_vals  = np.linspace(*ranges["V1"], N)
    V2_vals  = np.linspace(*ranges["V2"], N)   # ← CORRECTION : V2 itéré aussi
    Vout_vals = np.linspace(Vmin, Vmax, N)

    total = 0
    fail  = 0
    worst_RT = float("inf")
    worst_case = {}

    for Rf in Rf_vals:
        for R1 in R1_vals:
            for Rg in Rg_vals:
                for V1 in V1_vals:
                    for V2 in V2_vals:           # ← CORRECTION : boucle V2 ajoutée
                        for Vout in Vout_vals:

                            total += 1
                            RT = compute_RT(Rf, R1, Rg, V1, V2, Vout)

                            if RT is None or RT <= 0 or np.isnan(RT) or np.isinf(RT):
                                fail += 1
                                if RT is not None and RT < worst_RT:
                                    worst_RT = RT
                                    worst_case = dict(Rf=Rf, R1=R1, Rg=Rg,
                                                      V1=V1, V2=V2, Vout=Vout)

                            elif RT < worst_RT:  # suivi du pire RT positif
                                worst_RT = RT
                                worst_case = dict(Rf=Rf, R1=R1, Rg=Rg,
                                                  V1=V1, V2=V2, Vout=Vout)

    print(f"Total tests : {total:,}")
    print(f"Échecs      : {fail:,}")
    print(f"Succès      : {total - fail:,}")
    print(f"RT minimum  : {worst_RT:.4f}  → cas : {worst_case}")

    if fail == 0:
        print("\n✅ RT > 0 pour TOUS les cas testés")
    else:
        print(f"\n❌ {fail} combinaison(s) échouent → voir pire cas ci-dessus")


# =====================================================
# TEST ANALYTIQUE (GARANTIE MATHÉMATIQUE)
# =====================================================
def test_analytique():
    """
    RT > 0  ⟺  ((Rf+R1)*Rg*V2) / (R1*Vout + Rf*V1)  >  Rg
              ⟺  (Rf+R1)*V2  >  R1*Vout + Rf*V1

    Pire cas pour le membre gauche  → minimiser : Rf_min, R1_min, V2_min
    Pire cas pour le membre droit   → maximiser : R1_max, Vout_max, Rf_max, V1_max
    """
    print("\n=== TEST ANALYTIQUE (PIRE CAS) ===")

    Rf_min, Rf_max = ranges["Rf"]
    R1_min, R1_max = ranges["R1"]
    V1_min, V1_max = ranges["V1"]
    V2_min, V2_max = ranges["V2"]

    # CORRECTION : pire cas LHS = minimum de (Rf+R1)*V2
    LHS = (Rf_min + R1_min) * V2_min

    # pire cas RHS = maximum de R1*Vout + Rf*V1
    RHS = R1_max * Vmax + Rf_max * V1_max

    print(f"Condition requise : (Rf+R1)*V2  >  R1*Vout + Rf*V1")
    print(f"Pire LHS (min)   = ({Rf_min} + {R1_min}) × {V2_min} = {LHS}")
    print(f"Pire RHS (max)   = {R1_max} × {Vmax} + {Rf_max} × {V1_max} = {RHS}")
    print(f"Marge            = {LHS - RHS:.2f}")

    if LHS > RHS:
        print("\n✅ GARANTIE MATHÉMATIQUE : RT > 0 sur toute la plage")
    else:
        print("\n❌ PAS GARANTI — réduire les plages ou revoir les contraintes")
        print(f"   Il faut LHS > RHS, soit un écart de {RHS - LHS:.2f} à combler")


# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    test_analytique()
    test_numerique()