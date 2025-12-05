# Backup simulator
#
# What it does:
#   - asks for a source folder (where your files are)
#   - creates a backup folder with a timestamp
#   - copies all files (recursively) from source -> backup
#   - prints a small summary at the end

import os
import shutil
from datetime import datetime
from pathlib import Path

# default folders (you can change these if you want)
DEFAULT_SOURCE = Path("data") # where original files live
DEFAULT_BACKUP_ROOT = Path("backup")  #where backups are stored

def create_backup_folder(root: Path) -> Path:
    """
    Create a new backup folder with current timestamp.
    Example: backup/2025-12-04_141530
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_dir = root / timestamp
    backup_dir.mkdir(parents=True, exist_ok=False)
    return backup_dir
#
def copy_tree(src: Path, dst: Path) -> tuple[int, int]:
    """
    Copy all files from src to dst, keeping subfolders.
    Returns (files_copied, folders_created).
    """
    files_copied = 0
    folders_created = 0

    for root, dirs, files in os.walk(src):
        root_path = Path(root)
        relative_root = root_path.relative_to(src)
        target_root = dst / relative_root

        # create target folder if needed
        if not target_root.exists():
            target_root.mkdir(parents=True, exist_ok=True)
            folders_created += 1
        #Copy files in this folder
        for name in files:
            src_file = root_path / name
            dst_file = target_root / name
            shutil.copy2(src_file, dst_file)
            files_copied += 1

    return files_copied, folders_created

def main() -> None:
    print("=== TFI01 – Backup Simulator ===\n")
    print(f"Default source folder : {DEFAULT_SOURCE.resolve()}")
    print(f"Default backup root   : {DEFAULT_BACKUP_ROOT.resolve()}\n")

    src_input = input("Enter source folder path (leave empty for default): ").strip()
    if src_input:
        source = Path(src_input).expanduser().resolve()
    else:
        source = DEFAULT_SOURCE.resolve()

    if not source.exists() or not source.is_dir():
        print(f"\n[!] Source folder does not exist or is not a directory:\n    {source}")
        return

    # make sure backup root exists
    DEFAULT_BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

    try:
        backup_dir = create_backup_folder(DEFAULT_BACKUP_ROOT)
    except FileExistsError:
        # very unlikely with timestamp, but just in case
        print("\n[!] Could not create backup folder (already exists). Try again.")
        return

    print(f"\nBacking up from:\n  {source}")
    print(f"To:\n  {backup_dir}\n")

    files_copied, folders_created = copy_tree(source, backup_dir)
    print("--- Backup complete ---")
    print(f"Folders created: {folders_created}")
    print(f"Files copied   : {files_copied}")
    print("\nYou can open the backup folder and check that the structure is preserved.")

if __name__ == "__main__":
    main()
