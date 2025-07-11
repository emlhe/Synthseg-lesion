import torchio

## Torchio augmentation for pasting lesions

import random
import nibabel as nib
import numpy as np
import torch
import torchio as tio
import torch.nn.functional as F
from scipy import ndimage


class RandomPasteMask(tio.transforms.Transform):
    def __init__(self, mask_dataset, label_key="segmentation", augment=False, ignore_labels=None, p=1.0):
        super().__init__(p=p)
        self.mask_dataset = mask_dataset
        self.label_key = label_key
        self.augment=augment
        self.ignore_labels = ignore_labels

    def apply_transform(self, subject: tio.Subject):
        mask_path = random.choice(list(self.mask_dataset.values()))['mask']
        mask_img = nib.load(mask_path).get_fdata().astype(bool)
        if self.augment:
            mask_img = self.random_morph(mask_img, max_kernel_size=10, p_erode=0.4, p_dilate=0.4)

        seg = subject[self.label_key].data.numpy()
        
        # if mask.shape != seg.shape:
        #     h1, w1, d1 = mask.shape
        #     _,h2, w2, d2 = seg.shape
        #     dh = h2 - h1
        #     dw = w2 - w1
        #     dd = d2 - d1
        #     pad = (0, dd, 0, dw, 0, dh)
        #     mask = F.pad(mask, pad=pad, mode='constant', value=0)          

        seg = self.paste(mask_img, seg, ignore_labels=self.ignore_labels)
        seg = torch.from_numpy(seg)

        subject[self.label_key] = tio.LabelMap(tensor=seg)
        return subject

    def random_morph(self, mask, max_kernel_size=3, p_erode=0.33, p_dilate=0.33):
        """
        Randomly performs erosion, dilation, or nothing on a binary mask.

        Args:
            mask (np.ndarray): Input binary mask.
            max_kernel_size (int): max size of the structuring element.
            p_erode (float): Probability to apply erosion.
            p_dilate (float): Probability to apply dilation.

        Returns:
            np.ndarray: Transformed mask.
        """
        struct = np.ones((random.randint(1, max_kernel_size),random.randint(1, max_kernel_size),random.randint(1, max_kernel_size)), dtype=bool) if max_kernel_size is not None else np.ones((3,3,3))
        r = random.random()

        if r < p_erode:
            print("erode")
            return ndimage.binary_erosion(mask, structure=struct)
        elif r < p_erode + p_dilate:
            print("dilate")
            return ndimage.binary_dilation(mask, structure=struct)
        else:
            return mask.copy()
        

    def paste(self, mask, labels, ignore_labels=None):
        """
        Pastes a binary mask into a label array, except where labels are in ignore_labels.

        Args:
            labels (np.ndarray): integer ndarray of labels.
            mask (np.ndarray): boolean or 0/1 ndarray, same shape as labels.
            ignore_labels (list or set): labels to be left unchanged under the mask.
            
        Returns:
            np.ndarray: a new array with the mask applied.
        """
        # Create a boolean condition: apply mask only if current label not in ignore
        cond = mask & (~np.isin(labels, ignore_labels))
        new_lbl = int(labels.max()) + 1
        np.putmask(labels, cond, new_lbl)

        return labels