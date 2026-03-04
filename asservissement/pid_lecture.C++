// ===================== THERMISTANCE =====================
#define RT0 10000
#define B   3980
#define R   10000

const int adcPin = A3;

// ===================== PWM =====================
const int pwmPin_CHAUD = 2;   // PWM+ → chauffe
const int pwmPin_FROID = 11;  // PWM- → refroidit

// ===================== PID DISCRET ===================== trouver manière de prendre le setpoint d'une interface de l'usager
const float T_s = 0.5;          // Période échantillonnage (doit matcher Simulink!)
const float setpoint = 28.0;    // Consigne température °C

// ⚠️ Remplacer ces coefficients par ceux extraits de Simulink
const float a0 =  1.5;
const float a1 = -1.2;
const float a2 =  0.3;

// ===================== CIRCUIT AMPLI =====================
float Rc = 3300, Rd = 5600, Re = 6300;
float V1 = 1.795, V2 = 5.0;
float T0;

// ===================== VARIABLES D'ÉTAT PID =====================
float e[3]  = {0, 0, 0};   // e[k], e[k-1], e[k-2]
float u_prev = 0;

// ===================== CSV =====================
const unsigned long DUREE_ENREGISTREMENT = 1000;
unsigned long tempsDebut;
bool modeCSV = true;

// ===================== TIMING =====================
unsigned long lastPID = 0;

// ========================================== à vérifier pour le -255 et 255
float lireThermistance() {
  float Vout = (5.0 / 1023.0) * analogRead(adcPin);
  float RT = ((Rc + Re) * Rd * V2) / (Re * Vout + Rc * V1) - Rd;
  float TX = 1.0 / ((log(RT / RT0) / B) + (1.0 / T0));
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

    // 2. Erreur
    e[0] = setpoint - T2;

    // 3. Récurrence PID
    float u = u_prev + a0*e[0] + a1*e[1] + a2*e[2];

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
      Serial.print(e[0], 2);
      Serial.print(",");
      Serial.println(u, 2);
    } else if (modeCSV) {
      Serial.println("FIN");
      modeCSV = false;
    }
  }
}