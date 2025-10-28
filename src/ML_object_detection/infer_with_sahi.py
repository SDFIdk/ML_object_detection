#when testing this code it managed 14.8 seconds per large image. This is not the fastest posible.

import argparse
import os
import json
import torch
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
from tqdm import tqdm
import time
import pathlib
import tifffile

def get_image_size(image_path):
    with tifffile.TiffFile(image_path) as tif:
        page = tif.pages[0]
        height, width = page.shape[:2]
    return width, height

def yolo_to_labelme_shape(box, label):
    """Convert YOLO bounding box to LabelMe rectangle shape"""
    x1, y1, x2, y2 = map(float, box)
    x1, x2 = sorted([x1, x2])
    y1, y2 = sorted([y1, y2])
    return {
        "label": label,
        "points": [[x1, y1], [x2, y2]],
        "group_id": None,
        "shape_type": "rectangle",
        "flags": {}
    }

def create_labelme_json_dict(image_path, shapes):

    width, height = get_image_size(str(image_path))

    return {
        "version": "5.0.1",
        "flags": {},
        "shapes": shapes,
        "imagePath": image_path.name,
        "imageData": None,
        "imageHeight": height,
        "imageWidth": width,
    }


def sahi_inference(weights_path, folder_path, result_folder, slice_width, overlap_ratio):
    """
    Performs sliced inference on a folder of images using SAHI and YOLO.
    
    Args:
        weights_path (str): Path to the YOLO model weights.
        folder_path (str): Path to the folder containing images.
        result_folder (str): Path to save the output JSON file.
        slice_width (int): The width of each image slice.
        overlap_ratio (float): The overlap ratio between slices.
    """
    # Initialize the detection model
    try:
        detection_model = AutoDetectionModel.from_pretrained(
            model_type='yolov8',
            model_path=weights_path,
            confidence_threshold=0.3,
            device="cuda:0" if torch.cuda.is_available() else "cpu"
        )
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    print("detection_model.names:"+str(detection_model.model.names))
    # List image files in the folder
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp', '.gif'))]
    
    if not image_files:
        print("No image files found in the specified folder.")
        return

    all_detections = {}

    print(f"Found {len(image_files)} images. Starting inference...")
    start_time=time.time()

    for image_name in tqdm(image_files, desc="Processing Images"):
        image_path = pathlib.Path(os.path.join(folder_path, image_name))
        
        if True: #try:
            result_path = (pathlib.Path(result_folder)/pathlib.Path(image_path).name).with_suffix(".json")
            # Perform sliced prediction with user-defined slice parameters
            result = get_sliced_prediction(
                str(image_path),
                detection_model,
                slice_height=slice_width,  # Assuming a square slice
                slice_width=slice_width,
                overlap_height_ratio=overlap_ratio,
                overlap_width_ratio=overlap_ratio
            )



        results = result
        shapes = []

        for r in results.object_prediction_list:
            #print("r:"+str(r))
            #print(" pred.category.name:"+str(r.category.name))
            #print("bbox  : "+str(r.bbox))
            #print("bbox  : "+str(dir(r.bbox)))
            #print("bbox  : "+str(r.bbox.to_xyxy()))

            shape = yolo_to_labelme_shape(r.bbox.to_xyxy(), r.category.name)
            shapes.append(shape)



            #bbox = pred.bbox.minx, pred.bbox.miny, pred.bbox.maxx, pred.bbox.maxy
            #confidence = pred.score.value
            #for box, cls in zip(r.boxes.xyxy, r.boxes.cls):
            #    shape = yolo_to_labelme_shape(bbox.tolist(), detection_model.model.names[int(category)])
            #    shapes.append(shape)

        json_dict = create_labelme_json_dict(image_path, shapes)
        json_path = pathlib.Path(result_folder)/(image_path.with_suffix(".json").name)

        with open(json_path, "w") as f:
            json.dump(json_dict, f, indent=2)

        print(f"Saved: {json_path}")
    
    print("inference took (seconds): "+str(time.time()-start_time))
    print("inference per image(seconds): "+str((time.time()-start_time)/len(image_files)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run sliced object detection on large images using SAHI.")
    parser.add_argument("--weights", required=True, help="Path to the YOLO model weights file (e.g., best.pt).")
    parser.add_argument("--folder_with_images", required=True, help="Path to the folder containing the images.")
    parser.add_argument("--result_folder", required=True, help="Path to a foloder where the output JSON file should be saved.")
    parser.add_argument("--slice_width", type=int, default=640, help="Width of the image slices (default: 640).")
    parser.add_argument("--overlap_ratio", type=float, default=0.0625, help="Overlap ratio between slices (default: 0.0625).")

    args = parser.parse_args()


    print("GPU is available: "+str(torch.cuda.is_available()))

    # Create the output directory if it doesn't exist
    os.makedirs(args.result_folder, exist_ok=True)

    sahi_inference(
        args.weights, 
        args.folder_with_images, 
        args.result_folder, 
        args.slice_width, 
        args.overlap_ratio
    )
