#include <PID_v1.h>
#include <math.h>

// ============================================================
//                   PARAMÈTRES THERMISTOR
// ============================================================
const double THERMISTOR_R0_OHM = 10000.0;   // RT0 (Ω)
const double THERMISTOR_BETA   = 3984.0;    // B
const double T0_KELVIN         = 25.0 + 273.15; // 25°C en Kelvin

// ============================================================
//                      PINS ARDUINO
// ============================================================
const int BROCHE_ADC_TEMP = A0;

// Deux PWM vers ton PCB (pont en H + contrôle Peltier)
// Règle : si PWM12 > PWM13 => chauffe ; si PWM13 > PWM12 => refroidit
const int BROCHE_PWM_A = 5; // PWM A
const int BROCHE_PWM_B = 11; // PWM B

// ============================================================
//                   PARAMÈTRES DU MONTAGE 
// ============================================================
const double rf_ohm  = 6100.0;
const double rg_ohm  = 6100.0;
const double r1_ohm  = 2000.0;
const double v1_volt = 1.9;
const double v2_volt = 4.9;

// ============================================================
//                     VARIABLES MESURE
// ============================================================
double vout_volt     = 0.0;   // tension lue sur A0
double rt_ohm        = 0.0;   // résistance thermistor calculée
double temperature_c = 0.0;   // température calculée (°C)

// ============================================================
//                       VARIABLES PID 
// ============================================================
double consigne_c  = 100.0;   // Setpoint
double entree_c    = 0.0;     // Input  (température mesurée)
double sortie_pid  = 0.0;     // Output (signé)

// Paramètres PID agressifs / conservateurs (identiques à ton code)
double aggKp = 4,   aggKi = 0.2,  aggKd = 1;
double consKp = 1,  consKi = 0.05, consKd = 0.25;

// PID en DIRECT : si consigne > température => sortie augmente
PID monPID(&entree_c, &sortie_pid, &consigne_c, consKp, consKi, consKd, DIRECT);

// ============================================================
//                         PWM CENTRÉ
// ============================================================
const int PWM_CENTRE = 127;

// Zone morte autour de la consigne pour éviter le pompage (en °C)
// Mettre à 0.0 pour enlever
const double ZONE_MORTE_C = 0.3;

// Limite du "delta" appliqué autour du centre, pour éviter saturation totale
// (255 permet max; tu peux réduire si ton PCB/driver préfère)
const int DELTA_MAX = 255;

// ------------------------------------------------------------
// Lecture température 
// ------------------------------------------------------------
static double lire_temperature_c()
{
  int adc = analogRead(BROCHE_ADC_TEMP);
  vout_volt = (5.0 / 1023.0) * adc;

  // Formule résistance de la thermistance
  rt_ohm = ((rf_ohm + r1_ohm) * rg_ohm * v2_volt) / (r1_ohm * vout_volt + rf_ohm * v1_volt) - rg_ohm;

  // Conversion Beta
  double temp_k = 1.0 / ((log(rt_ohm / THERMISTOR_R0_OHM) / THERMISTOR_BETA) + (1.0 / T0_KELVIN));
  return temp_k - 273.15;
}

// ------------------------------------------------------------
// Application PWM centré vers ton PCB
// si A > B => chauffe ; si B > A => refroidit
//
// Crée deux PWM autour du centre :
//   delta > 0 => A = centre + delta/2, B = centre - delta/2  => A>B => chauffe
//   delta < 0 => A<B => refroidit
// ------------------------------------------------------------
static void appliquer_pwm_centre(double u_signe)
{
  // Clamp du PID
  if (u_signe >  DELTA_MAX) u_signe =  DELTA_MAX;
  if (u_signe < -DELTA_MAX) u_signe = -DELTA_MAX;

  // On utilise "delta" comme différence autour du centre
  int delta = (int)u_signe;

  int pwm_a = PWM_CENTRE + (delta / 2);
  int pwm_b = PWM_CENTRE - (delta / 2);

  // Saturation 0..255
  pwm_a = constrain(pwm_a, 0, 255);
  pwm_b = constrain(pwm_b, 0, 255);

  analogWrite(BROCHE_PWM_A, pwm_a);
  analogWrite(BROCHE_PWM_B, pwm_b);

  // Debug rapide
  // Serial.print("PWM_A="); Serial.print(pwm_a);
  // Serial.print(" PWM_B="); Serial.println(pwm_b);
}

void setup()
{
  Serial.begin(9600);

  pinMode(BROCHE_PWM_A, OUTPUT);
  pinMode(BROCHE_PWM_B, OUTPUT);

  // Réglages PID
  monPID.SetMode(AUTOMATIC);

  // À cause du delay(500), sample time cohérent
  monPID.SetSampleTime(500);

  // Sortie signée pour gérer chauffe/refroidit
  monPID.SetOutputLimits(-DELTA_MAX, DELTA_MAX);

  // Au démarrage : neutre (centre/centre)
  analogWrite(BROCHE_PWM_A, PWM_CENTRE);
  analogWrite(BROCHE_PWM_B, PWM_CENTRE);
}

void loop()
{
  // 1) Mesure température
  temperature_c = lire_temperature_c();
  entree_c = temperature_c; //  PID travaille sur la température

  // 2) Choix des gains 
  double ecart = fabs(consigne_c - temperature_c);
  if (ecart < 1.0) {
    monPID.SetTunings(consKp, consKi, consKd);
  } else {
    monPID.SetTunings(aggKp, aggKi, aggKd);
  }

  // 3) Calcul PID
  monPID.Compute();

  // 4) Zone morte anti-pompage (optionnelle)
  if (fabs(consigne_c - temperature_c) <= ZONE_MORTE_C) {
    sortie_pid = 0.0; // revient au neutre => centre/centre
  }

  // 5) Application vers le PCB (PWM centré)
  appliquer_pwm_centre(sortie_pid);

  // 6) Affichage
  Serial.print("Temp (C) : ");
  Serial.println(temperature_c);

  Serial.print("Resistance RT (ohm) : ");
  Serial.println(rt_ohm);

  Serial.print("Tension Vout (V) : ");
  Serial.println(vout_volt);

  Serial.print("Sortie PID (delta) : ");
  Serial.println(sortie_pid);

  Serial.println("----");
  delay(500);
}
``