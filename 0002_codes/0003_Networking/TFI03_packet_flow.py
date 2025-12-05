# Small packet flow simulator
# It shows, in a simplified way, how a packet travels:
# PC_A -> Switch -> Router -> Internet -> Router_B -> Switch_B -> PC_B
# The goal is to visualise the idea of hops and devices, not to implement real TCP/IP.

from dataclasses import dataclass
from typing import List

@dataclass
class Packet:
    src_ip: str
    dst_ip: str
    payload: str
    ttl: int = 8  #small TTL for demo

    def __str__(self) -> str:
        return f"Packet(src={self.src_ip}, dst={self.dst_ip}, ttl={self.ttl}, data='{self.payload}')"
@dataclass
class Device:
    name: str

    def handle(self, packet: Packet) -> None:
        raise NotImplementedError

@dataclass
class Host(Device):
    ip: str
    def send(self, dst_ip: str, payload: str, path: List["Device"]) -> None:
        packet = Packet(src_ip=self.ip, dst_ip=dst_ip, payload=payload)
        print(f"\n[HOST {self.name}] Sending packet:")
        print(f"  {packet}")
        traverse_path(packet, path)
    def receive(self, packet: Packet) -> None:
        print(f"[HOST {self.name}] Received packet:")
        print(f"  {packet}")
        print(f"  Payload delivered to application: '{packet.payload}'\n")

@dataclass
class Switch(Device):
    def handle(self, packet: Packet) -> None:
        print(f"[SWITCH {self.name}] Forwarding frame at Layer 2 (no IP change).")
        # In reality a switch uses MAC addresses, but we keep it simple.

@dataclass
class Router(Device):
    public_side: bool = False

    def handle(self, packet: Packet) -> None:
        print(f"[ROUTER {self.name}] Routing at Layer 3 (IP-based decision).")
        packet.ttl -= 1
        if packet.ttl <= 0:
            print(f"[ROUTER {self.name}] TTL expired. Packet dropped.")
            raise StopTraversal("TTL expired")

class StopTraversal(Exception):
    """Used to stop the path traversal when packet is dropped or delivered."""
    pass

def traverse_path(packet: Packet, path: List[Device]) -> None:
    """
    Take the packet through a list of devices until it reaches the last one.
    The last item in the path is assumed to be the destination Host.
    """
    try:
        for i, dev in enumerate(path):
            print("\n----------------------------------------")
            print(f"HOP {i + 1}: {dev.name}")
            print(f"Current packet: {packet}")

            if isinstance(dev, Host):
                # Destination host receives the packet
                dev.receive(packet)
                raise StopTraversal("Delivered to host")
            dev.handle(packet)
        print("\n[INFO] Path ended but packet never reached a host.")
    except StopTraversal as e:
        # Just end cleanly
        print(f"\n[FLOW END] {e}")

def make_demo_topology():
    """
    Build a small fixed topology:
        PC_A -> Switch_A -> Router_A -> Internet -> Router_B -> Switch_B -> PC_B
    """
    pc_a = Host(name="PC_A", ip="192.168.1.10")
    pc_b = Host(name="PC_B", ip="10.0.0.20")
    sw_a = Switch(name="SW_A")
    sw_b = Switch(name="SW_B")
    r_a = Router(name="R_A", public_side=True)
    r_b = Router(name="R_B", public_side=True)

    # "Internet" is just a label here, not a real device
    internet_hop = Device(name="INTERNET")  # type: ignore
    def fake_handle(self, packet: Packet) -> None:
        print(f"[INTERNET] Packet is travelling through multiple networks...")
        packet.ttl -= 1
        if packet.ttl <= 0:
            print("[INTERNET] TTL expired in transit. Packet dropped.")
            raise StopTraversal("TTL expired in Internet")

    # monkey-patch a simple handle method for our fake internet device
    setattr(internet_hop, "handle", fake_handle.__get__(internet_hop, Device))  # type: ignore
    return pc_a, pc_b, [sw_a, r_a, internet_hop, r_b, sw_b, pc_b]

def main() -> None:
    print("=== TFI03 – Packet Flow Simulator ===")
    print("This is a simplified view of how a packet moves across devices.\n")
    pc_a, pc_b, path = make_demo_topology()
    print("Topology:")
    print("  PC_A (192.168.1.10)")
    print("     -> Switch_A")
    print("     -> Router_A")
    print("     -> Internet")
    print("     -> Router_B")
    print("     -> Switch_B")
    print("     -> PC_B (10.0.0.20)\n")
    payload = input("Enter payload/message to send from PC_A to PC_B: ").strip()
    if not payload:
        payload = "Hello from PC_A!"
    pc_a.send(dst_ip=pc_b.ip, payload=payload, path=path)
    print("\nSimulation finished.")

if __name__ == "__main__":
    main()
