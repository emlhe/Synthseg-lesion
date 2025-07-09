import torchio 

## Get (prenormalized) data
## -> Masks + labels 
## Check if all labels have same number of labels, consecutive labels, same size and mask same size
## Use RandomLesionAug if parameter 
### Adding a second class ? only if brain MRIs with stroke are present 
## Use RandomLesionPasting 
### Avoid certain classes ? 
## Use RandomLesionToImage x times for each image 

## In config file : 
## config for augmentations ? 
## config for data format

## -> command line and get the parameters in this file and run the synthseg lesion process
## Parameters : -n, -in_labels -in_masks -in_MRI -lesaug

