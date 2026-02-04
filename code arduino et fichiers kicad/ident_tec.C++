
const int tecPin = A1;

// PWM output pins
const int pwmPin5 = 5;
const int pwmPin11 = 11; 

// Changement de duty cycle ICI (constante entre 0 et 255)
const int pwmValue5 = 40;
const int pwmValue11 = 40;

float Vout;


void setup() {  Serial.begin(9600);
  
  pinMode(pwmPin5, OUTPUT);
  pinMode(pwmPin11, OUTPUT);

  analogWrite(pwmPin5, pwmValue5);
  analogWrite(pwmPin11, pwmValue11);
  
}

void loop() {

  Vout = (5.0 / 1023.0) * analogRead(tecPin);
    Serial.println(Vout, 4);
  
  
  delay(500);
}
