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
    note: draw rectangles form the upper left corner to the lower right corner

*   convert the labelme dataset to yolo format with 

    ```sh
    labelme2yolo --json_dir /path/to/labelme_json_dir/ --val_size 0.15 --test_size 0.15
    ```
*   Train a object detection model on the dataset 

    ```sh
    python train.py --path_to_yml /path/to/labelme_json_dir/config.yml
    ```    
*   Use the model for inference 

    ```sh
    python infer.py --yml /path/to/labelme_json_dir/config.yml --data path/to/folder/or/image.tif
    ```    
