import torchio as tio
import argparse
import matplotlib.pyplot as plt
import numpy as np
from synthsegLesion.utilities.utils import get_files_paths, load_in_torchio_subjects, check_labels
from synthsegLesion.data_augmentation.custom_transforms.random_mask_pasting import RandomPasteMask
import os
from tqdm import tqdm

## TODO Check mask, labels and image size
### TODO Adding a second class ? only if brain MRIs with stroke are present 

def entry_point_generate_synthetic_images():
    parser = argparse.ArgumentParser(description='descr')
    parser.add_argument('-n', type=int, default=1, help='Number of images per subject to generate')
    parser.add_argument('-inlab', '--in_labels', type=str, help='Path of the directory containing the labels nifti files')
    parser.add_argument('-inimg', '--in_image', type=str, help='Path of the directory containing the nifti files of the images corresponding to the labels')
    parser.add_argument('-inmask', '--in_masks', type=str, help='Path of the directory containing the lesions masks nifti files')
    # parser.add_argument('-int1w', '--in_t1w', type=str, help='Path of the directory containing the t1w nifti files of the images corresponding to the masks (for lesion augmentation)')
    parser.add_argument('-lesaug', '--lesion_augmentations', type=bool, default=False, help='If true, augmentations are performed on the lesion masks prior pasting on the labels')
    parser.add_argument('-o', '--out', type=str, default=False, help='Output folder for synthetic images')
    args = parser.parse_args()

    generate_synthetic_images(args.in_labels, args.in_image, args.in_masks, args.out, args.lesion_augmentations, args.n)


def generate_synthetic_images(labels_folder, images_folder, masks_folder, output_folder, lesion_augmentations, n_gen):

    print(output_folder)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    dataset = get_files_paths(labels_folder, images_folder, ".nii.gz")
    masks_dataset = get_files_paths(masks_folder, file_ending=".nii.gz")

    subjects_labels_list = load_in_torchio_subjects(dataset)

    # Check if all labels are the same 
    check_labels(subjects_labels_list, [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17])

    # Create transforms
    paste_mask_tr = RandomPasteMask(masks_dataset, label_key="label", augment=lesion_augmentations, ignore_labels=[0,4,14,15])
    synth_tr = tio.RandomLabelsToImage(label_key='label',image_key='synth')
    transforms=[paste_mask_tr, synth_tr]
    transform = tio.Compose(transforms)

    # Apply to the subjects : 
    subjects_dataset = tio.SubjectsDataset(subjects_labels_list, transform=transform)

    for i in tqdm(range(0,len(subjects_dataset))):
        for n in tqdm(range(0,n_gen)):
            subject = subjects_dataset[i]
            print(f"{subject.id} saved in {os.path.join(output_folder, f'{subject.id}_...')}")
            subject.label.save(path=os.path.join(output_folder, f"{subject.id}_label_{n}.nii.gz"))
            subject.synth.save(path=os.path.join(output_folder, f"{subject.id}_synth_{n}.nii.gz"))


if __name__ == '__main__':
    entry_point_generate_synthetic_images()