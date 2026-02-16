#define RT0 10000
#define B   3984
#define R   10000

// === PINS ADC ===
const int adcPin1 = A0;
const int adcPin2 = A1;
const int adcPin3 = A2;

// PWM output pins
const int pwmPin5 = 5;
const int pwmPin11 = 11;

// Duty cycles
const int pwmValue5 = 35;
const int pwmValue11 = 55;

// DURÉE D'ENREGISTREMENT CSV (s)
const unsigned long DUREE_ENREGISTREMENT = 240;

float RT, TX, T0, Rf, R1, Rg, V1, V2;
float Vout;

unsigned long tempsDebut;
bool modeCSV = true;


// =====================================================
// FONCTION MESURE TEMPERATURE
// =====================================================
float mesureTemperature(int adcPin)
{
  // Lecture ADC
  Vout = (5.0 / 1023.0) * analogRead(adcPin);

  // Calcul résistance thermistance
  RT = ((Rf + R1) * Rg * V2) / (R1 * Vout + Rf * V1) - Rg;

  // Loi Beta
  float T = 1.0 / ((log(RT / RT0) / B) + (1.0 / T0));
  T = T - 273.15;

  return T;
}


// =====================================================
void setup() {

  Serial.begin(9600);

  T0 = 25.0 + 273.15;
  Rf = 5082.4 + 998.88;
  Rg = 5088.6 + 998.2;
  R1 = 1988.1;
  V1 = 1.900;
  V2 = 5.01;

  pinMode(pwmPin5, OUTPUT);
  pinMode(pwmPin11, OUTPUT);

  analogWrite(pwmPin5, pwmValue5);
  analogWrite(pwmPin11, pwmValue11);

  while (!Serial) {}

  delay(2000);

  // Header CSV
  Serial.println("temps_s,T1_C,T2_C,T3_C");

  tempsDebut = millis();
}


// =====================================================
void loop() {

  unsigned long t_ms = millis();
  double t_s = (t_ms - tempsDebut) / 1000.0;

  // === MESURES ===
  float T1 = mesureTemperature(adcPin1);
  float T2 = mesureTemperature(adcPin2);
  float T3 = mesureTemperature(adcPin3);

  // Passage mode affichage
  if (modeCSV && t_s >= DUREE_ENREGISTREMENT) {
    Serial.println("FIN");
    delay(500);
    Serial.println("\n=== Mode affichage continu ===");
    Serial.println("Temps(s)\tT1\tT2\tT3");
    Serial.println("--------------------------------");
    modeCSV = false;
    tempsDebut = millis();
  }

  // === AFFICHAGE ===
  if (modeCSV) {
    // CSV pour Python
    Serial.print(t_s, 3);
    Serial.print(",");
    Serial.print(T1, 2);
    Serial.print(",");
    Serial.print(T2, 2);
    Serial.print(",");
    Serial.println(T3, 2);
  }
  else {
    t_s = (millis() - tempsDebut) / 1000.0;

    Serial.print(t_s, 3);
    Serial.print("\t");
    Serial.print(T1, 2);
    Serial.print("\t");
    Serial.print(T2, 2);
    Serial.print("\t");
    Serial.println(T3, 2);
  }

  delay(500);
}
