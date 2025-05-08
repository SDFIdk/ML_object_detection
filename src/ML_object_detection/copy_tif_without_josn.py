import argparse
from pathlib import Path
import shutil

def copy_tif_without_json(src_dir: Path, dst_dir: Path):
    dst_dir.mkdir(parents=True, exist_ok=True)

    for tif_file in src_dir.glob("*.tif"):
        json_file = tif_file.with_suffix(".json")
        if not json_file.exists():
            shutil.copy2(tif_file, dst_dir)
            print(f"Copied: {tif_file.name}")
        else:
            print(f"Skipped (has .json): {tif_file.name}")

def main():
    parser = argparse.ArgumentParser(description="Copy .tif files without matching .json to another directory.")
    parser.add_argument("--src", required=True, type=Path, help="Source directory path")
    parser.add_argument("--dst", required=True, type=Path, help="Destination directory path")
    args = parser.parse_args()

    copy_tif_without_json(args.src, args.dst)

if __name__ == "__main__":
    main()
