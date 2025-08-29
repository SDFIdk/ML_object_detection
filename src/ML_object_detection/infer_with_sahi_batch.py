import argparse
import os
import json
import torch
from sahi.predict import predict

def sahi_batch_inference(weights_path, folder_path, result_path, slice_width, overlap_ratio, batch_size):
    """
    Performs batch sliced inference on a folder of images using SAHI's predict function.
    
    Args:
        weights_path (str): Path to the YOLO model weights.
        folder_path (str): Path to the folder containing images.
        result_path (str): Path to save the output JSON file.
        slice_width (int): The width/height of each image slice.
        overlap_ratio (float): The overlap ratio between slices.
        batch_size (int): The number of image slices to process in a single batch.
    """
    try:
        results = predict(
            model_type="ultralytics",
            model_path=weights_path,
            model_device="cuda:0" if torch.cuda.is_available() else "cpu",
            model_confidence_threshold=0.3,
            source=folder_path,
            slice_height=slice_width,
            slice_width=slice_width,
            overlap_height_ratio=overlap_ratio,
            overlap_width_ratio=overlap_ratio,
            # The 'batch_size' parameter in the predict() function handles batching of slices internally
            # to speed up inference.
            #batch_size=batch_size, 
            #save_json=True,  # SAHI will save a single JSON file with all results
            #save_path=result_path,
            novisual=True, # Set to True to prevent saving visualizations and only save JSON
            #force_sliced_prediction=True
        )

        print(f"Inference complete. Results saved to {result_path}")
    
    except Exception as e:
        print(f"Error during inference: {e}")
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run batch sliced object detection on large images using SAHI.")
    parser.add_argument("--weights", required=True, help="Path to the YOLO model weights file (e.g., best.pt).")
    parser.add_argument("--folder_with_images", required=True, help="Path to the folder containing the images.")
    parser.add_argument("--result_path", required=True, help="Path to the output JSON file to save results.")
    parser.add_argument("--slice_width", type=int, default=640, help="Width of the image slices (default: 640).")
    parser.add_argument("--overlap_ratio", type=float, default=0.0625, help="Overlap ratio between slices (default: 0.0625).")
    parser.add_argument("--batch_size", type=int, default=16, help="Number of slices to process in each batch (default: 16).")

    args = parser.parse_args()

    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.result_path), exist_ok=True)

    sahi_batch_inference(
        args.weights, 
        args.folder_with_images, 
        args.result_path, 
        args.slice_width, 
        args.overlap_ratio, 
        args.batch_size
    )
