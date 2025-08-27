import argparse
import json
import re
from pathlib import Path

def parse_offset_from_filename(filename: str):
    match = re.search(r"_x_(\d+)_y_(\d+)", filename)
    if not match:
        raise ValueError(f"Could not parse offsets from filename: {filename}")
    return int(match.group(1)), int(match.group(2))


def update_shape_points(shapes, offset_x, offset_y):
    updated_shapes = []
    for shape in shapes:
        new_shape = shape.copy()
        new_shape["points"] = [
            [pt[0] + offset_x, pt[1] + offset_y] for pt in shape["points"]
        ]
        updated_shapes.append(new_shape)
    return updated_shapes


def get_image_size(image_path: Path):
    """
    Efficiently get image width, height without reading full image.
    Supports TIFF (via tifffile) and other formats (via Pillow fallback).
    """
    try:
        import tifffile
        with tifffile.TiffFile(image_path) as tif:
            page = tif.pages[0]
            return page.imagewidth, page.imagelength
    except Exception:
        from PIL import Image
        with Image.open(image_path) as img:
            return img.size


def merge_jsons(input_folder, output_json, large_image_path):
    all_shapes = []
    large_image_path = Path(large_image_path)
    large_basename = large_image_path.stem

    # Efficiently get image size
    large_width, large_height = get_image_size(large_image_path)

    merged_metadata = None

    for json_file in Path(input_folder).glob("*.json"):
        if not json_file.name.startswith(large_basename + "_x_"):
            continue

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if merged_metadata is None:
            merged_metadata = data.copy()

        offset_x, offset_y = parse_offset_from_filename(json_file.name)
        updated_shapes = update_shape_points(data["shapes"], offset_x, offset_y)
        all_shapes.extend(updated_shapes)

    if merged_metadata is None:
        raise RuntimeError(f"No matching JSON files found for {large_basename}")

    merged_metadata["shapes"] = all_shapes
    merged_metadata["imagePath"] = str(large_image_path)
    merged_metadata["imageData"] = None
    merged_metadata["imageHeight"] = large_height
    merged_metadata["imageWidth"] = large_width

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(merged_metadata, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Merge cropped JSONs into one full-image JSON")
    parser.add_argument("--splitted_json_folder", required=True, help="Folder containing cropped JSON files")
    parser.add_argument("--output_json", required=True, help="Path to output merged JSON")
    parser.add_argument("--large_image", required=True, help="Path to the large image file")
    args = parser.parse_args()
    merge_jsons(args.splitted_json_folder, args.output_json, args.large_image)


if __name__ == "__main__":
    main()
