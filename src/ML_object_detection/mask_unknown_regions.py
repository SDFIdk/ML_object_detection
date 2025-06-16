#OBS! not tested! 

# if an area is difficult to label , simple label that area to "unknown" or "ignore", and use this script to set those areas to  black
# remember to remove the "ignore" class afterwards from the yololabel files!
import json
import cv2
import numpy as np
import os
from glob import glob

def mask_unknown_regions(json_path, out_img_dir):
    with open(json_path) as f:
        data = json.load(f)

    img_path = os.path.join(os.path.dirname(json_path), data['imagePath'])
    img = cv2.imread(img_path)

    if img is None:
        print(f"⚠️ Warning: Could not load image {img_path}")
        return
    print(img.shape[:2])
    mask = np.zeros(img.shape[:2], dtype=np.uint8)

    for shape in data['shapes']:
        if shape['label'].lower() not in ['unknown', 'ignore']:
            continue

        shape_type = shape.get('shape_type', 'polygon')
        pts = shape['points']

        if shape_type == 'rectangle':
            # Convert two corners to top-left and bottom-right
            (x1, y1), (x2, y2) = pts
            x1, x2 = int(round(min(x1, x2))), int(round(max(x1, x2)))
            y1, y2 = int(round(min(y1, y2))), int(round(max(y1, y2)))
            print([(x1, y1), (x2, y2)])
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, thickness=-1)
        elif shape_type == 'polygon':
            pts_np = np.array(pts, dtype=np.int32)
            cv2.fillPoly(mask, [pts_np], 255)
        else:
            print(f"⚠️ Unsupported shape_type: {shape_type}")

        input("sum is : "+str(max(mask.flatten())))
    # Apply white color to masked region

    img[mask == 255] = [255, 255, 255]

    os.makedirs(out_img_dir, exist_ok=True)
    out_path = os.path.join(out_img_dir, os.path.basename(img_path))
    cv2.imwrite(out_path, img)
    print(f"✅ Masked image saved: {out_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_dir', required=True, help='Folder with LabelMe JSON files')
    parser.add_argument('--out_img_dir', required=True, help='Where to save masked images')
    args = parser.parse_args()

    for json_file in glob(os.path.join(args.json_dir, '*.json')):
        mask_unknown_regions(json_file, args.out_img_dir)
