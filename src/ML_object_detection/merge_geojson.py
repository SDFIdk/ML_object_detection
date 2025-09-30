import argparse
import json
import sys

def merge_geojson_files(input_paths, output_path):
    """
    Merges features from multiple GeoJSON FeatureCollection files into a single file.
    """
    all_features = []
    # The CRS (Coordinate Reference System) from the first file will be used for the output
    crs = None
    
    print(f"Starting merge of {len(input_paths)} files...")

    for i, path in enumerate(input_paths):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data.get('type') != 'FeatureCollection':
                print(f"Warning: File '{path}' is not a 'FeatureCollection' and will be skipped.")
                continue

            # Set CRS from the first valid file
            if i == 0:
                crs = data.get('crs')
            
            # Extend the master feature list with features from the current file
            features = data.get('features', [])
            all_features.extend(features)
            print(f"Loaded {len(features)} features from '{path}'.")

        except FileNotFoundError:
            print(f"Error: Input file not found at '{path}'. Skipping.")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in file at '{path}'. Skipping.")
        except Exception as e:
            print(f"An unexpected error occurred while processing '{path}': {e}. Skipping.")

    # Construct the final GeoJSON FeatureCollection
    output_geojson = {
        "type": "FeatureCollection",
        # Include CRS if it was found
        **({'crs': crs} if crs is not None else {}),
        "features": all_features
    }

    try:
        # Write the merged data to the output file with indentation for readability
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_geojson, f, indent=2)
        
        print("\n--------------------------------")
        print(f"Merge **complete**! Total features: {len(all_features)}")
        print(f"Output saved to: {output_path}")
        print("--------------------------------")

    except Exception as e:
        print(f"Fatal Error: Could not write output file to '{output_path}'. Reason: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="A Python script to merge multiple GeoJSON FeatureCollection files into a single output file.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Argument for input files (accepts one or more paths)
    parser.add_argument(
        '--geojson',
        nargs='+',
        required=True,
        help="One or more paths to input GeoJSON files, separated by spaces (e.g., file1.geojson file2.geojson)."
    )

    # Argument for the output file
    parser.add_argument(
        '--outputgeojson',
        required=True,
        help="Path to the new GeoJSON file to be created (e.g., merged_data.geojson)."
    )

    args = parser.parse_args()

    merge_geojson_files(args.geojson, args.outputgeojson)


if __name__ == "__main__":
    main()
