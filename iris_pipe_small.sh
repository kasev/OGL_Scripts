#!/bin/bash
#SBATCH --mem=128000
#SBATCH -n 32
# module load python/2.7.6
# module load gcc/4.9.2
# module load leptonica
# module load tesseract
 
source envs/iris/bin/activate
supervisord -c supervisord_iris.conf
# iris batch --binarize sauvola:10,20,30,40 --ocr tesseract:grc+eng -- Data/book/*.png
sleep 252000
