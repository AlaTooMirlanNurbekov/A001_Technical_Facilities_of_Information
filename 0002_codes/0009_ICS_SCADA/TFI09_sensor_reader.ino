/* Sensor reader for demo purposes. This is a very small example of how a controller can read a sensor
  and raise a basic alert when something goes out of range.
  Hardware idea:
    - Use a potentiometer or analog temperature sensor on A0
    - Use the built-in LED (pin 13) as a warning indicator
  What it does:
    - reads the sensor value from A0
    - converts it to a fake "temperature" value
    - prints the reading to the Serial Monitor
    - turns the LED on when the value crosses a warning threshold
*/

const int SENSOR_PIN = A0;  // analog input
const int LED_PIN    = 13;   // built-in LED on many Arduino boards

//these values are just for demo, not calibrated
const int RAW_MIN = 0;          // ADC minimum (0)
const int RAW_MAX = 1023;       // ADC maximum (1023)

// we will map ADC range to 0 .. 100 "degrees"
const float TEMP_MIN = 0.0;
const float TEMP_MAX = 100.0;

// if "temperature" goes above this, we turn on LED
const float WARNING_THRESHOLD = 70.0;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(9600);
  while (!Serial) {
    ; // wait for Serial (useful on some boards)
  }

  Serial.println("TFI09 Sensor Reader Demo");
  Serial.println("------------------------");
  Serial.println("Reading from A0 and mapping to 0..100 'degrees'.");
  Serial.println("LED will turn on when value is above warning threshold.\n");
}
void loop() {
  int raw = analogRead(SENSOR_PIN);

  // map the raw ADC value to a fake temperature (0..100)
  float temperature = mapToRange(raw, RAW_MIN, RAW_MAX, TEMP_MIN, TEMP_MAX);

  // Decide if we need to raise a simple warning
  bool warning = (temperature >= WARNING_THRESHOLD);

  if (warning) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }

  // Print a simple log line to the Serial Monitor
  Serial.print("Raw: ");
  Serial.print(raw);
  Serial.print("  |  Temp: ");
  Serial.print(temperature, 1);
  Serial.print(" C  |  Status: ");
  Serial.println(warning ? "WARNING" : "OK");
  delay(1000); // 1 sec between readings
}
float mapToRange(int value, int inMin, int inMax, float outMin, float outMax) {
  //Linear mapping from one range to another
  float ratio = (float)(value - inMin) / (float)(inMax - inMin);
  return outMin + ratio * (outMax - outMin);
}
