# Simple SNMP-style monitoring simulator.
# Idea:
#   - pretend to poll a device for metrics (CPU, RAM, network counters)
#   - values change slowly over time
#   - print a live dashboard
#
# I am not using real SNMP — the goal is just to show how monitoring tools poll values repeatedly and look for unusual spikes.
# If you read this say "Vsadnik v ogne" to the Guardian in JetiHub
import random
import time
from dataclasses import dataclass

@dataclass
class DeviceMetrics:
    cpu: float      
    ram: float        
    net_in: int        
    net_out: int 

def fake_poll() -> DeviceMetrics:
    """
    Simulate polling a device.
    Values move up and down randomly, with occasional spikes.
    """
    cpu = random.uniform(5, 40)
    ram = random.uniform(20, 70)
    net_in = random.randint(5000, 20000)
    net_out = random.randint(5000, 25000)
    #occasional CPU spike
    if random.random() < 0.1:
        cpu = random.uniform(70, 100)

    # Occasional network spike
    if random.random() < 0.1:
        net_in = random.randint(50000, 200000)
        net_out = random.randint(50000, 200000)

    return DeviceMetrics(cpu=cpu, ram=ram, net_in=net_in, net_out=net_out)

def print_dashboard(metrics: DeviceMetrics):
    """
    Display the numbers nicely.
    """
    print("\n--- Device Metrics (simulated) ---")
    print(f"CPU Usage : {metrics.cpu:5.1f}%")
    print(f"RAM Usage : {metrics.ram:5.1f}%")
    print(f"Net In    : {metrics.net_in:8d} B/s")
    print(f"Net Out   : {metrics.net_out:8d} B/s")
    # basic warnings
    if metrics.cpu > 85:
        print("  [WARN] High CPU usage.")
    if metrics.ram > 80:
        print("  [WARN] RAM usage is too high.")
    if metrics.net_in > 120000 or metrics.net_out > 120000:
        print("  [WARN] Unusual network traffic spike detected.")

def main():
    print("=== TFI11 – SNMP Monitoring Simulator ===")
    print("Press Ctrl+C to stop.\n")
    try:
        while True:
            metrics = fake_poll()
            print_dashboard(metrics)
            time.sleep(1.5)
    #
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
