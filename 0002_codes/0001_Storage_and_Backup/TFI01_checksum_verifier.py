# Checksum verifier for "Technical Facilities of Information".
# What it does:
#   - asks for an "original" folder (where your real files are)
#   - asks for a "backup" folder (one of the backup copies)
#   - walks through all files in the original folder
#   - calculates SHA-256 hash for each file in original and backup
#   - reports which files match, which are missing, and which are different
#
# Idea: after running TFI01_backup_simulator.py you can run this script to see that your backup really contains the same data

import hashlib
import os
from pathlib import Path
from typing import Tuple

DEFAULT_ORIGINAL = Path("data")   #same default as backup simulator
DEFAULT_BACKUP_ROOT = Path("backup")  # where backup folders live


def hash_file(path: Path, chunk_size: int = 65536) -> str:
    """
    Calculate SHA-256 hash for a file.
    We read the file in chunks so it works for big files too.
    """
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def choose_backup_folder() -> Path:
    """
    Helper: pick a backup folder.
    If there are timestamped subfolders in backup/, choose the newest one.
    If not, just return backup/.
    """
    backup_root = DEFAULT_BACKUP_ROOT.resolve()
    if not backup_root.exists():
        return backup_root  # will be handled by caller

    subdirs = [d for d in backup_root.iterdir() if d.is_dir()]
    if not subdirs:
        return backup_root

    #sort by modification time, newest last
    subdirs.sort(key=lambda p: p.stat().st_mtime)
    return subdirs[-1]

def verify_backup(original: Path, backup: Path) -> Tuple[int, int, int, int]:
    """
    Compare files in 'original' vs 'backup' using SHA-256 hashes.
    Returns a tuple:
        (total_files, matched, mismatched, missing)
    """
    total_files = 0
    matched = 0
    mismatched = 0
    missing = 0
    for root, dirs, files in os.walk(original):
        root_path = Path(root)
        for name in files:
            total_files += 1

            src_file = root_path / name
            rel_path = src_file.relative_to(original)
            dst_file = backup / rel_path
            #
            if not dst_file.exists():
                print(f"[MISSING] {rel_path}")
                missing += 1
                continue

            src_hash = hash_file(src_file)
            dst_hash = hash_file(dst_file)

            if src_hash == dst_hash:
                print(f"[OK]       {rel_path}")
                matched += 1
            else:
                print(f"[MISMATCH] {rel_path}")
                mismatched += 1

    return total_files, matched, mismatched, missing


def main() -> None:
    print("=== TFI01 – Checksum Verifier ===\n")
    print("This checks if your backup files are identical to the originals.")
    print("It uses SHA-256 hashes for comparison.\n")

    print(f"Default original folder : {DEFAULT_ORIGINAL.resolve()}")
    orig_input = input("Enter original folder (leave empty for default): ").strip()
    if orig_input:
        original = Path(orig_input).expanduser().resolve()
    else:
        original = DEFAULT_ORIGINAL.resolve()

    if not original.exists() or not original.is_dir():
        print(f"\n[!] Original folder does not exist or is not a directory:\n    {original}")
        return

    # Try to guess a backup folder (latest timestamped dir) but let user override
    guessed_backup = choose_backup_folder()
    print(f"\nGuessed backup folder : {guessed_backup}")
    backup_input = input("Enter backup folder (leave empty to use this): ").strip()
    if backup_input:
        backup = Path(backup_input).expanduser().resolve()
    else:
        backup = guessed_backup

    if not backup.exists() or not backup.is_dir():
        print(f"\n[!] Backup folder does not exist or is not a directory:\n    {backup}")
        return

    print(f"\nComparing:\n  Original: {original}\n  Backup:   {backup}\n")

    total, ok, bad, missing = verify_backup(original, backup)

    print("\n--- Summary ---")
    print(f"Total files checked : {total}")
    print(f"Matched             : {ok}")
    print(f"Mismatched          : {bad}")
    print(f"Missing in backup   : {missing}")

    if bad == 0 and missing == 0:
        print("\nResult: Backup looks consistent with the original.")
    else:
        print("\nResult: There are issues. Check mismatched/missing entries above.")

if __name__ == "__main__":
    main()
