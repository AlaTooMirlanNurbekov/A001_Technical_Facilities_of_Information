# Simple "cloud backup" simulator
# Idea:
#   - take a local folder (e.g. your project or documents)
#   - create a .zip archive from it
#   - copy that archive into a "cloud" folder
#   - print a small progress bar for the upload
#
# There is no real cloud here – just local folders – but the flow is similar to how many backup tools work

import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

SOURCE_DEFAULT = Path("data")          # folder to back up
BACKUP_LOCAL_ROOT = Path("local_backup")
CLOUD_ROOT = Path("cloud_storage")
def create_zip_from_folder(source: Path, dest_dir: Path) -> Path:
    """Create a timestamped zip archive from the source folder."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    zip_path = dest_dir / f"backup_{timestamp}.zip"
    print(f"\n[STEP] Creating local backup archive:")
    print(f"       Source: {source}")
    print(f"       Zip   : {zip_path}")
    with ZipFile(zip_path, mode="w", compression=ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source):
            root_path = Path(root)
            for name in files:
                file_path = root_path / name
                # Store relative path inside the zip
                rel_path = file_path.relative_to(source)
                zf.write(file_path, arcname=rel_path)

    print("[INFO] Archive created.")
    return zip_path

def simulate_upload(zip_path: Path, cloud_root: Path) -> Path:
    """
    Simulate uploading the zip file to a "cloud" folder.
    In reality this is just a file copy with a fake progress bar.
    """
    cloud_root.mkdir(parents=True, exist_ok=True)
    cloud_dest = cloud_root / zip_path.name

    size_bytes = zip_path.stat().st_size
    size_mb = max(size_bytes / (1024 * 1024), 0.01)

    print(f"\n[STEP] Uploading archive to cloud storage:")
    print(f"       From: {zip_path}")
    print(f"       To  : {cloud_dest}")
    print(f"       Size: {size_mb:.2f} MB (simulated)\n")

    # Fake progress bar
    steps = 20
    for i in range(1, steps + 1):
        time.sleep(0.05)  # slow it down a bit so humans can see it
        done = "█" * i
        todo = "." * (steps - i)
        percent = (i / steps) * 100
        print(f"\rUploading: [{done}{todo}] {percent:5.1f}%", end="")

    # Now actually copy the file
    shutil.copy2(zip_path, cloud_dest)
    print("\n[INFO] Upload complete.")
    return cloud_dest

def main() -> None:
    print("=== TFI07 – Cloud Backup Simulator ===\n")

    print(f"Default source folder    : {SOURCE_DEFAULT.resolve()}")
    print(f"Local backup folder root : {BACKUP_LOCAL_ROOT.resolve()}")
    print(f"Cloud storage folder     : {CLOUD_ROOT.resolve()}\n")
    src_input = input("Enter source folder path (leave empty for default): ").strip()
    if src_input:
        source = Path(src_input).expanduser().resolve()
    else:
        source = SOURCE_DEFAULT.resolve()

    if not source.exists() or not source.is_dir():
        print(f"\n[!] Source folder does not exist or is not a directory:\n    {source}")
        return
    # Step 1: create local zip backup
    zip_path = create_zip_from_folder(source, BACKUP_LOCAL_ROOT)

    # Step 2: simulate upload to cloud
    cloud_dest = simulate_upload(zip_path, CLOUD_ROOT)
    print("\n--- Summary ---")
    print(f"Local archive : {zip_path}")
    print(f"Cloud copy    : {cloud_dest}")
    print("\nYou can open the cloud_storage folder to see the 'uploaded' backup file.")

if __name__ == "__main__":
    main()
