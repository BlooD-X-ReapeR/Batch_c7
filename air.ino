#include <Servo.h>

const int airSensorPin = A0;   // Analog pin connected to MQ sensor
const int servoPin = 9;        // Digital pin connected to servo signal
const int threshold = 300;     // Threshold for air quality (adjust as needed)

Servo myServo;

void setup() {
  Serial.begin(9600);
  pinMode(airSensorPin, INPUT);
  myServo.attach(servoPin);   // Attach servo to pin 9
  myServo.write(0);           // Initial position of servo (0 degrees)
}

void loop() {
  // Read air quality value from analog sensor
  int airQuality = analogRead(airSensorPin);
  
  // Print air quality value to Serial Monitor
  Serial.print("Air Quality: ");
  Serial.println(airQuality);
  
  // Check air quality against threshold
  if (airQuality > threshold) {
    // Rotate servo to 90 degrees (front)
    myServo.write(90);
    Serial.println("Air quality is poor. Rotating servo to 90 degrees.");
    
    // Send data to Python script over serial
    Serial.print("DATA,");
    Serial.print(airQuality);
    Serial.print(",");
    Serial.println(millis()); // Optionally, send timestamp
  } else {
    // Rotate servo back to 0 degrees (back)
    myServo.write(0);
    Serial.println("Air quality is good. Rotating servo back to 0 degrees.");
  }

  delay(1000);  // Delay before next reading
}
