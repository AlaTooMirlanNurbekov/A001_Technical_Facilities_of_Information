# AES-256 decryption demo
#
# This script:
#   - asks for the Base64 ciphertext string (output of TFI00_encrypt.py)
#   - asks for the same password
#   - extracts salt, nonce, and ciphertext+tag
#   - tries to decrypt with AES-256-GCM
#
# If the password is wrong or data is corrupted, decryption will fail.


import base64
from getpass import getpass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
# These must match TFI00_encrypt.py
SALT_SIZE = 16          # 16 bytes = 128 bits
NONCE_SIZE = 12         # 12 bytes is standard for GCM
KEY_SIZE = 32           # 32 bytes = 256 bits
PBKDF2_ITERATIONS = 100_000

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Turn a user password into a 256-bit key using PBKDF2 (HMAC-SHA256).
    Same as in TFI00_encrypt.py.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))

def decrypt_with_password(ciphertext_b64: str, password: str) -> str:
    """
    Decrypt the Base64 string produced by TFI00_encrypt.py.

    Input format after Base64 decoding:
        salt (16 bytes) || nonce (12 bytes) || ciphertext+tag (rest)
    """
    if not ciphertext_b64:
        raise ValueError("Ciphertext is empty.")
    if not password:
        raise ValueError("Password is empty.")
    try:
        data = base64.b64decode(ciphertext_b64)
    except Exception:
        raise ValueError("Ciphertext is not valid Base64 data.")

    if len(data) <= SALT_SIZE + NONCE_SIZE:
        raise ValueError("Ciphertext is too short or corrupted.")

    #split the blob into salt, nonce, ciphertext+tag
    salt = data[:SALT_SIZE]
    nonce = data[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext = data[SALT_SIZE + NONCE_SIZE:]

    key = derive_key(password, salt)

    aesgcm = AESGCM(key)
    try:
        plaintext_bytes = aesgcm.decrypt(
            nonce=nonce,
            data=ciphertext,
            associated_data=None,
        )
    except InvalidTag:
        # this usually means wrong password or modified data
        raise ValueError("Decryption failed. Wrong password or corrupted data.")

    return plaintext_bytes.decode("utf-8", errors="replace")


def main() -> None:
    print("=== TFI00 – AES-256 Decryption Demo ===")
    print("Paste the Base64 string produced by TFI00_encrypt.py.\n")
    ciphertext_b64 = input("Ciphertext (Base64): ").strip()
    password = getpass("Enter decryption password: ")
    try:
        plaintext = decrypt_with_password(ciphertext_b64, password)
    except ValueError as e:
        print(f"\n[!] Error: {e}")
        return
    print("\n--- Decrypted message ---")
    print(plaintext)
    
if __name__ == "__main__":
    main()
