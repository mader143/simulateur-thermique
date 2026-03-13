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
// PARAMÈTRES MODÈLES D'ESTIMATION (équation aux différences)
// y[k] = b0*u[k] + b1*u[k-1] - a1*y[k-1]
// =====================================================

// G3_1 : T3 estimé depuis T1
const float G1_b0 =  0.002432;
const float G1_b1 =  0.002432;
const float G1_a1 = -0.9926;

// G3_2 : T3 estimé depuis T2
const float G2_b0 =  0.009158;
const float G2_b1 =  0.009158;
const float G2_a1 = -0.98;

// =====================================================
// PWM — CONTRÔLE MANUEL (valeurs fixes)
// =====================================================
const int pwmPin5  = 5;
const int pwmPin11 = 11;
const int pwmValue5  = 0;    // 0–255
const int pwmValue11 = 0;    // 0–255

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

// États internes des filtres (équation aux différences)
float u1_prev = 0.0;   // T1[k-1]
float y1_prev = 0.0;   // T3_estimT1[k-1]

float u2_prev = 0.0;   // T2[k-1]
float y2_prev = 0.0;   // T3_estimT2[k-1]

bool premiereIteration = true;


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

  Serial.println("temps_s,T1_C,T2_C,T3_C,T3_estimT1,T3_estimT2");

  tempsDebut = millis();
}


// =====================================================
// LOOP
// =====================================================
void loop() {
  double t_s = (millis() - tempsDebut) / 1000.0;

  // ── Lecture des 3 thermistances ──
  float T[3];
  for (int i = 0; i < 3; i++) {
    T[i] = mesureTemperature(therm[i]);
  }

  float T1 = T[0];
  float T2 = T[1];
  float T3 = T[2];

  // ── Initialisation au premier passage ──
  if (premiereIteration) {
    u1_prev = T1;
    y1_prev = T3;
    u2_prev = T2;
    y2_prev = T3;
    premiereIteration = false;
  }

  // ── Estimation T3 depuis T1 (G3_1) ──
  float T3_estimT1 = G1_b0 * T1 + G1_b1 * u1_prev - G1_a1 * y1_prev;

  // ── Estimation T3 depuis T2 (G3_2) ──
  float T3_estimT2 = G2_b0 * T2 + G2_b1 * u2_prev - G2_a1 * y2_prev;

  // ── Mise à jour états précédents ──
  u1_prev = T1;
  y1_prev = T3_estimT1;
  u2_prev = T2;
  y2_prev = T3_estimT2;

  // ── Changement de mode ──
  if (modeCSV && t_s >= DUREE_ENREGISTREMENT) {
    Serial.println("FIN");
    delay(500);
    Serial.println("\n=== Mode affichage continu ===");
    Serial.println("Temps(s)\tT1\tT2\tT3\tT3_estT1\tT3_estT2");
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
    Serial.print(","); Serial.print(T3_estimT1, 2);
    Serial.print(","); Serial.println(T3_estimT2, 2);

  } else {
    t_s = (millis() - tempsDebut) / 1000.0;
    Serial.print(t_s, 3);
    Serial.print("\t"); Serial.print(T1, 2);
    Serial.print("\t"); Serial.print(T2, 2);
    Serial.print("\t"); Serial.print(T3, 2);
    Serial.print("\t"); Serial.print(T3_estimT1, 2);
    Serial.print("\t"); Serial.println(T3_estimT2, 2);
  }

  delay(500);
}