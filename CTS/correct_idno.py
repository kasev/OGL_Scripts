__author__ = 'matt'

from glob import glob
from lxml import etree
import os

class correct_idno:

	def __init__(self, orig):
		self.orig = orig

	def build_file_list(self):
		dirs1 = []
		[dirs1.append(x) for x in glob('{}/*'.format(self.orig)) if os.path.isdir(x) and '@' not in x]
		dirs2 = []
		for d in dirs1:
			[dirs2.append(x) for x in glob('{}/*'.format(d)) if os.path.isdir(x) and '@' not in x]
		self.files = []
		for d in dirs2:
			[self.files.append(x) for x in glob('{}/*'.format(d)) if os.path.isfile(x) and '_' not in x]

	def change_idno(self):
		for file in self.files:
			root = etree.parse(file).getroot()
			root.xpath('//tei:idno[@type="filename"]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0].text = os.path.basename(file)
			with open(file, mode='w') as f:
				f.write(etree.tostring(root, encoding='unicode', pretty_print=True))