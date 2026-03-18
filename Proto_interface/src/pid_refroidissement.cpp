#include <Arduino.h>

// ===================== PWM =====================
const int pwmPin_CHAUD = 5;
const int pwmPin_FROID = 11;

// ===================== PID DISCRET =====================
float setpoint    = 35.0;   // ← variable, modifiable via Python
float T0_celsius  = 21.0;   // ← température ambiante, modifiable via Python

// CORRECTION 1 : T_s était utilisé dans loop() mais jamais déclaré
const float T_s = 1.0;     // période d'échantillonnage en secondes

float a0 =  181.7;
float a1 = -355.7;
float a2 =  174;
float b1 = -0.003523;
float b2 = 0.9965;

float K = 10.85;
float Ti = 271;
float Td = 0;

// ===================== THERMISTANCES =====================
#define RT0 10000

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

float T0;

// ===================== ESTIMATEUR T3 depuis T1 (G3_1) =====================
const float G1_b0 =  0.002432;
const float G1_b1 =  0.002432;
const float G1_a1 = -0.9926;

float T1_init     = 0.0;
float u1_prev     = 0.0;
float y1_prev     = 0.0;

// ===================== ESTIMATEUR T3 depuis T2 (G3_2) =====================
const float G2_b0 =  0.009158;
const float G2_b1 =  0.009158;
const float G2_a1 = -0.98;

float T2_init     = 0.0;
float u2_prev     = 0.0;
float y2_prev     = 0.0;

float T3_init     = 0.0;

// ===================== VARIABLES PID =====================
float e[3]   = {0, 0, 0};
float u_prev_1 = 0.0;
float u_prev_2 = 0.0;


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
  u = constrain(u, -255, 255);
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
  T0 = 25.0 + 273.15;

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

  // CORRECTION 2 : lire les commandes SET_CONSIGNE et SET_AMBIANT envoyées par Python
  //Correction 3: jai mis tout dans un même chargement: les trucs du pid et la temp voulue
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("CONFIG:")) {
        String valeurs = cmd.substring(7);
        int v1 = valeurs.indexOf(',');
        int v2 = valeurs.indexOf(',', v1 + 1);
        int v3 = valeurs.indexOf(',', v2 + 1);

        if (v1 != -1 && v2 != -1 && v3 != -1) {
            setpoint   = valeurs.substring(0, v1).toFloat();
            K         = valeurs.substring(v1 + 1, v2).toFloat();
            Ti         = valeurs.substring(v2 + 1, v3).toFloat();
            Td         = valeurs.substring(v3 + 1).toFloat();

            Serial.println("ACK:CONFIG_COMPLETE");
        }
    }
//ANCIEN CODE
    // if (cmd.startsWith("SET_CONSIGNE:")) {
    //   setpoint = cmd.substring(13).toFloat();
    // } else if (cmd.startsWith("SET_AMBIANT:")) {
    //   T0_celsius = cmd.substring(12).toFloat();
    //   T0 = T0_celsius + 273.15;
    // }
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

    // 3a. Estimation T3 depuis T1
    float dT3_estimT1 = G1_b0 * dT1 + G1_b1 * u1_prev - G1_a1 * y1_prev;
    float T3_estimT1  = T3_init + dT3_estimT1;
    u1_prev = dT1;
    y1_prev = dT3_estimT1;

    // 3b. Estimation T3 depuis T2
    float dT3_estimT2 = G2_b0 * dT2 + G2_b1 * u2_prev - G2_a1 * y2_prev;
    float T3_estimT2  = T3_init + dT3_estimT2;
    u2_prev = dT2;
    y2_prev = dT3_estimT2;

    // 3c. Fusion : moyenne des deux estimations
    float T3_moy = (T3_estimT1 + T3_estimT2) / 2.0;

    // 4. Erreur PID sur T3 fusionnée
    e[0] = setpoint - T3_moy;
    //PAS SURE DE CES RELATIONS
    // a0 = K + Ti*T_s + Td/T_s;
    // a1 = -K -2*Td/T_s;
    // a2 = -Td/T_s;

    // 5. Récurrence PID
    float u = b1 * u_prev_1 + b2 * u_prev_2 + a0 * e[0] + a1 * e[1] + a2 * e[2];

    // 6. Saturation + PWM
    envoyerPWM(u);

    // 7. Décaler états PID
    u_prev_2 = u_prev_1;
    u_prev_1 = constrain(u, -255, 255);
    e[2]   = e[1];
    e[1]   = e[0];

    // 8. Log CSV
    double t_s = (now - tempsDebut) / 1000.0;

    if (modeCSV && t_s < DUREE_ENREGISTREMENT) {
      Serial.print(t_s, 3);
      Serial.print(","); Serial.print(T1, 2);
      Serial.print(","); Serial.print(T2, 2);
      Serial.print(","); Serial.print(T3, 2);
      Serial.print(","); Serial.print(T3_estimT2, 2);
      Serial.print(","); Serial.print(T3_estimT1, 2);
      Serial.print(","); Serial.print(T3_moy, 2);
      Serial.print(","); Serial.print(e[1], 4);
      Serial.print(","); Serial.println(constrain(u, -255, 255), 2);

    } else if (modeCSV) {
      Serial.println("FIN");
      modeCSV = false;
    }
  }
}