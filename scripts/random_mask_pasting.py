import torchio

## Torchio augmentation for pasting lesions

import random
import nibabel as nib
import numpy as np
import torch
import torchio as tio
import torch.nn.functional as F


class RandomPasteMask:
    def __init__(self, mask_paths, label_key="segmentation", p_per_sample=1.0):
        self.mask_paths = mask_paths
        self.label_key = label_key
        self.p_per_sample = p_per_sample

    def __call__(self, **data_dict):
        if random.random() > self.p_per_sample:
            return data_dict

        mask_path = random.choice(self.mask_paths)
        mask_img = nib.load(mask_path)
        mask = torch.from_numpy(mask_img.get_fdata().astype(bool)).unsqueeze(axis=0)
        seg = data_dict[self.label_key]
        
        if mask.shape != seg.shape:
            _,h1, w1, d1 = mask.shape
            _, h2, w2, d2 = seg.shape

            dh = h2 - h1
            dw = w2 - w1
            dd = d2 - d1
            pad = (0, dd, 0, dw, 0, dh)
            mask = F.pad(mask, pad=pad, mode='constant', value=0)
            

        new_lbl = int(seg.max()) + 1
        # paste mask
        seg[mask] = new_lbl

        data_dict[self.label_key] = seg
        return data_dict
