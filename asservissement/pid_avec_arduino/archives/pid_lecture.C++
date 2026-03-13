// ===================== THERMISTANCE =====================
#define RT0 10000
#define B   3980
#define R   10000

const int adcPin3 = A1;
const int adcPin2 = A2;
const int adcPin1 = A3;

// ===================== PWM =====================
const int pwmPin_CHAUD = 5;   // PWM+ → chauffe
const int pwmPin_FROID = 11;  // PWM- → refroidit

// ===================== PID DISCRET ===================== trouver manière de prendre le setpoint d'une interface de l'usager
const float T_s = 0.5;          // Période échantillonnage (doit matcher Simulink!)
const float setpoint = 28.0;    // Consigne température °C

// ⚠️ Remplacer ces coefficients par ceux extraits de Simulink
const float a0 =  8.765;  // K_c, a tester: 10.849
const float a1 = -8.595;  // T_i, a tester: 120
const float a2 =  0.0;    // T_d, a tester: 16
float T2_prev; // température mesurée à l'itération précédente
float T3_est;
float T3_prev;

// ===================== CIRCUIT AMPLI =====================
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
// >>>>>>> PARAMÈTRES DES THERMISTANCES <<<<<<<
// =====================================================
Thermistance therm[3] = {

  // Thermistance 1
  {A3, 6300, 5600, 3300, 1.774, 5.0, 3700},

  // Thermistance 2
  {A2, 6300, 5600, 3300, 1.80, 5.0, 3984},

  // Thermistance 3 
  {A1, 6300, 5600, 3300, 1.79, 5.0, 3700},
};
float T0;

// ===================== VARIABLES D'ÉTAT PID =====================
float e[3]  = {0, 0, 0};
float u_unsat = 0;   // commande non saturée
float u_prev  = 0;   // commande saturée (utilisée dans la récurrence)

// Gain anti-windup (à ajuster, typiquement 1/a0)
const float Ka = 0.5;

// ===================== CSV =====================
const unsigned long DUREE_ENREGISTREMENT = 1000;
unsigned long tempsDebut;
bool modeCSV = true;

// ===================== TIMING =====================
unsigned long lastPID = 0;

// ========================================== à vérifier pour le -255 et 255
float lireThermistance() {
  float Vout = (5.0 / 1023.0) * analogRead(t.pin);

  float RT = ((t.Rf + t.R1) * t.Rg * t.V2) /
             (t.R1 * Vout + t.Rf * t.V1) - t.Rg;

  float TX = 1.0 / ((log(RT / RT0) / t.B) + (1.0 / T0));

  return TX - 273.15;
}

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

// ==========================================
void setup() {
  Serial.begin(9600);
  T0 = 25.0 + 273.15;

  pinMode(pwmPin_CHAUD, OUTPUT);
  pinMode(pwmPin_FROID, OUTPUT);

float T[3];

  for (int i = 0; i < 3; i++) {
    T[i] = lireThermistance(therm[i]);
  }

  float T2_prev = lireThermistance(therm[2]); // température mesurée à l'itération précédente
  float T3_prev = T2_prev;

  while (!Serial);
  delay(2000);


  Serial.println("temps_s,temperature_C,erreur,commande_u");
  tempsDebut = millis();
}

// ========================================== checker ce qu'on doit faire afficher dans graphique
void loop() {
  unsigned long now = millis();

  // PID cadencé à T_s secondes
  if (now - lastPID >= (unsigned long)(T_s * 1000)) {
    lastPID = now;

    // 1. Lire température
    float T2 = lireThermistance();
  
    T3_est = 0.008635 * T2 + 0.008635 * T2_prev + 0.9806 * T3_prev; //
    T2_prev = T2; // température mesurée à l'itération précédente

    T3_prev = T3_est; // température estimée à l'itération précédente

    // 2. Erreur
    e[0] = setpoint - T3_est;

    // 3. Récurrence PID
    float u = u_prev + a0*e[0] + a1*e[1]+ a2*e[2];  // 
    // 4. Saturation + PWM
    envoyerPWM(u);

    // 5. Décaler états
    u_prev = constrain(u, -255, 255); // anti-windup simple
    e[2] = e[1];
    e[1] = e[0];

    // 6. Log
    double t_s = (now - tempsDebut) / 1000.0;

    if (modeCSV && t_s < DUREE_ENREGISTREMENT) {
      Serial.print(t_s, 3);
      Serial.print(",");
      Serial.print(T2, 2);
      Serial.print(",");
      Serial.print(T3_est, 2);
      Serial.print(",");
      Serial.println(u, 2);
    } else if (modeCSV) {
      Serial.println("FIN");
      modeCSV = false;
    }
  }
}