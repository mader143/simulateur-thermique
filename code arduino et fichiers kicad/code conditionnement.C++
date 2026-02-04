#define RT0 10000
#define B   3984
#define R   10000

const int adcPin = A0;

// PWM output pins
const int pwmPin13 = 13;
const int pwmPin12 = 12; 

// Changement de duty cycle ICI (constante entre 0 et 255)
const int pwmValue13 = 40;
const int pwmValue12 = 40;

// DURÉE D'ENREGISTREMENT CSV EN SECONDES
const unsigned long DUREE_ENREGISTREMENT = 20; // Modifiez cette valeur selon vos besoins

float RT, VR, TX, T0, Rf, R1, Rg, V1, V2;
float Vout, Vin, VRT;
unsigned long tempsDebut;
bool modeCSV = true;

void setup() {
  Serial.begin(9600);
  T0 = 25.0 + 273.15;
  Rf = 6100;
  Rg = 6100;
  R1 = 2000;
  V1 = 1.9;
  V2 = 4.9;
  
  pinMode(pwmPin13, OUTPUT);
  pinMode(pwmPin12, OUTPUT);

  analogWrite(pwmPin13, pwmValue13);
  analogWrite(pwmPin12, pwmValue12);
  
  while (!Serial) {
    ; // Attendre
  }
  
  delay(2000);
  
  // Envoyer l'en-tête CSV
  Serial.println("temps_s,temperature_C");
  
  tempsDebut = millis();
}

void loop() {
  unsigned long t_ms = millis();
  double t_s = (t_ms - tempsDebut) / 1000.0;
  
  // Lire la sortie de l'ampli
  Vout = (5.0 / 1023.0) * analogRead(adcPin);
  
  // Calculer la résistance
  RT = ((Rf + R1) * Rg * V2) / (R1 * Vout + Rf * V1) - Rg;
  
  // Calculer la température
  TX = 1.0 / ((log(RT / RT0) / B) + (1.0 / T0));
  TX = TX - 273.15;
  
  // Vérifier si on doit basculer du mode CSV au mode affichage normal
  if (modeCSV && t_s >= DUREE_ENREGISTREMENT) {
    Serial.println("FIN"); // Marqueur de fin pour le script Python
    delay(500);
    Serial.println("\n=== Mode affichage continu ===");
    Serial.println("Temps (s)\tTemp (°C)");
    Serial.println("----------------------------");
    modeCSV = false;
    tempsDebut = millis(); // Réinitialiser le chrono pour l'affichage continu
  }
  
  // Affichage selon le mode
  if (modeCSV) {
    // MODE CSV : pour enregistrement Python
    Serial.print(t_s, 3);
    Serial.print(",");
    Serial.println(TX, 4);
  } else {
    // MODE NORMAL : affichage lisible avec tabulations
    t_s = (millis() - tempsDebut) / 1000.0;
    Serial.print(t_s, 3);
    Serial.print("\t\t");
    Serial.println(TX, 4);
  }
  
  delay(500);
}
