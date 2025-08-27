import argparse
import json
from pathlib import Path
import cv2
from ultralytics import YOLO

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
    image = cv2.imread(str(image_path))
    height, width = image.shape[:2]

    return {
        "version": "5.0.1",
        "flags": {},
        "shapes": shapes,
        "imagePath": image_path.name,
        "imageData": None,
        "imageHeight": height,
        "imageWidth": width,
    }

def detect_and_save_json(model_path, image_dir,output_dir):
    model = YOLO(model_path)
    image_dir = Path(image_dir)
    output_dir =  Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_paths = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png")) + list(image_dir.glob("*.tif"))

    for image_path in image_paths:
        print(f"Processing {image_path.name}")
        results = model(image_path)
        shapes = []

        for r in results:
            for box, cls in zip(r.boxes.xyxy, r.boxes.cls):
                shape = yolo_to_labelme_shape(box.tolist(), model.names[int(cls)])
                shapes.append(shape)

        json_dict = create_labelme_json_dict(image_path, shapes)
        json_path = output_dir/(image_path.with_suffix(".json").name)

        with open(json_path, "w") as f:
            json.dump(json_dict, f, indent=2)

        print(f"Saved: {json_path}")

def main():
    parser = argparse.ArgumentParser(description="Run YOLOv8 and export LabelMe-compatible JSON annotations.")
    parser.add_argument("--path_to_trained_model", type=str, required=True, help="Path to YOLOv8 model")
    parser.add_argument("--path_to_images", type=str, required=True, help="Path to image folder")
    parser.add_argument("--output_folder", type=str, required=True, help="Path to output folder")
    args = parser.parse_args()

    detect_and_save_json(args.path_to_trained_model, args.path_to_images,args.output_folder)

if __name__ == "__main__":
    main()
