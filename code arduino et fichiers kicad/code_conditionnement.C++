#define RT0 10000
#define B   3980
#define R   10000

const int adcPin = A3;

// PWM output pins
const int pwmPin2 = 2;
const int pwmPin11 = 11; 

// Changement de duty cycle ICI (constante entre 0 et 255)
const int pwmValue2 = 128;
const int pwmValue11 = 128;

// DURÉE D'ENREGISTREMENT CSV EN SECONDES
const unsigned long DUREE_ENREGISTREMENT = 1000; // Modifiez cette valeur selon vos besoins

float RT, VR, TX, T0, Rc, Re, Rd, V1, V2;
float Vout, Vin, VRT;
unsigned long tempsDebut;
bool modeCSV = true;

void setup() {
  Serial.begin(9600);
  T0 = 25.0 + 273.15;
  Rc = 3300;
  Rd = 5600;
  Re = 6300;
  V1 = 1.795;
  V2 = 5.0;
  
  pinMode(pwmPin2, OUTPUT);
  pinMode(pwmPin11, OUTPUT);

  analogWrite(pwmPin2, pwmValue2);
  analogWrite(pwmPin11, pwmValue11);
  
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
  RT = ((Rc + Re) * Rd * V2) / (Re * Vout + Rc * V1) - Rd;
  
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
    Serial.println(TX, 2);
  } else {
    // MODE NORMAL : affichage lisible avec tabulations
    t_s = (millis() - tempsDebut) / 1000.0;
    Serial.print(t_s, 3);
    Serial.print("\t\t");
    Serial.println(TX, 2);
  }
  
  delay(500);
}