# IDS simulator(Intrusion Detection System) The basic idea of how IDS systems watch logs
# Idea:
#   - read lines from a log file
#   - detect suspicious patterns such as:
#         * repeated failed logins
#         * too many requests from same IP
#         * possible port scans
#   - print alerts when something suspicious happens
#

import time
from pathlib import Path
from collections import defaultdict
#file that IDS will monitor
LOG_FILE = Path("ids_demo.log")
# Thresholds (simple and unrealistic, but good for learning)
MAX_FAILED_LOGINS = 5
MAX_REQUESTS = 20
MAX_PORT_VARIETY = 10

# Trackers
failed_logins = defaultdict(int)
request_count = defaultdict(int)
ports_seen = defaultdict(set)


def process_log_line(line: str) -> None:
    """
    Look at one log line and decide if anything suspicious is happening.
    Expected example formats:
        FAILED_LOGIN 192.168.1.10
        REQUEST 192.168.1.20 PORT 443
        REQUEST 192.168.1.20 PORT 22
    """
    parts = line.strip().split()
    if not parts:
        return

    if parts[0] == "FAILED_LOGIN" and len(parts) >= 2:
        ip = parts[1]
        failed_logins[ip] += 1

        if failed_logins[ip] == MAX_FAILED_LOGINS:
            print(f"[ALERT] Too many failed logins from {ip} (possible brute-force).")

    elif parts[0] == "REQUEST" and len(parts) >= 4 and parts[2] == "PORT":
        ip = parts[1]
        port = parts[3]

        request_count[ip] += 1
        ports_seen[ip].add(port)

        if request_count[ip] >= MAX_REQUESTS:
            print(f"[ALERT] High number of requests from {ip} (possible flood attack).")

        if len(ports_seen[ip]) >= MAX_PORT_VARIETY:
            print(f"[ALERT] Many different ports accessed by {ip} (possible port scan).")


def tail_log_file(path: Path):
    """
    Follow the log file like 'tail -f'. Keep reading as new lines are added.
    """
    print(f"Watching log file: {path.resolve()}")
    print("Press Ctrl+C to stop.\n")

    #if the file doesn't exist yet, create an empty one
    path.touch(exist_ok=True)

    with path.open("r") as f:
        #  move to end of file
        f.seek(0, 2)

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.3)
                continue

            print(f"[LOG] {line.strip()}")
            process_log_line(line)


def main() -> None:
    print("=== TFI05 – Simple IDS Simulator ===\n")

    print("This script watches 'ids_demo.log' and prints alerts when")
    print("it detects suspicious behavior.\n")

    print("Try adding lines manually to the log file, for example:")
    print("  FAILED_LOGIN 192.168.1.10")
    print("  REQUEST 192.168.1.20 PORT 22")
    print("  REQUEST 192.168.1.20 PORT 80\n")

    try:
        tail_log_file(LOG_FILE)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
