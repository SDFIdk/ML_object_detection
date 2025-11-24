# ML_object_detection

Maintained by the Danish Climate Data Agency for Bounding Box Detection on Oblique Images.

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





*   Create a dataset with labelme
    split dataset like this 
    python split_with_gdal.py --image /path/to/large/images --output dataset/folder --x 640 --y 640 --overlap 40


* copy all data to a new location before doing the next steps

    note: draw rectangles form the upper left corner to the lower right corner

    NOTE:if data is on the old ITU NAS you have to moove the dataset to a local folder the the user have rights to change mete data on 

*   set all "unkown"/"ignore" areas to black 
    python  mask_unknown_regions.py -h



    make sure that all .json files use the same format (original .tif image)
    python standardize_json.py --json_dir /mnt/T/mnt/trainingdata/object_detection/from_Fdrev_ampol/all/


*   convert the labelme dataset to yolo format with 

    ```sh
    labelme2yolo --json_dir /path/to/labelme_json_dir/ --val_size 0.15 --test_size 0.15
    e.g labelme2yolo --json_dir /mnt/T/mnt/trainingdata/object_detection/from_Fdrev_ampol/split/
    ```
*   Train a object detection model on the dataset 

    ```sh
    python train.py --data /path/to/labelme_json_dir/config.yml
    ```    
*   Use the model for inference on large (unsplitted images) (e.g for creating sugestions for new labels) 

    ```sh
    python src/ML_object_detection/infer_with_sahi.py --weights models/example_model.pt --folder_with_images data/example_images/ --result_folder output

    ```    

