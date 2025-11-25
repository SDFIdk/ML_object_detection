# ML_object_detection

Maintained by the Danish Climate Data Agency for Bounding Box Detection on Oblique Images.

<img width="1124" height="1125" alt="image" src="https://github.com/user-attachments/assets/69aa5ca9-ac97-4a4b-98d5-b0820fc07f3c" />


## Installation

*   clone repo

    ```sh
    git clone https://github.com/SDFIdk/ML_object_detection
    ```
*   create conda environment
    ```sh
    cd ML_object_detection
    mamba env create -f environment.yml
    mamba activate  ML_object_detection
    ```  
  

## Example use
*   Use the included model for inference on one small and one large image from the included set of example images
    ```sh
    python src/ML_object_detection/infer_with_sahi.py --weights models/example_model.pt --folder_with_images data/example_images/ --result_folder output
    ```

## Create dataset for training

* split the images to sizes suitable for yolo
  
    python split_with_gdal.py --image /path/to/large/images --output dataset/folder --x 640 --y 640 --overlap 40
    
*   Create a dataset with labelme
    Open folder containing the splitted images
    for each image you want to train on, draw rectangles form the upper left corner to the lower right corner.
    OBS. All objects of the categoriez you want to detect needs to be marked up. Partly labeled images will ruin the training.

*   (optional) set all "unkown"/"ignore" areas to black
  if you labeled areas with the text "ignore" we have the option to mask all these areas and make them black.
    python  mask_unknown_regions.py -h


*    make sure that all .json files use the same format (original .tif image)
    python standardize_json.py --json_dir /mnt/T/mnt/trainingdata/object_detection/from_Fdrev_ampol/all/


*   convert the labelme dataset to yolo format with 

    ```sh
    labelme2yolo --json_dir /path/to/labelme_json_dir/ --val_size 0.15 --test_size 0.15
    e.g labelme2yolo --json_dir /mnt/T/mnt/trainingdata/object_detection/from_Fdrev_ampol/split/
    ```
*   Train a object detection model on the dataset 

    ```sh
    python train.py --data /path/to/labelme_json_dir/config.yml
    e.g e.g  python src/ML_object_detection/train.py --data /mnt/T/mnt/trainingdata/object_detection/object_detection_dataset/2025-06-16/labelme_images/YOLODataset/dataset.yaml
    ```    
*   Use the model for inference on large (unsplitted images) (e.g for creating sugestions for new labels) 

    ```sh
    python src/ML_object_detection/infer_with_sahi.py --weights models/example_model.pt --folder_with_images data/example_images/ --result_folder output

    ```    

