# AES-256 encryption demo 
# To run this file you need the "cryptography" package (pip install cryptography)
# This script:
#   - asks the user for a message
#   - asks for a password (hidden)
#   - turns the password into a 256-bit key
#   - encrypts the message with AES-GCM
#   - prints one Base64 string that contains everything we need to decrypt later
#

import os
import base64
from getpass import getpass
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

#basic settings for the demo
SALT_SIZE = 16          # 16 bytes = 128 bits
NONCE_SIZE = 12         # 12 bytes is standard for GCM
KEY_SIZE = 32           # 32 bytes = 256 bits
PBKDF2_ITERATIONS = 100_000

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Turn a user password into a 256-bit key using PBKDF2 (HMAC-SHA256).
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))

def encrypt_with_password(plaintext: str, password: str) -> str:
    """
    Encrypt the given plaintext with AES-256-GCM using a key derived from the password.
    We return a Base64 string that contains:
        salt || nonce || ciphertext_and_tag
    """
    if not plaintext:
        raise ValueError("Plaintext is empty.")
    if not password:
        raise ValueError("Password is empty.")
    #fresh random salt for this encryption
    salt = os.urandom(SALT_SIZE)
    # derive key from password + salt
    key = derive_key(password, salt)
    # random nonce for GCM (must be unique for each encryption with the same key)
    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(
        nonce=nonce,
        data=plaintext.encode("utf-8"),
        associated_data=None,   # we don't use AAD in this simple demo
    )

    # build one binary blob so decryption script can split it later
    data = salt + nonce + ciphertext

    #Base64 makes it easy to copy-paste into slides or text files
    return base64.b64encode(data).decode("ascii")

def main() -> None:
    print("=== TFI00 – AES-256 Encryption Demo ===")
    print("This will encrypt your message with AES-GCM using a password.\n")
    message = input("Enter the message to encrypt: ").strip()
    password = getpass("Enter encryption password: ")
    password_confirm = getpass("Confirm password: ")
    if password != password_confirm:
        print("\n[!] Passwords do not match. Try again.")
        return
    try:
        result_b64 = encrypt_with_password(message, password)
    except ValueError as e:
        print(f"\n[!] Error: {e}")
        return

    print("\n--- Result ---")
    print("Ciphertext (Base64):")
    print(result_b64)
    #this extra print is just to explain in class what is inside.
    print("\nNote for explanation:")
    print(f"- Salt size:   {SALT_SIZE} bytes")
    print(f"- Nonce size:  {NONCE_SIZE} bytes")
    print(f"- Key size:    {KEY_SIZE} bytes (256 bits)")
    print("\nYou can save this string and later decrypt it in TFI00_decrypt.py.")

if __name__ == "__main__":
    main()
