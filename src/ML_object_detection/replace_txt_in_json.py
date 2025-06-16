import argparse
import json
from pathlib import Path

def replace_in_json(file_path, old, new):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        new_data = data.replace(old, new)
        if data != new_data:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_data)
            print(f"Modified: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Replace string in all .json files in a folder.")
    parser.add_argument('--folder', required=True, help="Path to the folder containing JSON files")
    parser.add_argument('--old', required=True, help="Old string to replace")
    parser.add_argument('--new', required=True, help="New string to insert")
    args = parser.parse_args()

    folder_path = Path(args.folder)
    if not folder_path.is_dir():
        print(f"Error: {folder_path} is not a valid directory.")
        return

    json_files = folder_path.rglob("*.json")
    for json_file in json_files:
        replace_in_json(json_file, args.old, args.new)

if __name__ == "__main__":
    main()
