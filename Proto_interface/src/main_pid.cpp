#include <Arduino.h>

// ===================== PWM =====================
const int pwmPin_CHAUD = 5;
const int pwmPin_FROID = 11;
int pwm_manuel = -1;   // ✅ AUTO par défaut

// ===================== PID =====================
float setpoint = 20;
const float T_s = 0.5;

float K  = 10.85;
float Ti = 271.0;
float Td = 0.0;

float new_K  = 0.0;
float new_Ti = 0.0;
float new_Td = 0.0;

// ===================== THERMISTANCES =====================
#define RT0 10000
const float T0 = 25.0 + 273.15;

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
  {A3, 3300, 5600, 3300, 1.774, 5.0, 4010},
  {A2, 6300, 5600, 3300, 1.80,  5.0, 3984},
  {A1, 6300, 5600, 3300, 1.79,  5.0, 3700},
};

// ===================== ESTIMATEURS =====================
const float G1_b0 =  0.002432;
const float G1_b1 =  0.002432;
const float G1_a1 = -0.9926;

float T1_init = 0.0;
float u1_prev = 0.0;
float y1_prev = 0.0;

const float G2_b0 =  0.009158;
const float G2_b1 =  0.009158;
const float G2_a1 = -0.98;

float T2_init = 0.0;
float u2_prev = 0.0;
float y2_prev = 0.0;

float T3_init = 0.0;

// ===================== PID =====================
float e[3]   = {0.0, 0.0, 0.0};
float u_prev = 0.0;

const float U_MAX =  255.0;
const float U_MIN = -255.0;

// ===================== CSV =====================
const unsigned long DUREE_ENREGISTREMENT = 1000;
unsigned long tempsDebut;
bool modeCSV = true;

// ===================== TIMING =====================
unsigned long lastPID = 0;

// =====================================================
float mesureTemperature(Thermistance t) {
  float Vout = (5.0 / 1023.0) * analogRead(t.pin);
  float RT = ((t.Rf + t.R1) * t.Rg * t.V2) /
             (t.R1 * Vout + t.Rf * t.V1) - t.Rg;
  float TX = 1.0 / ((log(RT / RT0) / t.B) + (1.0 / T0));
  return TX - 273.15;
}

float mesureTemperature1(Thermistance t) {
  float Vout = (5.0 / 1023.0) * analogRead(t.pin);
  return 9.1562 * Vout + 7.9337;
}

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
void setup() {
  Serial.begin(9600);

  pinMode(pwmPin_CHAUD, OUTPUT);
  pinMode(pwmPin_FROID, OUTPUT);
  analogWrite(pwmPin_CHAUD, 0);
  analogWrite(pwmPin_FROID, 0);

  delay(2000);

  T1_init = mesureTemperature1(therm[0]);
  T2_init = mesureTemperature(therm[1]);
  T3_init = mesureTemperature(therm[2]);

  Serial.println("temps_s,T1,T2,T3,T3_est2,T3_est1,T3_moy,erreur,commande");

  tempsDebut = millis();
}

// =====================================================
void loop() {
  unsigned long now = millis();

  // ===================== SERIAL =====================
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("CONFIG_MANUELLE:")){
      pwm_manuel = cmd.substring(16).toInt();
    }

    if (cmd.startsWith("CONFIG:")) {
      pwm_manuel = -1;  // ✅ retour en AUTO

      String valeurs = cmd.substring(7);
      int v1 = valeurs.indexOf(',');
      int v2 = valeurs.indexOf(',', v1 + 1);
      int v3 = valeurs.indexOf(',', v2 + 1);
      int v4 = valeurs.indexOf(',', v3 + 1);
      int v5 = valeurs.indexOf(',', v4 + 1);
      int v6 = valeurs.indexOf(',', v5 + 1);

      u_prev = 0.0;
      e[1] = 0.0;
      e[2] = 0.0;

      float new_sp = valeurs.substring(0, v1).toFloat();

      if (new_sp > 23.5) {
        new_K  = valeurs.substring(v1 + 1, v2).toFloat();
        new_Ti = valeurs.substring(v2 + 1, v3).toFloat();
        new_Td = valeurs.substring(v3 + 1, v4).toFloat();
      } else {
        new_K  = valeurs.substring(v4 + 1, v5).toFloat();
        new_Ti = valeurs.substring(v5 + 1, v6).toFloat();
        new_Td = valeurs.substring(v6 + 1).toFloat();
      }

      if (new_Ti != 0.0) {
        setpoint = new_sp;
        K  = new_K;
        Ti = new_Ti;
        Td = new_Td;
      }
    }
  }

  // ===================== PID =====================
  if (now - lastPID >= (unsigned long)(T_s * 1000)) {
    lastPID = now;

    float T1 = mesureTemperature1(therm[0]);
    float T2 = mesureTemperature(therm[1]);
    float T3 = mesureTemperature(therm[2]);

    float t_s = (now - tempsDebut) / 1000.0;

    float T3_estimT1, T3_estimT2, T3_moy;

    if (pwm_manuel != -1){
      envoyerPWM(pwm_manuel);
    }
    else{
      float dT1 = T1 - T1_init;
      float dT2 = T2 - T2_init;

      float dT3_estimT1 = G1_b0 * dT1 + G1_b1 * u1_prev - G1_a1 * y1_prev;
      T3_estimT1 = T3_init + dT3_estimT1;
      u1_prev = dT1;
      y1_prev = dT3_estimT1;

      float dT3_estimT2 = G2_b0 * dT2 + G2_b1 * u2_prev - G2_a1 * y2_prev;
      T3_estimT2 = T3_init + dT3_estimT2;
      u2_prev = dT2;
      y2_prev = dT3_estimT2;

      T3_moy = (T3_estimT1 + T3_estimT2) / 2.0;

      float a0 =  K * (1.0 + T_s / Ti + Td / T_s);
      float a1 = -K * (1.0 + 2.0 * Td / T_s);
      float a2 =  K * (Td / T_s);

      e[0] = setpoint - T3_moy;

      float u = u_prev + a0 * e[0] + a1 * e[1] + a2 * e[2];
      float u_sat = constrain(u, U_MIN, U_MAX);

      envoyerPWM(u_sat);

      // ✅ correction PID
      u_prev = u_sat;

      e[2] = e[1];
      e[1] = e[0];
    }
  }
}