import json
import argparse
from pathlib import Path

def fix_json(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Remove embedded image data
    data['imageData'] = None

    # Set imagePath to match .json filename but with .tif extension
    tif_name = json_path.with_suffix('.tif').name
    data['imagePath'] = tif_name

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_dir', type=Path, required=True, help='Directory with LabelMe .json files')
    args = parser.parse_args()

    for json_file in args.json_dir.glob('*.json'):
        fix_json(json_file)

if __name__ == "__main__":
    main()
