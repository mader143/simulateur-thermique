#define RT0 10000
#define B   3984

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
};

// =====================================================
// >>>>>>> PARAMÈTRES DES THERMISTANCES <<<<<<<
// =====================================================
Thermistance therm[3] = {

  // Thermistance 1
  {A3, 5082.4 + 998.88, 5088.6 + 998.2, 3300, 1.900, 5.01},

  // Thermistance 2
  {A2, 5082.4 + 998.88, 5088.6 + 998.2, 3300, 1.900, 5.01},

  // Thermistance 3 
  {A1, 5082.4 + 998.88, 5088.6 + 998.2, 3300, 1.900, 5.01}
};


// PWM output pins
const int pwmPin5 = 5;
const int pwmPin11 = 11;

const int pwmValue5 = 0;
const int pwmValue11 = 0;

const unsigned long DUREE_ENREGISTREMENT = 800;

float T0;
unsigned long tempsDebut;
bool modeCSV = true;


// =====================================================
// FONCTION MESURE TEMPERATURE
// =====================================================
float mesureTemperature(Thermistance t)
{
  float Vout = (5.0 / 1023.0) * analogRead(t.pin);

  float RT = ((t.Rf + t.R1) * t.Rg * t.V2) /
             (t.R1 * Vout + t.Rf * t.V1) - t.Rg;

  float T = 1.0 / ((log(RT / RT0) / B) + (1.0 / T0));

  return T - 273.15;
}


// =====================================================
void setup() {

  Serial.begin(9600);

  T0 = 25.0 + 273.15;

  pinMode(pwmPin5, OUTPUT);
  pinMode(pwmPin11, OUTPUT);

  analogWrite(pwmPin5, pwmValue5);
  analogWrite(pwmPin11, pwmValue11);

  while (!Serial) {}

  delay(2000);

  Serial.println("temps_s,T1_C,T2_C,T3_C");

  tempsDebut = millis();
}


// =====================================================
void loop() {

  double t_s = (millis() - tempsDebut) / 1000.0;

  // ===== Lecture automatique des 3 thermistances =====
  float T[3];

  for (int i = 0; i < 3; i++) {
    T[i] = mesureTemperature(therm[i]);
  }

  // ===== Changement de mode =====
  if (modeCSV && t_s >= DUREE_ENREGISTREMENT) {
    Serial.println("FIN");
    delay(500);
    Serial.println("\n=== Mode affichage continu ===");
    Serial.println("Temps(s)\tT1\tT2\tT3");
    Serial.println("--------------------------------");
    modeCSV = false;
    tempsDebut = millis();
  }

  // ===== Affichage =====
  if (modeCSV) {

    Serial.print(t_s, 3);
    for (int i = 0; i < 3; i++) {
      Serial.print(",");
      Serial.print(T[i], 2);
    }
    Serial.println();

  } else {

    t_s = (millis() - tempsDebut) / 1000.0;

    Serial.print(t_s, 3);
    Serial.print(", \t");
    Serial.print(T[0], 2);
    Serial.print(", \t");
    Serial.print(T[1], 2);
    Serial.print(", \t");
    Serial.println(T[2], 2);
  }

  delay(500);
}
