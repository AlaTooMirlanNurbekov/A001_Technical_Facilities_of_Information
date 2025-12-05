# Small DNS resolution simulator (the goal is to see the steps, not to be 100% like real DNS)
# It shows:
#   - stub resolver cache on the client
#   - recursive resolver with its own cache
#   - root servers
#   - TLD servers
#   - authoritative servers

from dataclasses import dataclass
from typing import Dict, Optional

# Fake "internet" records

#Authoritative DNS data: final answer lives here
AUTH_RECORDS: Dict[str, str] = {
    "alatoo.edu.kg": "212.42.101.253",
    "example.com": "93.184.216.34",
    "mirlan.shop": "203.0.113.77",
}

# Map TLD to a fake TLD server name
TLD_SERVERS: Dict[str, str] = {
    "kg": "KG-TLD-SERVER",
    "com": "COM-TLD-SERVER",
    "shop": "SHOP-TLD-SERVER",
}
# root server that points to TLD servers
ROOT_SERVER = "ROOT-SERVER-A"

@dataclass
class DNSCache:
    records: Dict[str, str]

    def lookup(self, name: str) -> Optional[str]:
        return self.records.get(name)

    def store(self, name: str, ip: str) -> None:
        self.records[name] = ip


# Stub resolver cache on "client"
stub_cache = DNSCache(records={})

#recursive resolver cache at ISP / DNS provider
recursive_cache = DNSCache(records={})

# DNS resolution functions
def stub_resolve(name: str) -> Optional[str]:
    """Client-side stub resolver."""
    print("\n[Stage 0000] Stub resolver on client checks local cache...")
    cached = stub_cache.lookup(name)
    if cached:
        print(f"  -> Found in stub cache: {name} -> {cached}")
        return cached

    print("  -> Not in stub cache, asking recursive resolver...\n")
    ip = recursive_resolve(name)

    if ip:
        print("[Stage 0000] Stub resolver stores result in client cache.")
        stub_cache.store(name, ip)

    return ip


def recursive_resolve(name: str) -> Optional[str]:
    """Recursive resolver that talks to root, TLD and authoritative servers."""
    print("[Stage 0001] Recursive resolver received query.")
    cached = recursive_cache.lookup(name)
    if cached:
        print(f"  -> Found in recursive cache: {name} -> {cached}")
        return cached

    print("[Stage 0002] Not in recursive cache, contacting root server...")
    tld = get_tld(name)
    if not tld:
        print("  -> Could not parse TLD. Resolution failed.")
        return None

    print(f"  -> Asking root server ({ROOT_SERVER}) where to find '.{tld}' TLD server...")
    tld_server = TLD_SERVERS.get(tld)
    if not tld_server:
        print(f"  -> Root server: no TLD server known for '.{tld}'.")
        return None

    print(f"[Stage 0003] Contacting TLD server for '.{tld}': {tld_server}")
    print(f"  -> Asking: 'Where is the authoritative server for {name}?'")

    #in this toy model we skip returning NS; we just go straight to authoritative
    print("[Stage 0004] Contacting authoritative server...")
    ip = AUTH_RECORDS.get(name)

    if not ip:
        print("  -> Authoritative server: domain not found (NXDOMAIN).")
        return None

    print(f"  -> Authoritative answer: {name} -> {ip}")

    print("[Stage 0005] Recursive resolver stores result in its cache.")
    recursive_cache.store(name, ip)

    return ip

def get_tld(name: str) -> Optional[str]:
    """Return the top-level domain (last label)."""
    parts = name.split(".")
    if len(parts) < 2:
        return None
    return parts[-1].lower()


# CLI / main loop
def main() -> None:
    print("=== TFI03 – DNS Resolution Simulator ===")
    print("Type a domain and watch how it is resolved.\n")
    print("Known demo domains:")
    for d in AUTH_RECORDS:
        print(f"  - {d}")
    print()

    while True:
        domain = input("\nEnter domain name (or 'exit' to quit): ").strip()
        if domain.lower() == "exit":
            print("Goodbye.")
            break

        if not domain:
            continue
        print("\n========================================")
        print(f"Resolving: {domain}")
        ip = stub_resolve(domain)

        if ip:
            print(f"\n[Result] {domain} -> {ip}")
        else:
            print(f"\n[Result] Could not resolve '{domain}'.")
        again = input("\nResolve another? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye.")
            break

if __name__ == "__main__":
    main()
