 #when testing this code it managed 14.8 seconds per alrge image. This is not the fastest posible.

import argparse
import os
import json
import torch
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
from tqdm import tqdm
import time
def sahi_inference(weights_path, folder_path, result_path, slice_width, overlap_ratio):
    """
    Performs sliced inference on a folder of images using SAHI and YOLO.
    
    Args:
        weights_path (str): Path to the YOLO model weights.
        folder_path (str): Path to the folder containing images.
        result_path (str): Path to save the output JSON file.
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

    # List image files in the folder
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp', '.gif'))]
    
    if not image_files:
        print("No image files found in the specified folder.")
        return

    all_detections = {}

    print(f"Found {len(image_files)} images. Starting inference...")
    start_time=time.time()

    for image_name in tqdm(image_files, desc="Processing Images"):
        image_path = os.path.join(folder_path, image_name)
        
        try:
            # Perform sliced prediction with user-defined slice parameters
            result = get_sliced_prediction(
                image_path,
                detection_model,
                slice_height=slice_width,  # Assuming a square slice
                slice_width=slice_width,
                overlap_height_ratio=overlap_ratio,
                overlap_width_ratio=overlap_ratio
            )

            # Convert results to a dictionary
            detections_for_image = []
            for pred in result.object_prediction_list:
                bbox = pred.bbox.minx, pred.bbox.miny, pred.bbox.maxx, pred.bbox.maxy
                category = pred.category.name
                confidence = pred.score.value
                detections_for_image.append({
                    "bbox": [int(b) for b in bbox],
                    "category": category,
                    "confidence": float(confidence)
                })
            
            all_detections[image_name] = detections_for_image
        
        except Exception as e:
            print(f"Error processing {image_name}: {e}")

    # Save results to a JSON file
    with open(result_path, 'w') as f:
        json.dump(all_detections, f, indent=4)
    
    print(f"Inference complete. Results saved to {result_path}")
    print("inference took (seconds): "+str(time.time()-start_time))
    print("inference per image(seconds): "+str((time.time()-start_time)/len(image_files)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run sliced object detection on large images using SAHI.")
    parser.add_argument("--weights", required=True, help="Path to the YOLO model weights file (e.g., best.pt).")
    parser.add_argument("--folder_with_images", required=True, help="Path to the folder containing the images.")
    parser.add_argument("--result_path", required=True, help="Path to the output JSON file to save results.")
    parser.add_argument("--slice_width", type=int, default=640, help="Width of the image slices (default: 640).")
    parser.add_argument("--overlap_ratio", type=float, default=0.0625, help="Overlap ratio between slices (default: 0.0625).")

    args = parser.parse_args()

    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.result_path), exist_ok=True)

    sahi_inference(
        args.weights, 
        args.folder_with_images, 
        args.result_path, 
        args.slice_width, 
        args.overlap_ratio
    )
