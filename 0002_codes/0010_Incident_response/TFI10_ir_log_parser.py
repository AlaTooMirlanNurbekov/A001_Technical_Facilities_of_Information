# Simplified incident response (IR) log parser. # You can create a small test log manually with my code idea
#
# Idea:
#   - read a text log file with timestamps and levels
#   - count how many INFO / WARNING / ALERT / CRITICAL messages
#   - let you filter by keyword or IP address
#
# Expected log format (one line per event, for example):
#   2025-12-05 12:30:01 [INFO] User login from 10.0.0.5
#   2025-12-05 12:31:10 [WARNING] Failed login for admin from 203.0.113.10
#   2025-12-05 12:32:55 [ALERT] Multiple failed logins from 203.0.113.10
#   2025-12-05 12:35:00 [CRITICAL] Ransomware activity detected on host 10.0.0.20
#

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional

LOG_PATH_DEFAULT = Path("ir_events.log")


@dataclass
class LogEntry:
    timestamp: str
    level: str
    message: str
    raw: str

def parse_log_line(line: str) -> Optional[LogEntry]:
    """
    Try to parse a single log line.
    Very simple parser for lines like:
        YYYY-MM-DD HH:MM:SS [LEVEL] message...
    """
    line = line.strip()
    if not line:
        return None

    parts = line.split(" ", 2)  #date, time, rest
    if len(parts) < 3:
        return None

    date_str, time_str, rest = parts
    timestamp = f"{date_str} {time_str}"

    # rest should start with [LEVEL]
    if not rest.startswith("[") or "]" not in rest:
        return None

    closing = rest.find("]")
    level = rest[1:closing].strip().upper()
    message = rest[closing + 1 :].strip()

    return LogEntry(timestamp=timestamp, level=level, message=message, raw=line)


def load_entries(path: Path) -> List[LogEntry]:
    """Read and parse all log entries from the file."""
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")

    entries: List[LogEntry] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        entry = parse_log_line(raw)
        if entry:
            entries.append(entry)
    return entries


def summarize_levels(entries: List[LogEntry]) -> Dict[str, int]:
    """Count how many entries there are for each level."""
    counts: Dict[str, int] = {}
    for e in entries:
        counts[e.level] = counts.get(e.level, 0) + 1
    return counts
def filter_by_keyword(entries: List[LogEntry], keyword: str) -> List[LogEntry]:
    """Return entries that contain the keyword (case-insensitive)."""
    keyword_lower = keyword.lower()
    return [e for e in entries if keyword_lower in e.message.lower()]

def filter_by_ip(entries: List[LogEntry], ip: str) -> List[LogEntry]:
    """Return entries where the given IP appears in the message."""
    return [e for e in entries if ip in e.message]

def print_entries(entries: List[LogEntry], limit: int = 0) -> None:
    """Print entries, optionally limited to first `limit`."""
    if limit > 0:
        entries = entries[:limit]

    for e in entries:
        print(e.raw)
    if not entries:
        print("(no matching entries)")

def main() -> None:
    print("=== TFI10 – IR Log Parser ===\n")

    print(f"Default log path: {LOG_PATH_DEFAULT.resolve()}")
    path_input = input("Enter log path (leave empty for default): ").strip()
    if path_input:
        log_path = Path(path_input).expanduser().resolve()
    else:
        log_path = LOG_PATH_DEFAULT.resolve()
    try:
        entries = load_entries(log_path)
    except FileNotFoundError as e:
        print(f"[!] {e}")
        return

    if not entries:
        print("[!] No valid log entries found.")
        return

    print(f"\nLoaded {len(entries)} log entries.\n")
    # summary
    counts = summarize_levels(entries)
    print("--- Level summary ---")
    for level in sorted(counts.keys()):
        print(f"  {level:9s}: {counts[level]}")
    print()
    while True:
        print("\nMenu:")
        print("  1) Show last 10 events")
        print("  2) Filter by keyword")
        print("  3) Filter by IP address")
        print("  4) Exit")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            print("\nLast 10 events:")
            print_entries(entries[-10:])

        elif choice == "2":
            keyword = input("Keyword to search (e.g. 'ransomware', 'failed login'): ").strip()
            if not keyword:
                print("[!] Keyword cannot be empty.")
                continue
            matches = filter_by_keyword(entries, keyword)
            print(f"\nFound {len(matches)} matching entries:\n")
            print_entries(matches)
        elif choice == "3":
            ip = input("IP address to search (e.g. '203.0.113.10'): ").strip()
            if not ip:
                print("[!] IP address cannot be empty.")
                continue
            matches = filter_by_ip(entries, ip)
            print(f"\nFound {len(matches)} matching entries:\n")
            print_entries(matches)

        elif choice == "4":
            print("Goodbye.")
            break

        else:
            print("[!] Invalid choice. Please pick 1–4.")

if __name__ == "__main__":
    main()
