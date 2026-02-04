
const int tecPin = A1;

// PWM output pins
const int pwmPin13 = 13;
const int pwmPin12 = 12; 

// Changement de duty cycle ICI (constante entre 0 et 255)
const int pwmValue13 = 40;
const int pwmValue12 = 40;

float Vout;


void setup() {  Serial.begin(9600);
  
  pinMode(pwmPin13, OUTPUT);
  pinMode(pwmPin12, OUTPUT);

  analogWrite(pwmPin13, pwmValue13);
  analogWrite(pwmPin12, pwmValue12);
  
}

void loop() {

  Vout = (5.0 / 1023.0) * analogRead(tecPin);
    Serial.println(Vout, 4);
  }
  
  delay(500);
}
