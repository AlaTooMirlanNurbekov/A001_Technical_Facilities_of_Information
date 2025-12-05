# User authentication demo
# What this script shows:
#   - how to store passwords using a hash (not plain text)
#   - why we use salt
#   - how to verify a password during login
#
# It keeps users in a small JSON file: tfi02_users.json

import json
import os
import base64
import hmac
from getpass import getpass
from pathlib import Path
from typing import Dict, Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

USERS_FILE = Path("tfi02_users.json")

SALT_SIZE = 16          # 16 bytes salt
KEY_SIZE = 32            # 32 bytes = 256 bits
PBKDF2_ITERATIONS = 100_000


#helper functions 
def load_users() -> Dict[str, Any]:
    """Load user data from JSON file (if it exists)."""
    if not USERS_FILE.exists():
        return {}
    try:
        with USERS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # broken file -> start fresh, but mention it
        print("[!] Warning: users file is corrupted, starting with empty DB.")
        return {}

def save_users(users: Dict[str, Any]) -> None:
    """Save user data to JSON file."""
    with USERS_FILE.open("w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def hash_password(password: str, salt: bytes) -> str:
    """Return a hex string of PBKDF2-HMAC-SHA256(password, salt)."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    key = kdf.derive(password.encode("utf-8"))
    return key.hex()
def register_user(users: Dict[str, Any]) -> None:
    """Create a new user with salted password hash."""
    username = input("Choose a username: ").strip()
    if not username:
        print("[!] Username cannot be empty.")
        return

    if username in users:
        print("[!] This username already exists.")
        return
    pwd1 = getpass("Choose a password: ")
    pwd2 = getpass("Confirm password: ")

    if pwd1 != pwd2:
        print("[!] Passwords do not match.")
        return

    if not pwd1:
        print("[!] Password cannot be empty.")
        return

    salt = os.urandom(SALT_SIZE)
    pwd_hash = hash_password(pwd1, salt)

    users[username] = {
        "salt": base64.b64encode(salt).decode("ascii"),
        "hash": pwd_hash,
        "iterations": PBKDF2_ITERATIONS,
    }
    save_users(users)
    print(f"[+] User '{username}' registered successfully.")

def login_user(users: Dict[str, Any]) -> None:
    """Verify a username and password."""
    username = input("Username: ").strip()
    if username not in users:
        print("[!] Unknown user.")
        return

    record = users[username]
    try:
        salt = base64.b64decode(record["salt"])
        stored_hash = record["hash"]
        iterations = int(record.get("iterations", PBKDF2_ITERATIONS))
    except (KeyError, ValueError, base64.binascii.Error):
        print("[!] User record is invalid or corrupted.")
        return

    password = getpass("Password: ")

    #use the same settings that were used for this user
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=iterations,
    )
    key = kdf.derive(password.encode("utf-8"))
    candidate_hash = key.hex()

    if hmac.compare_digest(candidate_hash, stored_hash):
        print(f"[+] Login successful. Welcome, {username}!")
    else:
        print("[!] Login failed. Wrong password.")

#main menu
def main() -> None:
    print("=== TFI02 – User Authentication Demo ===")
    print("This shows salted password hashing with PBKDF2.\n")

    users = load_users()

    while True:
        print("\nMenu:")
        print("  1) Register new user")
        print("  2) Login")
        print("  3) Exit")
        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            register_user(users)
        elif choice == "2":
            login_user(users)
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("[!] Invalid choice. Please pick 1, 2 or 3.")


if __name__ == "__main__":
    main()
