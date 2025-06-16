import os
import argparse

def rename_files(folder: str, prefix: str):
    if not os.path.isdir(folder):
        print(f"Error: '{folder}' is not a valid directory.")
        return

    for filename in os.listdir(folder):
        old_path = os.path.join(folder, filename)

        if os.path.isfile(old_path):
            new_filename = prefix + filename
            new_path = os.path.join(folder, new_filename)

            # Skip if the filename already starts with the prefix
            if filename.startswith(prefix):
                print(f"Skipping '{filename}' (already has prefix)")
                continue

            # Rename the file
            os.rename(old_path, new_path)
            print(f"Renamed '{filename}' to '{new_filename}'")

def main():
    parser = argparse.ArgumentParser(description="Rename files by adding a prefix.")
    parser.add_argument("--folder", required=True, help="Path to the folder with files to rename.")
    parser.add_argument("--prefix", required=True, help="Prefix to add to each filename.")

    args = parser.parse_args()
    rename_files(args.folder, args.prefix)

if __name__ == "__main__":
    main()
