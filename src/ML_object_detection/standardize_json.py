import json
import argparse
from pathlib import Path

def fix_json(json_path, remove_ids):
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Remove embedded image data
    data['imageData'] = None

    # Set imagePath to match .json filename but with .tif extension
    tif_name = json_path.with_suffix('.tif').name
    data['imagePath'] = tif_name

    # Filter out shapes with label == remove_id
    original_count = len(data.get('shapes', []))
    data['shapes'] = [shape for shape in data.get('shapes', []) if not (shape.get('label') in remove_ids)]
    removed_count = original_count - len(data['shapes'])

    print(f"{json_path.name}: Removed {removed_count} shape(s) with labels '{remove_ids}'.")

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_dir', type=Path, required=True, help='Directory with LabelMe .json files')
    parser.add_argument('--remove_ids', type=str, default=['Skorsten',"ignore","unknown"], help='Label to remove from shapes')
    args = parser.parse_args()

    for json_file in args.json_dir.glob('*.json'):
        fix_json(json_file, args.remove_ids)

if __name__ == "__main__":
    main()
