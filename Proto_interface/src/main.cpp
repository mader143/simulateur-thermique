#include <Arduino.h>

// ===================== PWM =====================
const int pwmPin_CHAUD = 5;
const int pwmPin_FROID = 11;

// ===================== PID DISCRET =====================
float setpoint = 30.0;   // modifiable via Python

const float T_s = 0.5;   // période d'échantillonnage en secondes

// Gains PID (modifiables via Python)
float K  = 10.85;
float Ti = 271.0;
float Td = 0.0;

// ===================== THERMISTANCES =====================
#define RT0 10000
const float T0 = 25.0 + 273.15;  // température de référence fixe (Kelvin)

struct Thermistance {
  int   pin;
  float Rf;
  float Rg;
  float R1;
  float V1;
  float V2;
  float B;
};

Thermistance therm[3] = {
  {A3, 6300, 5600, 3300, 1.774, 5.0, 3700},  // T1
  {A2, 6300, 5600, 3300, 1.80,  5.0, 3984},  // T2
  {A1, 6300, 5600, 3300, 1.79,  5.0, 3700},  // T3
};

// ===================== ESTIMATEUR T3 depuis T1 (G3_1) =====================
const float G1_b0 =  0.002432;
const float G1_b1 =  0.002432;
const float G1_a1 = -0.9926;

float T1_init    = 0.0;
float u1_prev    = 0.0;
float y1_prev    = 0.0;

// ===================== ESTIMATEUR T3 depuis T2 (G3_2) =====================
const float G2_b0 =  0.009158;
const float G2_b1 =  0.009158;
const float G2_a1 = -0.98;

float T2_init    = 0.0;
float u2_prev    = 0.0;
float y2_prev    = 0.0;

float T3_init    = 0.0;

// ===================== VARIABLES PID =====================
// Forme incrémentale : u[k] = u[k-1] + a0*e[k] - a1*e[k-1] + a2*e[k-2]
// Coefficients avec signes conventionnels positifs dans la récurrence :
//   a0 =  K*(1 + T_s/Ti + Td/T_s)
//   a1 =  K*(1 + 2*Td/T_s)          ← soustrait dans la récurrence
//   a2 =  K*(Td/T_s)                 ← ajouté dans la récurrence
float e[3]   = {0.0, 0.0, 0.0};
float u_prev = 0.0;

const float U_MAX =  255.0;
const float U_MIN = -255.0;

// ===================== CSV / LOG =====================
const unsigned long DUREE_ENREGISTREMENT = 1000;
unsigned long tempsDebut;
bool modeCSV = true;

// ===================== TIMING =====================
unsigned long lastPID = 0;


// =====================================================
// FONCTION MESURE TEMPÉRATURE
// =====================================================
float mesureTemperature(Thermistance t) {
  float Vout = (5.0 / 1023.0) * analogRead(t.pin);

  float RT = ((t.Rf + t.R1) * t.Rg * t.V2) /
             (t.R1 * Vout + t.Rf * t.V1) - t.Rg;

  float TX = 1.0 / ((log(RT / RT0) / t.B) + (1.0 / T0));

  return TX - 273.15;
}


// =====================================================
// ENVOI PWM CHAUD / FROID
// =====================================================
void envoyerPWM(float u) {
  u = constrain(u, U_MIN, U_MAX);
  if (u > 0) {
    analogWrite(pwmPin_CHAUD, (int) u);
    analogWrite(pwmPin_FROID, 0);
  } else {
    analogWrite(pwmPin_CHAUD, 0);
    analogWrite(pwmPin_FROID, (int)(-u));
  }
}


// =====================================================
// SETUP
// =====================================================
void setup() {
  Serial.begin(9600);

  pinMode(pwmPin_CHAUD, OUTPUT);
  pinMode(pwmPin_FROID, OUTPUT);
  analogWrite(pwmPin_CHAUD, 0);
  analogWrite(pwmPin_FROID, 0);

  delay(2000);

  T1_init = mesureTemperature(therm[0]);
  T2_init = mesureTemperature(therm[1]);
  T3_init = mesureTemperature(therm[2]);

  u1_prev = 0.0;  y1_prev = 0.0;
  u2_prev = 0.0;  y2_prev = 0.0;

  Serial.println("temps_s,T1_C,T2_C,T3_C,T3_estimT2,T3_estimT1,T3_moy,erreur,commande_u");
  tempsDebut = millis();
}


// =====================================================
// LOOP
// =====================================================
void loop() {
  unsigned long now = millis();

  // --- Lecture des commandes Python ---
  // Format: CONFIG:consigne,K,Ti,Td\n
  // Exemple: CONFIG:35.0,10.85,271.0,0.0
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("CONFIG:")) {
      String valeurs = cmd.substring(7);
      int v1 = valeurs.indexOf(',');
      int v2 = valeurs.indexOf(',', v1 + 1);
      int v3 = valeurs.indexOf(',', v2 + 1);

      // Validation : on exige exactement 3 virgules et des champs non-vides
      if (v1 > 0 && v2 > v1 + 1 && v3 > v2 + 1) {
        float new_sp = valeurs.substring(0, v1).toFloat();
        float new_K  = valeurs.substring(v1 + 1, v2).toFloat();
        float new_Ti = valeurs.substring(v2 + 1, v3).toFloat();
        float new_Td = valeurs.substring(v3 + 1).toFloat();

        // Garder les anciens paramètres si les nouvelles valeurs sont invalides
        if (new_Ti != 0.0) {
          setpoint = new_sp;
          K        = new_K;
          Ti       = new_Ti;
          Td       = new_Td;
          Serial.println("ACK:CONFIG_COMPLETE");
        } else {
          Serial.println("ERR:Ti_INVALIDE");
        }
      } else {
        Serial.println("ERR:FORMAT_INVALIDE");
      }
    }
  }

  if (now - lastPID >= (unsigned long)(T_s * 1000)) {
    lastPID = now;

    // 1. Lecture des 3 thermistances
    float T1 = mesureTemperature(therm[0]);
    float T2 = mesureTemperature(therm[1]);
    float T3 = mesureTemperature(therm[2]);

    // 2. Écarts par rapport à l'état initial
    float dT1 = T1 - T1_init;
    float dT2 = T2 - T2_init;

    // 3a. Estimation T3 depuis T1 (filtre IIR)
    float dT3_estimT1 = G1_b0 * dT1 + G1_b1 * u1_prev - G1_a1 * y1_prev;
    float T3_estimT1  = T3_init + dT3_estimT1;
    u1_prev = dT1;          // entrée retardée du filtre (= dT1[k-1])
    y1_prev = dT3_estimT1;  // sortie retardée du filtre

    // 3b. Estimation T3 depuis T2 (filtre IIR)
    float dT3_estimT2 = G2_b0 * dT2 + G2_b1 * u2_prev - G2_a1 * y2_prev;
    float T3_estimT2  = T3_init + dT3_estimT2;
    u2_prev = dT2;
    y2_prev = dT3_estimT2;

    // 3c. Fusion : moyenne des deux estimations
    float T3_moy = (T3_estimT1 + T3_estimT2) / 2.0;

    // 4. Erreur PID sur T3 fusionnée
    e[0] = setpoint - T3_moy;

    // 5. Calcul des coefficients PID discrets (forme incrémentale standard)
    //    u[k] = u[k-1] + a0*e[k] - a1*e[k-1] + a2*e[k-2]
    float a0 =  K * (1.0 + T_s / Ti + Td / T_s);
    float a1 =  K * (1.0 + 2.0 * Td / T_s);
    float a2 =  K * (Td / T_s);

    // 6. Récurrence PID incrémentale
    float u = u_prev + a0 * e[0] - a1 * e[1] + a2 * e[2];

    // 7. Saturation de la commande
    float u_sat = constrain(u, U_MIN, U_MAX);

    // 8. Anti-windup : ne pas accumuler si on est en saturation
    //    et que l'erreur pousse encore dans le sens de la saturation
    bool en_saturation = (u > U_MAX && e[0] > 0) || (u < U_MIN && e[0] < 0);
    if (en_saturation) {
      u_prev = u_sat;  // figer u_prev à la limite de saturation
    } else {
      u_prev = u_sat;
    }

    // 9. Envoi PWM
    envoyerPWM(u_sat);

    // 10. Décaler états PID
    e[2] = e[1];
    e[1] = e[0];

    // 11. Log CSV
    double t_s = (now - tempsDebut) / 1000.0;

    if (modeCSV && t_s < DUREE_ENREGISTREMENT) {
      Serial.print(t_s, 3);
      Serial.print(","); Serial.print(T1, 2);
      Serial.print(","); Serial.print(T2, 2);
      Serial.print(","); Serial.print(T3, 2);
      Serial.print(","); Serial.print(T3_estimT2, 2);
      Serial.print(","); Serial.print(T3_estimT1, 2);
      Serial.print(","); Serial.print(T3_moy, 2);
      Serial.print(","); Serial.print(e[0], 4);
      Serial.print(","); Serial.println(u_sat, 2);

    } else if (modeCSV) {
      Serial.println("FIN");
      modeCSV = false;
    }
  }
}
