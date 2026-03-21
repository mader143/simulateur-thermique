#include <Arduino.h>
// Code updaté qui détermine si on prend le PID chaud ou froid
// ===================== PWM =====================
const int pwmPin_CHAUD = 5;
const int pwmPin_FROID = 11;

int pwm_1 = 0;
int pwm_2 = 0;

// ===================== CONSIGNE =====================
float setpoint = 20;




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
  {A3, 3300, 5600, 3300, 1.774, 5.0, 3700},
  {A2, 6300, 5600, 3300, 1.80,  5.0, 3984},
  {A1, 6300, 5600, 3300, 1.79,  5.0, 3700},
};




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
  Serial.println(Vout);
  float RT = ((t.Rf + t.R1) * t.Rg * t.V2) /
             (t.R1 * Vout + t.Rf * t.V1) - t.Rg;
  float TX = 1.0 / ((log(RT / RT0) / t.B) + (1.0 / T0));
  return TX - 273.15;
}


// =====================================================
// ENVOI PWM CHAUD / FROID
// =====================================================
void envoyerPWM() {
   analogWrite(pwmPin_CHAUD, (int) pwm_1);
   analogWrite(pwmPin_FROID, (int) pwm_2);
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

  tempsDebut = millis();
}


// =====================================================
// LOOP
// =====================================================
void loop() {
  unsigned long now = millis();

  if (now - lastPID >= 500UL) {
    lastPID = now;

    float T1 = mesureTemperature(therm[0]);
    float T2 = mesureTemperature(therm[1]);
    float T3 = mesureTemperature(therm[2]);

    envoyerPWM();


    double t_s = (now - tempsDebut) / 1000.0;

    if (modeCSV && t_s < DUREE_ENREGISTREMENT) {
      Serial.print(t_s, 3);
      Serial.print(", T1: "); Serial.print(T1, 2);
      Serial.print(", T2: "); Serial.print(T2, 2);
      Serial.print(", T3: "); Serial.print(T3, 2);

    } else if (modeCSV) {
      Serial.println("FIN");
      modeCSV = false;
    }
  }
}