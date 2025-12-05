# Safe control loop simulation
# Idea:
#   - simulate reading a sensor value
#   - validate input (range checks)
#   - update an "actuator" only when safe
#   - generate warnings or alarms when out of range
import random
import time
from dataclasses import dataclass

# configurations for the simulation
MIN_SENSOR_VALUE = 0
MAX_SENSOR_VALUE = 100

WARNING_LEVEL = 70
ALARM_LEVEL = 85

@dataclass
class SensorData:
    value: float
    timestamp: float

@dataclass
class Actuator:
    state: str = "IDLE"   #could be IDLE, COOLING, SHUTDOWN

    def set_state(self, new_state: str):
        print(f"[ACTUATOR] State change: {self.state} -> {new_state}")
        self.state = new_state


def read_sensor() -> SensorData:
    """
    Fake sensor:
        - sometimes produces normal values
        - sometimes spikes high or low
    """
    base = random.uniform(20, 65)
    # introduce occasional spikes for demo
    if random.random() < 0.10:
        base = random.uniform(80, 110)  # too high
    if random.random() < 0.10:
        base = random.uniform(-10, 10)  # too low

    return SensorData(value=base, timestamp=time.time())


def validate_sensor(data: SensorData) -> bool:
    """
    Ensure sensor reading is within a plausible range.
    """
    if data.value < MIN_SENSOR_VALUE or data.value > MAX_SENSOR_VALUE:
        print(f"[INVALID] Sensor reading {data.value:.1f} out of valid range "
              f"({MIN_SENSOR_VALUE}-{MAX_SENSOR_VALUE}). Ignoring value.")
        return False
    return True

def control_logic(sensor_value: float, actuator: Actuator):
    """
    Very small example of a safe-control decision.
    """
    if sensor_value >= ALARM_LEVEL:
        print(f"[ALARM] Value {sensor_value:.1f} is critically high. Entering SHUTDOWN.")
        actuator.set_state("SHUTDOWN")

    elif sensor_value >= WARNING_LEVEL:
        print(f"[WARN] Value {sensor_value:.1f} is high. Cooling system activated.")
        actuator.set_state("COOLING")

    else:
        if actuator.state != "IDLE":
            actuator.set_state("IDLE")
        print(f"[OK] {sensor_value:.1f} within normal range.")

def main():
    print("=== TFI09 – Safe Control Loop Simulation ===\n")
    print("Press Ctrl+C to stop.\n")
    actuator = Actuator()
    try:
        while True:
            data = read_sensor()
            print(f"\n[SENSOR] Value: {data.value:.1f}")

            if validate_sensor(data):
                control_logic(data.value, actuator)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
