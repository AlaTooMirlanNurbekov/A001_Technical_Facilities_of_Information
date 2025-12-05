# a MAC filter simulator ( to illustrate the concept of MAC filtering on a wifi router)
#
# Idea:
#   - keep a small list of allowed device MAC addresses
#   - simulate a device trying to connect
#   - show ALLOW / DENY decision
#   - let you add/remove MACs and list them
#
from dataclasses import dataclass, field
from typing import Set


def normalize_mac(mac: str) -> str:
    """
    Normalize MAC to a standard format: upper-case, colon-separated.

    Examples:
        "aa-bb-cc-dd-ee-ff" -> "AA:BB:CC:DD:EE:FF"
        "aabb.ccdd.eeff"    -> "AA:BB:CC:DD:EE:FF"
        "AA:bb:CC:dd:EE:ff" -> "AA:BB:CC:DD:EE:FF"
    """
    # keep only hex characters
    hex_only = "".join(ch for ch in mac if ch.isalnum()).upper()
    if len(hex_only) != 12:
        raise ValueError("MAC address must have 12 hex characters after cleanup.")

    #group into pairs
    pairs = [hex_only[i : i + 2] for i in range(0, 12, 2)]
    return ":".join(pairs)


@dataclass
class MacFilter:
    allowed: Set[str] = field(default_factory=set)

    def add(self, mac: str) -> None:
        norm = normalize_mac(mac)
        self.allowed.add(norm)
        print(f"[INFO] Added to allow list: {norm}")

    def remove(self, mac: str) -> None:
        norm = normalize_mac(mac)
        if norm in self.allowed:
            self.allowed.remove(norm)
            print(f"[INFO] Removed from allow list: {norm}")
        else:
            print(f"[INFO] {norm} was not in the allow list.")

    def is_allowed(self, mac: str) -> bool:
        norm = normalize_mac(mac)
        return norm in self.allowed

    def list_allowed(self) -> None:
        if not self.allowed:
            print("[INFO] Allow list is empty.")
            return
        print("Current allow list:")
        for m in sorted(self.allowed):
            print(f"  - {m}")


def make_default_filter() -> MacFilter:
    """
    Build a filter with a few demo MAC addresses.
    """
    mf = MacFilter()
    demo_macs = [
        "AA:BB:CC:DD:EE:01", # laptop
        "AA:BB:CC:DD:EE:02",  # phone
        "AA:BB:CC:DD:EE:03",  # printer
    ]
    for m in demo_macs:
        mf.add(m)
    return mf

def menu() -> None:
    print("\nMenu:")
    print("  1) Show allow list")
    print("  2) Test device connection")
    print("  3) Add MAC to allow list")
    print("  4) Remove MAC from allow list")
    print("  5) Exit")

def main() -> None:
    print("=== TFI04 – MAC Filter Demo ===\n")
    print("This simulates a router that only allows devices whose MAC")
    print("addresses are in the allow list.\n")

    mac_filter = make_default_filter()
    while True:
        menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            mac_filter.list_allowed()
        elif choice == "2":
            mac = input("Enter device MAC address to test: ").strip()
            if not mac:
                print("[!] MAC cannot be empty.")
                continue
            try:
                if mac_filter.is_allowed(mac):
                    print("[ALLOW] Device is allowed to connect.")
                else:
                    print("[DENY]  Device is NOT allowed to connect.")
            except ValueError as e:
                print(f"[!] {e}")

        elif choice == "3":
            mac = input("Enter MAC address to add: ").strip()
            if not mac:
                print("[!] MAC cannot be empty.")
                continue
            try:
                mac_filter.add(mac)
            except ValueError as e:
                print(f"[!] {e}")

        elif choice == "4":
            mac = input("Enter MAC address to remove: ").strip()
            if not mac:
                print("[!] MAC cannot be empty.")
                continue
            try:
                mac_filter.remove(mac)
            except ValueError as e:
                print(f"[!] {e}")

        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("[!] Invalid choice. Please pick 1–5.")

if __name__ == "__main__":
    main()
