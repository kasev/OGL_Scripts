__author__ = 'matt'

from glob import glob
import os
from time import sleep

for dir in glob('/home/fbaumgardt/ddd/*'):
	if '$' not in dir:
		os.system('iris batch --binarize sauvola:10,20,30,40 --ocr tesseract:grc+eng --willitblend -- {0}/*.png'.format(dir))
		#os.system('rm -r {0}\n'.format(dir))
		sleep(1200)
