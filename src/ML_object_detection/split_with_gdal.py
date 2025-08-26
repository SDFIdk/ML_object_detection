import os
import argparse
from osgeo import gdal

def split_geotiff(image_path, output_dir, tile_width, tile_height, overlap):
    os.makedirs(output_dir, exist_ok=True)
    ds = gdal.Open(image_path)
    if ds is None:
        raise FileNotFoundError(f"Could not open {image_path}")

    img_width = ds.RasterXSize
    img_height = ds.RasterYSize

    x_step = tile_width - overlap
    y_step = tile_height - overlap

    tile_count = 0
    for y in range(0, img_height, y_step):
        for x in range(0, img_width, x_step):
            w = min(tile_width, img_width - x)
            h = min(tile_height, img_height - y)

            output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(image_path))[0]}_x_{x}_y_{y}.tif")
            gdal.Translate(
                output_path,
                ds,
                srcWin=[x, y, w, h],
                creationOptions=["COMPRESS=LZW"]
            )
            tile_count += 1

    print(f"Created {tile_count} tiles from '{image_path}' in '{output_dir}'.")

def process_input(input_path, output_dir, tile_width, tile_height, overlap):
    if os.path.isdir(input_path):
        for fname in os.listdir(input_path):
            full_path = os.path.join(input_path, fname)
            if fname.lower().endswith(".tif") and os.path.isfile(full_path):
                split_geotiff(full_path, output_dir, tile_width, tile_height, overlap)
    elif os.path.isfile(input_path):
        split_geotiff(input_path, output_dir, tile_width, tile_height, overlap)
    else:
        raise FileNotFoundError(f"{input_path} does not exist or is not a valid file/directory")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split GeoTIFF(s) into tiles.")
    parser.add_argument("--image", required=True, help="Path to input GeoTIFF or directory containing GeoTIFFs")
    parser.add_argument("--output", required=True, help="Directory to save tiles")
    parser.add_argument("--x", type=int, required=True, help="Tile width in pixels")
    parser.add_argument("--y", type=int, required=True, help="Tile height in pixels")
    parser.add_argument("--overlap", type=int, default=0, help="Overlap in pixels")

    args = parser.parse_args()
    process_input(args.image, args.output, args.x, args.y, args.overlap)
