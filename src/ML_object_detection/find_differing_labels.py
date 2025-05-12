# Import necessary libraries
import argparse
import json
import os
import shutil
from glob import glob
from pathlib import Path
from typing import List, Tuple

# Function to parse command-line arguments
def parse_args():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Find differing labels between two folders of labelme annotations.")
    parser.add_argument("--folder1", required=True, help="Path to the first folder containing images and JSON annotations.")
    parser.add_argument("--folder2", required=True, help="Path to the second folder containing JSON annotations.")
    parser.add_argument("--output", required=True, help="Path to the output directory to save results.")
    parser.add_argument("--overlap", type=float, default=0.5, help="IoU threshold for considering bounding boxes as overlapping (default: 0.5).")
    # --- New Argument ---
    parser.add_argument("--only_save_boundingboxes_from_folder_1", action='store_true',
                        help="If set, only save bounding boxes from folder1 that do not overlap with folder2.")
    return parser.parse_args()

# Function to load JSON data from a file
def load_json(path: Path):
    """
    Loads JSON data from the specified file path.

    Args:
        path: The path to the JSON file.

    Returns:
        The loaded JSON data (typically a dictionary).
    """
    with open(path) as f:
        return json.load(f)

# Function to save JSON data to a file
def save_json(data, path: Path):
    """
    Saves data to a JSON file with indentation.

    Args:
        data: The data (e.g., dictionary) to save.
        path: The path where the JSON file will be saved.
    """
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Function to convert labelme points to a bounding box
def bbox_from_points(points: List[List[float]]) -> Tuple[float, float, float, float]:
    """
    Convert 2-point 'rectangle' labelme shape to (xmin, ymin, xmax, ymax).

    Args:
        points: A list containing two points [[x1, y1], [x2, y2]].

    Returns:
        A tuple representing the bounding box: (xmin, ymin, xmax, ymax).
    """
    # Handle cases where points might not be in min/max order
    (x1, y1), (x2, y2) = points
    return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)

# Function to calculate Intersection over Union (IoU)
def iou(b1, b2) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.

    Args:
        b1: The first bounding box (xmin, ymin, xmax, ymax).
        b2: The second bounding box (xmin, ymin, xmax, ymax).

    Returns:
        The IoU score (float between 0.0 and 1.0).
    """
    x1, y1, x2, y2 = b1
    x1_, y1_, x2_, y2_ = b2

    # Determine the coordinates of the intersection rectangle
    inter_x1 = max(x1, x1_)
    inter_y1 = max(y1, y1_)
    inter_x2 = min(x2, x2_)
    inter_y2 = min(y2, y2_)

    # Calculate the area of intersection rectangle
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)

    # Calculate the area of both bounding boxes
    area1 = (x2 - x1) * (y2 - y1)
    area2 = (x2_ - x1_) * (y2_ - y1_)

    # Calculate the area of union
    union_area = area1 + area2 - inter_area

    # Compute the IoU
    # Avoid division by zero if union area is 0
    return inter_area / union_area if union_area > 0 else 0

# --- Modified Function ---
# Function to filter shapes based on IoU and the new flag
def filter_shapes(shapes1, shapes2, threshold, only_keep_folder1=False): # Added only_keep_folder1 parameter
    """
    Filters shapes based on IoU overlap.

    Args:
        shapes1: List of shapes (dictionaries) from the first JSON file.
        shapes2: List of shapes (dictionaries) from the second JSON file.
        threshold: The IoU threshold. Shapes with IoU <= threshold with all shapes
                   in the other list are considered non-overlapping.
        only_keep_folder1: If True, only return non-overlapping shapes from shapes1.
                           If False, return non-overlapping shapes from both lists.

    Returns:
        A list of filtered shapes (dictionaries).
    """
    # Extract bounding boxes for efficient calculation
    # Store original shape along with its bounding box
    # Only consider 'rectangle' shapes for IoU comparison
    boxes1 = [(s, bbox_from_points(s["points"])) for s in shapes1 if s.get("shape_type") == "rectangle"]
    boxes2 = [(s, bbox_from_points(s["points"])) for s in shapes2 if s.get("shape_type") == "rectangle"]

    # Find shapes in shapes1 that do *not* significantly overlap with any shape in shapes2
    keep1 = [s1 for s1, b1 in boxes1 if all(iou(b1, b2) <= threshold for _, b2 in boxes2)]

    # --- Conditional Logic Based on Flag ---
    if only_keep_folder1:
        # If the flag is set, only return the non-overlapping shapes from folder1
        return keep1 # Only return shapes from the first list
    else:
        # Original behavior: also find shapes in shapes2 that do not overlap with shapes1
        keep2 = [s2 for s2, b2 in boxes2 if all(iou(b2, b1) <= threshold for _, b1 in boxes1)]
        # Return the combined list of non-overlapping shapes from both folders
        return keep1 + keep2

# --- Modified Function ---
# Main processing function
def process(folder1, folder2, output, overlap, only_save_folder1_bboxes): # Added only_save_folder1_bboxes parameter
    """
    Processes the folders, finds differing labels, and saves the results.

    Args:
        folder1: Path to the first folder.
        folder2: Path to the second folder.
        output: Path to the output directory.
        overlap: IoU threshold.
        only_save_folder1_bboxes: Boolean flag indicating whether to only save
                                     non-overlapping bounding boxes from folder1.
    """
    os.makedirs(output, exist_ok=True) # Ensure output directory exists
    # Find all JSON files in the first folder
    json_files1 = sorted(glob(str(Path(folder1) / "*.json")))

    print(f"Found {len(json_files1)} JSON files in {folder1}")

    processed_count = 0
    # Iterate through each JSON file in the first folder
    for json_file1_path in json_files1:
        json_file1_path = Path(json_file1_path)
        name = json_file1_path.stem # Get the base name without extension

        # Load the JSON data from the first file to find the corresponding image path
        try:
            data1 = load_json(json_file1_path)
            # Handle potential missing imagePath or different image extensions
            img_path_in_json = data1.get("imagePath")
            if not img_path_in_json:
                 print(f"Warning: 'imagePath' missing in {json_file1_path}. Skipping.")
                 continue
            img_suffix = Path(img_path_in_json).suffix # Get image suffix from JSON
            img_file1_path = Path(folder1) / (name + img_suffix)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {json_file1_path}. Skipping.")
            continue
        except Exception as e:
            print(f"Error processing {json_file1_path}: {e}")
            continue # Skip this file if loading fails or imagePath is missing

        # Construct the expected path for the corresponding JSON file in the second folder
        json_file2_path = Path(folder2) / (name + ".json")

        # Check if the corresponding JSON file exists in the second folder
        if not os.path.exists(json_file2_path):
            # print(f"Skipping {name}: Corresponding JSON not found in {folder2}")
            continue # Skip if the corresponding file doesn't exist

        # Check if the corresponding image file exists in the first folder
        if not os.path.exists(img_file1_path):
            print(f"Skipping {name}: Image file {img_file1_path.name} not found in {folder1}")
            continue # Skip if the image file is missing

        # Load shapes from both JSON files
        try:
            shapes1 = data1.get("shapes", [])
            data2 = load_json(json_file2_path)
            shapes2 = data2.get("shapes", [])
        except json.JSONDecodeError:
             print(f"Error decoding JSON from {json_file2_path}. Skipping {name}.")
             continue
        except Exception as e:
            print(f"Error loading shapes from {json_file1_path} or {json_file2_path}: {e}")
            continue # Skip if shape loading fails

        # Filter shapes based on the overlap threshold and the new flag
        # Pass the value of the command-line flag here
        filtered_shapes = filter_shapes(shapes1, shapes2, overlap, only_save_folder1_bboxes) # Pass the flag value

        # If there are differing shapes, process and save the output
        if filtered_shapes:
            processed_count += 1
            # Define the output image path
            out_img_path = Path(output) / img_file1_path.name
            # Copy the image file to the output directory
            try:
                shutil.copy(img_file1_path, out_img_path)
            except Exception as e:
                print(f"Error copying image {img_file1_path} to {out_img_path}: {e}")
                continue # Skip if image copy fails

            # Create the output JSON data structure
            # Use the data from the first file as a base
            base_data = data1
            # Replace the shapes with the filtered list
            base_data["shapes"] = filtered_shapes
            # Update the image path to point to the copied image in the output folder
            base_data["imagePath"] = out_img_path.name # Use relative path name

            # Define the output JSON file path
            out_json_path = Path(output) / (name + ".json")
            # Save the new JSON data
            try:
                save_json(base_data, out_json_path)
            except Exception as e:
                print(f"Error saving JSON {out_json_path}: {e}")
                # Clean up the copied image if JSON saving fails
                if os.path.exists(out_img_path):
                    try:
                        os.remove(out_img_path)
                        print(f"Removed partially copied image {out_img_path.name} due to JSON save error.")
                    except OSError as rm_err:
                        print(f"Error removing image {out_img_path.name} after JSON save error: {rm_err}")
                continue # Continue to the next file

    print(f"Processing complete. Saved results for {processed_count} images with differing labels to {output}")

# Entry point of the script
if __name__ == "__main__":
    # Parse the command-line arguments
    args = parse_args()
    # Run the main processing function with the parsed arguments
    # Pass the value of the new argument to the process function
    process(args.folder1, args.folder2, args.output, args.overlap, args.only_save_boundingboxes_from_folder_1)
