__author__ = 'matt'

import os
from glob import glob
from time import sleep
import re

os.system('screen -S supervisord -X stuff "supervisord -c supervisord_iris.conf"')
dirs = sorted(glob('/home/mmunson/ddd100/*'))

dest_dirs = glob('/home/mmunson/ddd/*')
done = []
for dir in dest_dirs:
    for file in glob(dir + '/*.hocr'):
		done.append(re.split('_rgb_', os.path.basename(file))[0] + '.png')
for dir in dirs:
	if os.path.isdir(dir):
		for file in glob(dir + '/*'):
			if os.path.basename(file) not in done:
				os.system('screen -S iris -X stuff "iris batch --binarize sauvola:10,20,30,40 --ocr tesseract:grc+eng --willitblend -- {0}\n"'.format(file))
				sleep(3)
		os.system('screen -S iris -X stuff "mv {0}* /home/mmunson/ddd100_done\n"'.format(dir))
		os.system('screen -S iris -X stuff "date\n"')
		sleep(1900)
		os.system('supervisorctl -c supervisord_iris.conf restart celery\n')
		#sleep(10)
		#os.system('screen -S celery -d -m\n')
		#os.system('screen -S celery -X stuff ". envs/Ben_Iris/bin/activate.fish\n"')
		#os.system('screen -S celery -X stuff "celery -A iris.tasks worker\n"')
