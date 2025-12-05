# wi-fi password strength checker
# Idea:
#   - ask for wi-fi name (SSID) and password
#   - check length and character variety
#   - warn about common / easy patterns
#   - give a simple score and suggestions
# This is just a helper tool, NOT A HACKER TOOL!!!!!!! PLS remember about responsibility for your actions!
import re
from dataclasses import dataclass

COMMON_PASSWORDS = {
    "password",
    "12345678",
    "123456789",
    "1234567890",
    "qwerty",
    "letmein",
    "admin123",
    "alatoo123",
    "wifi1234",
    "123456789a",
}

MIN_LENGTH = 8
GOOD_LENGTH = 12
STRONG_LENGTH = 16

@dataclass
class PasswordReport:
    score: int
    rating: str
    reasons: list[str]
    tips: list[str]

def analyze_password(ssid: str, pwd: str) -> PasswordReport:
    reasons: list[str] = []
    tips: list[str] = []
    score = 0
    if not pwd:
        return PasswordReport(
            score=0,
            rating="invalid",
            reasons=["Password is empty."],
            tips=["Use at least 12 characters with a mix of letters, numbers, and symbols."],
        )
    lower_pwd = pwd.lower()

    # 1) length check
    length = len(pwd)
    if length < MIN_LENGTH:
        reasons.append(f"Too short (only {length} characters).")
        tips.append(f"Use at least {MIN_LENGTH} characters, ideally {GOOD_LENGTH}+.")
    elif length < GOOD_LENGTH:
        reasons.append(f"Length is okay but could be stronger ({length} characters).")
        score += 1
        tips.append(f"Aim for {GOOD_LENGTH}+ characters if possible.")
    elif length < STRONG_LENGTH:
        reasons.append(f"Good length ({length} characters).")
        score += 2
    else:
        reasons.append(f"Great length ({length} characters).")
        score += 3

    # 2) character variety
    has_lower = bool(re.search(r"[a-z]", pwd))
    has_upper = bool(re.search(r"[A-Z]", pwd))
    has_digit = bool(re.search(r"\d", pwd))
    has_symbol = bool(re.search(r"[^A-Za-z0-9]", pwd))

    variety_count = sum([has_lower, has_upper, has_digit, has_symbol])

    if variety_count <= 1:
        reasons.append("Uses only one character type (very easy to guess).")
        tips.append("Mix lowercase, UPPERCASE, digits, and symbols.")
    elif variety_count == 2:
        reasons.append("Uses two character types.")
        score += 1
        tips.append("Add digits or symbols to make it harder to guess.")
    elif variety_count == 3:
        reasons.append("Uses three different character types.")
        score += 2
    else:
        reasons.append("Uses lowercase, UPPERCASE, digits and symbols.")
        score += 3

    # 3) common passwords / patterns
    simple_pwd = re.sub(r"[^a-z0-9]", "", lower_pwd)  # strip weird chars for comparison
    if simple_pwd in COMMON_PASSWORDS:
        reasons.append("Looks like a very common password pattern.")
        tips.append("Avoid popular passwords like '12345678', 'password', etc.")
        score -= 2
    if ssid:
        if ssid.lower() in lower_pwd:
            reasons.append("Password contains the Wi-Fi name (SSID).")
            tips.append("Avoid including the network name inside the password.")
            score -= 1

    # 4) obvious sequences
    if re.search(r"(0123|1234|2345|3456|4567|5678|6789)", pwd):
        reasons.append("Contains obvious number sequences (e.g. 1234, 6789).")
        tips.append("Avoid long straight sequences of numbers.")
        score -= 1

    if re.search(r"(aaaa|bbbb|1111|2222|zzzz)", lower_pwd):
        reasons.append("Contains repeated characters (e.g. aaaa, 1111).")
        tips.append("Mix characters instead of repeating the same one many times.")
        score -= 1

    #final rating
    if score <= 0:
        rating = "very weak"
    elif score == 1:
        rating = "weak"
    elif score == 2 or score == 3:
        rating = "okay"
    elif score == 4 or score == 5:
        rating = "strong"
    else:
        rating = "very strong"

    return PasswordReport(score=score, rating=rating, reasons=reasons, tips=tips)

def main() -> None:
    print("=== TFI04 – Wi-Fi Password Strength Checker ===\n")

    ssid = input("Wi-Fi name (SSID)          : ").strip()
    pwd = input("Wi-Fi password to analyse : ").strip()

    report = analyze_password(ssid, pwd)

    print("\n--- Result ---")
    print(f"Rating: {report.rating}  (score: {report.score})\n")

    print("Checks:")
    for r in report.reasons:
        print(f" - {r}")

    if report.tips:
        print("\nSuggestions:")
        # remove duplicates but keep order
        seen = set()
        for tip in report.tips:
            if tip not in seen:
                seen.add(tip)
                print(f" - {tip}")

    print("\nRemember: never reuse your Wi-Fi password on websites or other accounts.")

if __name__ == "__main__":
    main()
