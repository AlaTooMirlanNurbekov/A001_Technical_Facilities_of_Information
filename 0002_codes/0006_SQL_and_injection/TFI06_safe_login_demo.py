# Simple safe-login demo using SQLite.
# Use this together with TFI06_setup.sql to create the database
# Shows:
#   - unsafe login (string concatenation)
#   - safe login (parameterized query)
#

import sqlite3
from pathlib import Path

DB_PATH = Path("tfi06_demo.db")

def unsafe_login(conn, username: str, password: str) -> bool:
    """
    UNSAFE: builds the query as a string.
    Vulnerable to SQL injection.
    """
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print("\n[UNSAFE QUERY]")
    print(query)

    rows = conn.execute(query).fetchall()
    return len(rows) > 0

def safe_login(conn, username: str, password: str) -> bool:
    """
    SAFE: uses parameters instead of string concatenation.
    Prevents SQL injection.
    """
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    print("\n[SAFE QUERY]")
    print(query)
    rows = conn.execute(query, (username, password)).fetchall()
    return len(rows) > 0
def main():
    print("=== TFI06 – Safe Login Demo (SQL Injection Prevention) ===\n")

    if not DB_PATH.exists():
        print("[!] Database file not found. Run TFI06_setup.sql first to create tfi06_demo.db.")
        return

    conn = sqlite3.connect(DB_PATH)
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    print("\n--- Testing UNSAFE login ---")
    try:
        if unsafe_login(conn, username, password):
            print("[UNSAFE] Logged in (this should not always be trusted).")
        else:
            print("[UNSAFE] Login failed.")
    except Exception as e:
        print("[UNSAFE] Error:", e)

    print("\n--- Testing SAFE login ---")
    try:
        if safe_login(conn, username, password):
            print("[SAFE] Logged in successfully.")
        else:
            print("[SAFE] Login failed.")
    except Exception as e:
        print("[SAFE] Error:", e)

    conn.close()

if __name__ == "__main__":
    main()
