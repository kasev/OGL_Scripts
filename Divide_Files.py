__author__ = 'matt'

import os
import shutil
from glob import glob

def Move():
	home_dir = '/home/fbaumgardt/ddd'
	dest_dir = '/home/mmunson/ddd100/'
	dirs = os.listdir(home_dir)
	print('dirs: {0}'.format(len(dirs)))
	for dir in dirs:
		print('Now working on {0}'.format(dir))
		if '$' not in dir:
			book = dir
			files = glob(home_dir + book + '/*.png')
			old_start = 0
			for n in range(100, len(files)+100, 100):
				dest = '{0}{1}_{2}-{3}'.format(dest_dir, book, old_start, n)
				os.mkdir(dest)
				if n > len(files):
					n = len(files)
				for file in files[old_start:n]:
					shutil.copy(file, dest)
				old_start = n