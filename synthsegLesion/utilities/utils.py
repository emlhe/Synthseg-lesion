import os 
import numpy as np
from typing import List, Union, Optional
import torchio as tio
import torch 

    
def get_files_paths(labels_folder, t1w_folder=None, file_ending='nii.gz'):
    if t1w_folder==None:
         identifiers = get_identifiers(labels_folder, '_mask' + file_ending)
         masks = [os.path.join(labels_folder, i + '_mask' + file_ending) for i in identifiers]
         dataset = {i: {'mask': m} for i, m in zip(identifiers, masks)}
    else:
        identifiers = get_identifiers(t1w_folder, '_T1w' + file_ending)
        images = [os.path.join(t1w_folder, i + '_T1w' + file_ending) for i in identifiers]
        labels = [os.path.join(labels_folder, i + '_labels' + file_ending) for i in identifiers]
        dataset = {i: {'image': im, 'labels': lab} for i, im, lab in zip(identifiers, images, labels)}

    return dataset

def get_identifiers(folder: str, file_ending: str):
    files = subfiles(folder, suffix=file_ending, join=False)
    crop = len(file_ending)
    files = [i[:-crop] for i in files]
    # only unique image ids
    files = np.unique(files)
    return files

## from batchgenerators package (DKFZ)
def subfiles(folder: str, join: bool = True, prefix: Optional[str] = None, suffix: Optional[str] = None, sort: bool = True) -> List[str]:
    """
    Returns a list of files in a given folder, optionally filtering by prefix and suffix,
    and optionally sorting the results. Uses os.scandir for efficient directory traversal,
    making it suitable for network drives.

    Parameters:
    - folder: Path to the folder to list files from.
    - join: Whether to return full file paths (if True) or just file names (if False).
    - prefix: Only include files that start with this prefix (if provided).
    - suffix: Only include files that end with this suffix (if provided).
    - sort: Whether to sort the list of files alphabetically.

    Returns:
    - List of file paths (or names) meeting the specified criteria.
    """
    files = []
    with os.scandir(folder) as entries:
        for entry in entries:
            if entry.is_file() and \
               (prefix is None or entry.name.startswith(prefix)) and \
               (suffix is None or entry.name.endswith(suffix)):
                file_path = entry.path if join else entry.name
                files.append(file_path)

    if sort:
        files.sort()

    return files

def load_in_torchio_subjects(dataset):
    subjects = []

    for identifier in dataset.keys():
        subject = tio.Subject(
            image=tio.ScalarImage(dataset[identifier]['image']),
            label=tio.LabelMap(dataset[identifier]['labels']),
            id=identifier
        )
        subjects.append(subject)

    return subjects


def check_labels(dataset, expected_labels):
    """
    Checks if every subject in the dataset has exactly the same consecutive label values.
    Returns True if so, False otherwise.
    """
    for subject in dataset:
        # Locate LabelMap
        unique_labels = np.sort(np.unique(subject.label.data.numpy()))

        unexpected_labels = [i for i in unique_labels if i not in expected_labels]

        if len(unique_labels) == 0 and unique_labels[0] == 0:
            print(f'WARNING: File {subject.id} only has label 0 (which should be background)')
        if len(unexpected_labels) > 0:
            print(f"Error: Unexpected labels found in file {subject.id} .\nExpected: {expected_labels} \nFound: {unique_labels}")
        return False
            
    return True