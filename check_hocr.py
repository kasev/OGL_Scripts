__author__ = 'matt'

import os
import re

def check(orig):
	orig_files = os.listdir('/home/fbaumgardt/ddd/{0}'.format(orig))
	dest_files = os.listdir('/home/mmunson/ddd/{0}'.format(orig))
	orig_pages = [int(re.match(r'.*?.pdf-([0-9]{1,5})-.*', file).group(1)) for file in orig_files if file.endswith('.png')]
	dest_pages = [int(re.match(r'.*?.pdf-([0-9]{1,5})-.*', file).group(1)) for file in dest_files if file.endswith('.hocr')]
	for page in sorted(orig_pages):
		if page not in dest_pages:
			print(page)
	print('{0} pages missing from {1}'.format(len(orig_pages)-len(dest_pages), orig))