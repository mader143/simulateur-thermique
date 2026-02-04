#define RT0 10000
#define B   3984
#define R   10000

const int adcPin = A0;

// PWM output pins
const int pwmPin50 = 13;
const int pwmPin10 = 12;  


float RT, VR, TX, T0, Rf,R1, Rg, V1, V2;
float Vout, Vin, VRT;

void setup() {
  Serial.begin(9600);
  T0 = 25.0 + 273.15;
  Rf=6100;
  Rg=6100;
  R1=2000;
  V1=1.9;
  V2=4.9;
  
  pinMode(pwmPin50, OUTPUT);
  pinMode(pwmPin10, OUTPUT);

  analogWrite(pwmPin50, 50);
  analogWrite(pwmPin10, 26);
}

void loop() {
  // 1) Lire la sortie de l'ampli (ATTENTION: doit être 0..5V pour l'UNO)
  Vout = (5.0 / 1023.0) * analogRead(adcPin);


  RT = ((Rf + R1) * Rg * V2) / (R1 * Vout + Rf * V1) - Rg;


  TX = 1.0 / ((log(RT / RT0) / B) + (1.0 / T0));
  TX = TX - 273.15;


  unsigned long t_ms = millis();
  double t_s = t_ms / 1000.0;

  Serial.print(t_s, 3);    // temps en secondes (3 décimales)
  Serial.print('\t');      // séparateur (tab)
  Serial.println(TX, 4); // température en °C


  delay(500);
}