# ML_object_detection


## Installation

*   clone repo

    ```sh
    git clone https://github.com/SDFIdk/ML_object_detection
    ```
*   create conda environment
    ```sh
    mamba create env -f environment.yml
    ```  
  

## Example use

*   Create a dataset with labelme
    split dataset like this 
    python split_with_gdal.py --image /path/to/large/images --output dataset/folder --x 640 --y 640 --overlap 40

    note: draw rectangles form the upper left corner to the lower right corner

*   convert the labelme dataset to yolo format with 

    ```sh
    labelme2yolo --json_dir /path/to/labelme_json_dir/ --val_size 0.15 --test_size 0.15
    e.g labelme2yolo --json_dir /mnt/T/mnt/trainingdata/object_detection/from_Fdrev_ampol/split/
    ```
*   Train a object detection model on the dataset 

    ```sh
    python train.py --path_to_yml /path/to/labelme_json_dir/config.yml
    ```    
*   Use the model for inference (e.g for creating sugestions for new labels) 

    ```sh

    python infer_to_labelme_json.py --path_to_trained_model runs/detect/train/weights/last.pt --path_to_images ~/object_detection_dataset/split_unlabeled/
    ```    
