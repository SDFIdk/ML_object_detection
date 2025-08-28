import argparse
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser(description="Train YOLOv8 with a YOLO-format dataset.")
    parser.add_argument('--data', type=str, required=True, help='Path to the YOLO-format data.yaml file')
    parser.add_argument('--weights', type=str, default='yolov8n.pt', help='Pretrained model or path to weights')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs to train')
    parser.add_argument('--imgsz', type=int, default=640, help='Image size for training')
    parser.add_argument('--device', type=str, default='cuda:0', help='Device to use, e.g., "cuda:0", "cpu", "0,1"')
    parser.add_argument('--image', type=str, help='Optional path to an image for inference after training')
    parser.add_argument('--export', action='store_true', help='If set, export the trained model to ONNX format')
    args = parser.parse_args()

    # Load YOLO model
    model = YOLO(args.weights)

    # Train the model
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        device=args.device,
    )

    # Validate the model
    model.val()

    # Run inference on an optional image
    if args.image:
        results = model(args.image)
        results[0].show()

    # Optionally export the model
    if args.export:
        export_path = model.export(format='onnx')
        print(f"Model exported to: {export_path}")

if __name__ == '__main__':
    main()
