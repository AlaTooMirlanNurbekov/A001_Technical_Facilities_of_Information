# static analysis demo
# Idea:
#   - read a Python source file
#   - look for some risky patterns:
#       * hardcoded passwords / secrets
#       * use of eval()
#       * use of exec()
#       * use of os.system()
#   - print warnings with line numbers
# This is not a real security scanner, just a small example of what static analysis tools try to do.

from dataclasses import dataclass
from pathlib import Path
from typing import List
@dataclass
class Finding:
    line_no: int
    line: str
    message: str

PATTERNS = [
    ("password", "Possible hardcoded password."),
    ("secret", "Possible hardcoded secret/token."),
    ("api_key", "Possible hardcoded API key."),
    ("eval(", "Use of eval() can be dangerous."),
    ("exec(", "Use of exec() can be dangerous."),
    ("os.system(", "os.system() can be risky if input is not sanitized."),
]
def analyze_file(path: Path) -> List[Finding]:
    findings: List[Finding] = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except UnicodeDecodeError:
        raise ValueError("File is not UTF-8 text. Try another file.")

    for i, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()

        # Skip empty and comment-only lines
        if not line or line.startswith("#"):
            continue
        lower = line.lower()
        for keyword, message in PATTERNS:
            if keyword in lower:
                findings.append(Finding(line_no=i, line=raw_line, message=message))
                break  # avoid multiple messages for the same line

    return findings

def main() -> None:
    print("=== TFI08 – Static Analysis Demo ===\n")
    print("This script scans a Python file for a few simple risky patterns.\n")
    file_input = input("Enter path to a .py file: ").strip()
    if not file_input:
        print("[!] No file provided.")
        return

    target = Path(file_input).expanduser().resolve()

    if not target.exists():
        print(f"[!] File does not exist: {target}")
        return

    if not target.is_file():
        print(f"[!] Not a file: {target}")
        return

    print(f"\nAnalyzing: {target}\n")

    try:
        findings = analyze_file(target)
    except (FileNotFoundError, ValueError) as e:
        print(f"[!] Error: {e}")
        return

    if not findings:
        print("No risky patterns found (based on our simple rules).")
        print("Remember: real static analyzers check much more than this.")
        return

    print("Findings:")
    for f in findings:
        print(f"  Line {f.line_no}: {f.message}")
        print(f"    {f.line.rstrip()}")
        print()

    print("Review these lines and think: is this safe, or should it be improved?")
if __name__ == "__main__":
    main()
