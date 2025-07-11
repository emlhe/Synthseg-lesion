import torchio as tio
import argparse
import matplotlib.pyplot as plt
import numpy as np
from synthsegLesion.utilities.utils import get_files_paths, load_in_torchio_subjects, check_labels
from synthsegLesion.data_augmentation.custom_transforms.random_mask_pasting import RandomPasteMask
import os
from tqdm import tqdm
import json
import sys

def entry_point_generate_synthetic_images():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=1, help='Number of images to generate per subject')
    parser.add_argument('-inlab', '--in_labels', type=str, help='Path of the directory containing the labels nifti files')
    parser.add_argument('-inimg', '--in_image', type=str, help='Path of the directory containing the nifti files of the images corresponding to the labels')
    parser.add_argument('-inmask', '--in_masks', type=str, help='Path of the directory containing the lesions masks nifti files')
    # parser.add_argument('-int1w', '--in_t1w', type=str, help='Path of the directory containing the t1w nifti files of the images corresponding to the masks (for lesion augmentation)')
    parser.add_argument('-lesaug', '--lesion_augmentations', type=bool, default=False, help='If true, augmentations are performed on the lesion masks prior pasting on the labels')
    parser.add_argument('-o', '--out', type=str, default=False, help='Output folder for synthetic images')
    args = parser.parse_args()

    transform_file = "./synthsegLesion/config_files/transforms.json"

    generate_synthetic_images(args.in_labels, args.in_image, args.in_masks, args.out, args.lesion_augmentations, args.n, transform_file)

def get_transform_from_json(json_file):
    with open(json_file) as f:
        transfo_st = json.load(f)
    train_transfo = parse_transform(transfo_st['train_transforms'],'train_transforms')
    motion_transfo = parse_transform(transfo_st['motion_transforms'],'motion_transforms')
    return tio.Compose([train_transfo, motion_transfo])

def parse_transform(t, transfo_name):
    # Based on https://github.com/romainVala/Synthetic_learning_on_dHCP
    if isinstance(t, list):
        transfo_list = [parse_transform(tt, transfo_name) for tt in t]
        if transfo_name == 'train_transforms':
            return tio.Compose(transfo_list)
        elif transfo_name == 'motion_transforms':
            return tio.OneOf(transfo_list, p=0.5)
    
    attributes = t.get('attributes') or {}

    t_class = getattr(tio.transforms, t['name'])
    return t_class(**attributes)

def generate_synthetic_images(labels_folder, images_folder, masks_folder, output_folder, lesion_augmentations, n_gen, transform_file):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_images_folder = os.path.join(output_folder, "imagesTr")
    if not os.path.exists(output_images_folder):
        os.makedirs(output_images_folder)
    output_labels_folder = os.path.join(output_folder, "labelsTr")
    if not os.path.exists(output_labels_folder):
        os.makedirs(output_labels_folder)


    dataset = get_files_paths(labels_folder, images_folder, ".nii.gz")
    masks_dataset = get_files_paths(masks_folder, file_ending=".nii.gz")

    subjects_labels_list = load_in_torchio_subjects(dataset)

    with open(os.path.join(labels_folder, "config.json")) as f:
        try:
            config = json.load(f)
            expected_labels=list(config['labels'].values())
            labels_to_ignore_when_pasting=list(config['ignore_labels'])
        except json.decoder.JSONDecodeError as e:
            print(f"Invalid JSON syntax: {e}")
            sys.exit(1)
        
    ## TODO Check mask, labels and image size
    check_labels(subjects_labels_list, expected_labels)

    ## TODO Adding a second class when pasting the mask : only if brain MRIs with lesions are present 
    paste_mask_tr = RandomPasteMask(masks_dataset, label_key="label", augment=lesion_augmentations, ignore_labels=labels_to_ignore_when_pasting)
    augment_tr = get_transform_from_json(transform_file)   
    transforms=[paste_mask_tr, augment_tr]
    transform = tio.Compose(transforms)

    subjects_dataset = tio.SubjectsDataset(subjects_labels_list, transform=transform)

    for i in tqdm(range(0,len(subjects_dataset))):
        for n in tqdm(range(0,n_gen)):
            subject = subjects_dataset[i]
            print(f"{subject.id} image saved in {os.path.join(output_images_folder, f'{subject.id}-{n}_0000.nii.gz')}")
            print(f"{subject.id} label saved in {os.path.join(output_labels_folder,  f'{subject.id}-{n}.nii.gz')}")
            subject.label.save(path=os.path.join(output_labels_folder, f"{subject.id}-{n}.nii.gz"))
            subject.synth.save(path=os.path.join(output_images_folder, f"{subject.id}-{n}_0000.nii.gz"))
    
    config['labels']["lesion"]=len(expected_labels)
    dataset_dict={"channel_names":{"synth":0}, "labels":config["labels"],"numTraining":(i+1)*(n+1), "file_ending":"nii.gz"}
    print(dataset_dict)
    with open(os.path.join(output_folder, "dataset.json"), "w") as f:
        json.dump(dataset_dict , f, indent='\t') 

if __name__ == '__main__':
    entry_point_generate_synthetic_images()