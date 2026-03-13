#define RT0 10000

// =====================================================
// STRUCTURE THERMISTANCE
// =====================================================
struct Thermistance {
  int pin;
  float Rf;
  float Rg;
  float R1;
  float V1;
  float V2;
  float B;
};

// =====================================================
// PARAMÈTRES DES THERMISTANCES
// =====================================================
Thermistance therm[3] = {
  {A3, 6300, 5600, 3300, 1.774, 5.0, 3700},  // T1
  {A2, 6300, 5600, 3300, 1.80,  5.0, 3984},  // T2
  {A1, 6300, 5600, 3300, 1.79,  5.0, 3700},  // T3
};

// =====================================================
// PARAMÈTRES MODÈLES D'ESTIMATION
// y[k] = b0*u[k] + b1*u[k-1] - a1*y[k-1]
// =====================================================
const float G1_b0 =  0.002432;
const float G1_b1 =  0.002432;
const float G1_a1 = -0.9926;

const float G2_b0 =  0.009158;
const float G2_b1 =  0.009158;
const float G2_a1 = -0.98;

// =====================================================
// PWM — CONTRÔLE MANUEL
// =====================================================
const int pwmPin5  = 5;
const int pwmPin11 = 11;
const int pwmValue5  = 0;   // 0–255
const int pwmValue11 = 0;   // 0–255

// =====================================================
// DURÉE ENREGISTREMENT
// =====================================================
const unsigned long DUREE_ENREGISTREMENT = 800;  // secondes

// =====================================================
// VARIABLES GLOBALES
// =====================================================
float T0;
unsigned long tempsDebut;
bool modeCSV = true;

float T1_init = 0.0;
float T2_init = 0.0;
float T3_init = 0.0;

float u1_prev = 0.0;
float y1_prev = 0.0;
float u2_prev = 0.0;
float y2_prev = 0.0;


// =====================================================
// FONCTION MESURE TEMPÉRATURE
// =====================================================
float mesureTemperature(Thermistance t) {
  float Vout = (5.0 / 1023.0) * analogRead(t.pin);

  float RT = ((t.Rf + t.R1) * t.Rg * t.V2) /
             (t.R1 * Vout + t.Rf * t.V1) - t.Rg;

  float T = 1.0 / ((log(RT / RT0) / t.B) + (1.0 / T0));

  return T - 273.15;
}


// =====================================================
// SETUP
// =====================================================
void setup() {
  Serial.begin(9600);

  T0 = 25.0 + 273.15;

  pinMode(pwmPin5,  OUTPUT);
  pinMode(pwmPin11, OUTPUT);
  analogWrite(pwmPin5,  pwmValue5);
  analogWrite(pwmPin11, pwmValue11);

  while (!Serial) {}
  delay(2000);

  // Capture état initial
  T1_init = mesureTemperature(therm[0]);
  T2_init = mesureTemperature(therm[1]);
  T3_init = mesureTemperature(therm[2]);

  u1_prev = 0.0;
  y1_prev = 0.0;
  u2_prev = 0.0;
  y2_prev = 0.0;

  Serial.println("temps_s,T1_C,T2_C,T3_mesuree,T3_estimT2,T3_estimT1,T3_moy");

  tempsDebut = millis();
}


// =====================================================
// LOOP
// =====================================================
void loop() {
  double t_s = (millis() - tempsDebut) / 1000.0;

  // ── Lecture des 3 thermistances ──
  float T1 = mesureTemperature(therm[0]);
  float T2 = mesureTemperature(therm[1]);
  float T3 = mesureTemperature(therm[2]);

  // ── Écarts par rapport à l'état initial ──
  float dT1 = T1 - T1_init;
  float dT2 = T2 - T2_init;

  // ── Estimation en écarts ──
  float dT3_estimT1 = G1_b0 * dT1 + G1_b1 * u1_prev - G1_a1 * y1_prev;
  float dT3_estimT2 = G2_b0 * dT2 + G2_b1 * u2_prev - G2_a1 * y2_prev;

  // ── Températures absolues estimées ──
  float T3_estimT1 = T3_init + dT3_estimT1;
  float T3_estimT2 = T3_init + dT3_estimT2;
  float T3_moy     = (T3_estimT1 + T3_estimT2) / 2.0;

  // ── Mise à jour états ──
  u1_prev = dT1;
  y1_prev = dT3_estimT1;
  u2_prev = dT2;
  y2_prev = dT3_estimT2;

  // ── Changement de mode ──
  if (modeCSV && t_s >= DUREE_ENREGISTREMENT) {
    Serial.println("FIN");
    delay(500);
    Serial.println("\n=== Mode affichage continu ===");
    Serial.println("Temps(s)\tT1\tT2\tT3\tT3_estT2\tT3_estT1\tT3_moy");
    Serial.println("--------------------------------------------------");
    modeCSV = false;
    tempsDebut = millis();
  }

  // ── Affichage ──
  if (modeCSV) {
    Serial.print(t_s, 3);
    Serial.print(","); Serial.print(T1, 2);
    Serial.print(","); Serial.print(T2, 2);
    Serial.print(","); Serial.print(T3, 2);
    Serial.print(","); Serial.print(T3_estimT2, 2);
    Serial.print(","); Serial.print(T3_estimT1, 2);
    Serial.print(","); Serial.println(T3_moy, 2);

  } else {
    t_s = (millis() - tempsDebut) / 1000.0;
    Serial.print(t_s, 3);
    Serial.print("\t"); Serial.print(T1, 2);
    Serial.print("\t"); Serial.print(T2, 2);
    Serial.print("\t"); Serial.print(T3, 2);
    Serial.print("\t"); Serial.print(T3_estimT2, 2);
    Serial.print("\t"); Serial.print(T3_estimT1, 2);
    Serial.print("\t"); Serial.println(T3_moy, 2);
  }

  delay(500);
}