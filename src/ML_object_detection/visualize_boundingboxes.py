import argparse
import json
from pathlib import Path
import numpy as np
import rasterio
from rasterio.features import rasterize
from shapely.geometry import box


def get_color_map(labels):
    """
    Assign a unique RGB color per class label.
    """
    base_colors = [
        (255, 0, 0),     # Red
        (0, 255, 0),     # Green
        (0, 0, 255),     # Blue
        (255, 165, 0),   # Orange
        (128, 0, 128),   # Purple
        (0, 255, 255),   # Cyan
        (255, 192, 203), # Pink
        (255, 255, 0),   # Yellow
    ]
    return {label: base_colors[i % len(base_colors)] for i, label in enumerate(labels)}


def draw_bounding_boxes_rasterio(image_path, json_path, output_path):
    # Load JSON bounding boxes
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    shapes = data.get("shapes", [])
    labels = list({shape["label"] for shape in shapes})
    label_to_color = get_color_map(labels)

    # Open large image with rasterio
    with rasterio.open(image_path) as src:
        meta = src.meta.copy()

        # Ensure output has 3 bands (RGB)
        meta.update(count=3, dtype="uint8", compress="deflate", BIGTIFF="YES")

        # Read original image into memory (careful if extremely large!)
        img_data = src.read(out_dtype="uint8")

        # If grayscale, expand to RGB
        if img_data.shape[0] == 1:
            img_data = np.repeat(img_data, 3, axis=0)

    # Create overlay mask for bounding boxes
    overlay = np.zeros_like(img_data, dtype=np.uint8)

    # Rasterize each bounding box into overlay
    for shape in shapes:
        print("new shape")
        if shape.get("shape_type") != "rectangle":
            continue
        pts = shape["points"]
        (x1, y1), (x2, y2) = pts
        print((x1, y1))
        geom = box(x1, y1, x2, y2)
        color = label_to_color.get(shape["label"], (255, 255, 255))

        # Burn each channel separately
        for band, val in enumerate(color):
            mask = rasterize(
                [(geom, val)],
                out_shape=(overlay.shape[1], overlay.shape[2]),
                transform=src.transform,
                fill=0,
                dtype="uint8"
            )
            overlay[band] = np.maximum(overlay[band], mask)

    # Combine original image + overlay (overlay just replaces pixels on boxes)
    img_out = np.where(overlay > 0, overlay, img_data)

    # Save new TIFF
    with rasterio.open(output_path, "w", **meta) as dst:
        dst.write(img_out)


def main():
    parser = argparse.ArgumentParser(description="Draw bounding boxes on a huge TIFF using rasterio")
    parser.add_argument("--largeimage", required=True, help="Path to the large input TIFF image")
    parser.add_argument("--json", required=True, help="Path to the merged JSON file with bounding boxes")
    parser.add_argument("--new_large_tiff", required=True, help="Path to the output TIFF with drawn boxes")
    args = parser.parse_args()

    draw_bounding_boxes_rasterio(args.largeimage, args.json, args.new_large_tiff)


if __name__ == "__main__":
    main()
