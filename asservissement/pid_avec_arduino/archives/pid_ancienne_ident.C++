// ===================== PWM =====================
const int pwmPin_CHAUD = 5;   // PWM+ → chauffe
const int pwmPin_FROID = 11;  // PWM- → refroidit

// ===================== PID DISCRET =====================
const float T_s = 0.5;    // Période échantillonnage (s)
float setpoint  = 30.0;   // Consigne température °C

// Coefficients PID discrets
const float a0 =  10.86;
const float a1 = -10.84;
const float a2 =  0;

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
  {A3, 6300, 5600, 3300, 1.774, 5.0, 3700},  // therm[0] → T1
  {A2, 6300, 5600, 3300, 1.80,  5.0, 3984},  // therm[1] → T2
  {A1, 6300, 5600, 3300, 1.79,  5.0, 3700},  // therm[2] → T3
};

float T0;  // température de référence en Kelvin

// ===================== FILTRE D'ÉTAT — estimateur T3 depuis T2 =====================
float T2_prev    = 0.0;
float T3_est     = 0.0;   // estimation T3 depuis T2
float T3_prev    = 0.0;

// ===================== FILTRE D'ÉTAT — estimateur T3 depuis T1 =====================
// Gz = (0.002823 + 0.002823·z^-1) / (1 - 0.9915·z^-1)
// Récurrence : T3_est_T1[k] = 0.9915·T3_est_T1[k-1] + 0.002823·T1[k] + 0.002823·T1[k-1]
float T1_prev        = 0.0;
float T3_est_T1      = 0.0;  // estimation T3 depuis T1
float T3_est_T1_prev = 0.0;

// ===================== VARIABLES D'ÉTAT PID =====================
float e[3]   = {0, 0, 0};
float u_prev = 0.0;

// ===================== CSV / LOG =====================
const unsigned long DUREE_ENREGISTREMENT = 1000;  // secondes
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

  while (!Serial);
  delay(2000);

  // Initialisation filtre d'état depuis T2
  T2_prev = mesureTemperature(therm[1]);
  T3_prev = T2_prev;
  T3_est  = T2_prev;

  // Initialisation filtre d'état depuis T1
  float T1_init    = mesureTemperature(therm[0]);
  T1_prev          = T1_init;
  T3_est_T1        = T1_init;
  T3_est_T1_prev   = T1_init;

  Serial.println("temps_s,T1_C,T2_C,T3_C,T3_est_T2,T3_est_T1,T3_fused,erreur,commande_u");
  tempsDebut = millis();
}


// =====================================================
// LOOP
// =====================================================
void loop() {
  unsigned long now = millis();

  // PID cadencé à T_s
  if (now - lastPID >= (unsigned long)(T_s * 1000)) {
    lastPID = now;

    // 1. Lecture des 3 thermistances
    float T[3];
    for (int i = 0; i < 3; i++) {
      T[i] = mesureTemperature(therm[i]);
    }

    // 2a. Filtre d'état sur T2 → estimation T3
    T3_est  = 0.008635 * T[1] + 0.008635 * T2_prev + 0.9806 * T3_prev;
    T2_prev = T[1];
    T3_prev = T3_est;

    // 2b. Filtre d'état sur T1 → estimation T3
    // Gz = (0.002823 + 0.002823·z^-1) / (1 - 0.9915·z^-1)
    T3_est_T1      = 0.9915 * T3_est_T1_prev
                   + 0.002823 * T[0]
                   + 0.002823 * T1_prev;
    T1_prev        = T[0];
    T3_est_T1_prev = T3_est_T1;

    // 2c. Fusion : moyenne des deux estimations
    float T3_fused = (T3_est + T3_est_T1) / 2.0;

    // 3. Erreur PID sur T3 fusionnée
    e[0] = setpoint - T3_fused;

    // 4. Récurrence PID
    float u = u_prev + a0 * e[0] + a1 * e[1] + a2 * e[2];

    // 5. Saturation + PWM
    envoyerPWM(u);

    // 6. Décaler états
    u_prev = constrain(u, -255, 255);
    e[2]   = e[1];
    e[1]   = e[0];

    // 7. Log CSV
    double t_s = (now - tempsDebut) / 1000.0;

    if (modeCSV && t_s < DUREE_ENREGISTREMENT) {
      Serial.print(t_s, 3);
      Serial.print(",  ");
      Serial.print(T[0], 2);        // T1 mesurée
      Serial.print(",  ");
      Serial.print(T[1], 2);        // T2 mesurée
      Serial.print(",  ");
      Serial.print(T[2], 2);        // T3 mesurée
      Serial.print(",  ");
      Serial.print(T3_est, 2);      // T3 estimée depuis T2
      Serial.print(",  ");
      Serial.print(T3_est_T1, 2);   // T3 estimée depuis T1
      Serial.print(",  ");
      Serial.print(T3_fused, 2);    // T3 fusionnée (moyenne)
      Serial.print(",  ");
      Serial.print(e[1], 4);        // erreur
      Serial.print(",  ");
      Serial.println(constrain(u, -255, 255), 2);  // commande

    } else if (modeCSV) {
      Serial.println("FIN");
      modeCSV = false;
    }
  }
}
