# Synthseg-lesion
Using synthseg approach [1] to generate synthetic brains with lesions from labels for whole brain segmentation tasks. 

<img src="images/schema_methode_general.png"  />

Based on the [following paper](https://hal.science/hal-05123560): 

    Emma Lhermitte, Romain Valabregue, Mickael Dinomais, Rodrigo Araneda, Yannick Bleyenheuft, et al.. Synthetic learning: a novel approach for segmenting structures in children brains with perinatal stroke. 2025. ⟨hal-05123560⟩ 


## Installation instructions:
Clone the repository :
```bash
git clone https://github.com/emlhe/Synthseg-lesion.git
cd Synthseg-lesion
pip install -e .
```

## How to use:

### Data format 
1. All your images (labels, images and masks) must be normalized in a standard space, with the same dimensions
2. All your labels must be the same and consecutive
3. The folders must look like :

```bash   
    labels_folder/
    ├── id-sub-001_label.nii.gz
    ├── id-sub-002_label.nii.gz
    ├── id-sub-003_label.nii.gz
    ├── ...
```
```bash
    images_folder/
    ├── id-sub-001_image.nii.gz
    ├── id-sub-002_image.nii.gz
    ├── id-sub-003_image.nii.gz
    ├── ...
```
```bash
    masks_folder/
    ├── id-mask-001_mask.nii.gz
    ├── id-mask-002_mask.nii.gz
    ├── id-mask-003_mask.nii.gz
    ├── ...
```

4. The labels folder must contain a config.json file indicating the labels  

```bash
    { 
     "labels": {
       "background": 0,
       "label1": 1,
       "label1": 2
       ...
     }, 
     "ignore_labels": [0,4,...]
    }
```

```ignore_labels``` is a list of labels to preserve when pasting the lesion mask, such as the ventricles : should always be at least [0] to prevent from pasting voxels in the background.  

### Data generation 

1. Run ```python generate_synthetic_images.py``` script with the following parameters:
   
```bash
python generate_synthetic_images.py -inlab LABELS_FOLDER -inimg IMAGES_FOLDER -inmask MASKS_FOLDER -o OUTPUT_FOLDER -n X -lesaug True
```

```-n``` indicates the number of images to generate per subject. If ```-lesaug``` = True, perform lesion augmentation (random erosions and dilations) on the lesion masks prior pasting on the labels. In the output folder, imagesTr and labelsTr folders and dataset.json file will be created according to the nnUNet framework [2], to easily train nnUNet models after data generation. 


# References 

- [1] Billot, B., Greve, D., Van Leemput, K., Fischl, B., Iglesias, J. E., & Dalca, A. V. (2020). A learning strategy for contrast-agnostic MRI segmentation. arXiv preprint arXiv:2003.01995.
- [2] Isensee, F., Jaeger, P. F., Kohl, S. A., Petersen, J., & Maier-Hein, K. H. (2021). nnU-Net: a self-configuring 
method for deep learning-based biomedical image segmentation. Nature methods, 18(2), 203-211.