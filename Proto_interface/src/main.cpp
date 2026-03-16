#include <Arduino.h>

// ===================== THERMISTANCE =====================
#define RT0 10000
#define B   3980
#define R   10000

const int adcPin  = A2;
const int adcPin2 = A3;  // ← T1 (température actuateur)

// ===================== PWM =====================
const int pwmPin_CHAUD = 5;
const int pwmPin_FROID = 11;

// ===================== PID DISCRET =====================
const float T_s = 0.5;
float setpoint    = 35.0;   // ← variable, modifiable via Python
float T0_celsius  = 21.0;   // ← température ambiante, modifiable via Python

const float a0 =  8.765;
const float a1 = -8.595;
const float a2 =  0.0;

float T2_prev = 0;
float T3_est  = 0;
float T3_prev = 0;

// ===================== CIRCUIT AMPLI =====================
float Rc = 3300, Rd = 5600, Re = 6300;
float V1 = 1.795, V2 = 5.0;
float T0;

// ===================== VARIABLES D'ÉTAT PID =====================
float e[3]   = {0, 0, 0};
float u_prev = 0;
const float Ka = 0.5;

// ===================== CSV =====================
const unsigned long DUREE_ENREGISTREMENT = 1000;
unsigned long tempsDebut;
bool modeCSV = true;

// ===================== TIMING =====================
unsigned long lastPID = 0;

// ===================== LECTURE COMMANDES PYTHON =====================
void lireCommandesSerie() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("SET_CONSIGNE:")) {
      float val = cmd.substring(13).toFloat();
      if (val >= 10.0 && val <= 45.0) {
        setpoint = val;
      }
    } else if (cmd.startsWith("SET_AMBIANT:")) {
      float val = cmd.substring(12).toFloat();
      if (val >= -30.0 && val <= 60.0) {
        T0_celsius = val;
        T0 = T0_celsius + 273.15;
      }
    }
  }
}

// ===================== THERMISTANCES =====================
float lireThermistance(int pin) {
  float Vout = (5.0 / 1023.0) * analogRead(pin);
  float RT   = ((Rc + Re) * Rd * V2) / (Re * Vout + Rc * V1) - Rd;
  float TX   = 1.0 / ((log(RT / RT0) / B) + (1.0 / T0));
  return TX - 273.15;
}

// ===================== PWM =====================
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

// ===================== SETUP =====================
void setup() {
  Serial.begin(9600);
  T0 = T0_celsius + 273.15;  // ← utilise la valeur par défaut

  pinMode(pwmPin_CHAUD, OUTPUT);
  pinMode(pwmPin_FROID, OUTPUT);

  T2_prev = lireThermistance(adcPin);
  T3_prev = T2_prev;

  while (!Serial);
  delay(2000);

  // header CSV — 5 valeurs pour correspondre à Python (len(values) == 5)
  Serial.println("temps_s,T1,T2,T3_est,commande_u");
  tempsDebut = millis();
}

// ===================== LOOP =====================
void loop() {
  lireCommandesSerie();  // ← vérifie les commandes Python à chaque itération

  unsigned long now = millis();

  if (now - lastPID >= (unsigned long)(T_s * 1000)) {
    lastPID = now;

    // 1. Lire températures
    float T1 = lireThermistance(adcPin2);  // actuateur
    float T2 = lireThermistance(adcPin);   // thermistance principale

    // 2. Filtre estimateur T3
    T3_est  = 0.008635 * T2 + 0.008635 * T2_prev + 0.9806 * T3_prev;
    T2_prev = T2;
    T3_prev = T3_est;

    // 3. Erreur
    e[0] = setpoint - T3_est;

    // 4. Récurrence PID
    float u = u_prev + a0*e[0] + a1*e[1] + a2*e[2];

    // 5. Saturation + PWM
    envoyerPWM(u);

    // 6. Décaler états
    u_prev = constrain(u, -255, 255);
    e[2] = e[1];
    e[1] = e[0];

    // 7. Log → format attendu par Python : temps_s,T1,T2,T3_est,commande_u
    double t_s = (now - tempsDebut) / 1000.0;

    if (modeCSV && t_s < DUREE_ENREGISTREMENT) {
      Serial.print(t_s, 3);
      Serial.print(",");
      Serial.print(T1, 2);      // values[1]
      Serial.print(",");
      Serial.print(T2, 2);      // values[2]
      Serial.print(",");
      Serial.print(T3_est, 2);  // values[3]
      Serial.print(",");
      Serial.println(u, 2);     // values[4]
    } else if (modeCSV) {
      Serial.println("FIN");
      modeCSV = false;
    }
  }
}