__author__ = 'matt'

import os
from glob import glob
import re

home_dir = "OCR/"
dirs = glob(home_dir + "*")
for dir in dirs:
	if os.path.isdir(dir):
		files = os.listdir(dir)
		for file in files:
			if file.endswith('blend_hocr.hocr'):
				dest_dir = '/home/mmunson/ddd/' + re.search(r'(.*?)\.pdf', file).group(1)
				if os.path.isdir(dest_dir) == False:
					os.mkdir(dest_dir)
				os.system('mv {0}/{1} [2}'.format(dir, file, dest_dir))
