__author__ = 'matt'

from glob import glob
import os

class check_coverage:

	def __init__(self, orig, dest, min_percent):
		'''

		:param orig: location of the parent directory for the OCR results
		:param dest: directory to which acceptable results will be moved
		:param min_percent: minimum level of success for a directory to be move (as decimal)
		:return:
		'''
		self.orig = orig
		self.dest = dest
		self.min_percent = float(min_percent)

	def extract_results(self):
		'''
		Checks each subdirectory of self.orig to find the status output from nidaba
		Extracts the percentage of completed tasks
		:return:
		'''
		dirs = glob('{}/*'.format(self.orig))
		self.results = {}
		for d in dirs:
			out_file = glob('{}/????????-*.out'.format(d))
			try:
				with open(out_file[0]) as f:
					try:
						l = f.read().split('\n')[2].split()
					except IndexError:
						self.results[d] = [0, 'No Results']
				self.results[d] = (float(l[0].split('/')[0])/float(l[0].split('/')[1]), l)
			except IndexError:
				print('No .out file in {}'.format(d))

	def move_dirs(self):
		'''
		Moves the OCR results directories that meet self.min_percent to self.dest
		:return:
		'''
		for x in self.results.items():
			if x[1][0] >= self.min_percent:
				os.rename(x[0], '{0}/{1}'.format(self.dest, os.path.basename(x[0])))