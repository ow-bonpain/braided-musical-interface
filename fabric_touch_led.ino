int sensorPin = A0;
int secSensorPin = A1;
long sensorValue, secSensorValue;
const int ledPin = 13;   

long readCapacitiveSensor(int samples, int sensorPin) {
  long total = 0;

  for (int i = 0; i < samples; i++) {
    // Discharge pin
    pinMode(sensorPin, OUTPUT);
    digitalWrite(sensorPin, LOW);
    delayMicroseconds(1);

    // Set pin to input and measure charge time
    pinMode(sensorPin, INPUT);
    long start = micros();
    while (digitalRead(sensorPin) == LOW) {
      if ((micros() - start) > 3000) break; // timeout
    }
    long elapsed = micros() - start;
    total += elapsed;
  }

  return total / samples;
}

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW); 
  Serial.println("Starting sensing...");
}

void loop() {
  sensorValue = 0;

  // Measure capacitance
  //pinMode(sensorPin, OUTPUT);
  //digitalWrite(sensorPin, LOW);
  //delayMicroseconds(80);
  //pinMode(sensorPin, INPUT);

  //long start = micros();
  //while(digitalRead(sensorPin) == LOW){
  //  sensorValue = micros() - start;
  //}

  sensorValue = readCapacitiveSensor(30, sensorPin);
  secSensorValue = readCapacitiveSensor(30, secSensorPin);
  Serial.println("Sensor A value: ");
  Serial.print(sensorValue);
  Serial.print("; Sensor B value: ");
  Serial.print(secSensorValue);

  // Adjust threshold for touch
  if(sensorValue < 400){
    Serial.println("Touched!");
    digitalWrite(ledPin, HIGH); 
  } else if (secSensorValue < 400) {
    Serial.println("Touched!");
    digitalWrite(ledPin, HIGH); 
  }else {
    Serial.println("No touch sensed");
    digitalWrite(ledPin, LOW); 
  }

  delay(100);
}