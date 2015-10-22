__author__ = 'matt'

from lxml import etree
from lxml.builder import ElementMaker
from collections import defaultdict
from glob import glob
from os.path import isdir, basename, splitext
import os

class CTS_refs:

	def __init__(self, orig_dir, tsv_file, author_col, uri_col, title_col, urn_col, levels_col, root_tag):
		with open(tsv_file) as f:
			lines = f.read().split('\n')
		self.refsD = defaultdict(dict)
		#assumes a header line. Delete [1:] if no header line exists.
		for line in lines[1:]:
			self.refsD[line.split('\t')[uri_col]]['levels'] = line.split('\t')[levels_col].split(', ')
			self.refsD[line.split('\t')[uri_col]]['urn'] = line.split('\t')[urn_col]
			self.refsD[line.split('\t')[uri_col]]['title'] = line.split('\t')[title_col]
			self.refsD[line.split('\t')[uri_col]]['author'] = line.split('\t')[author_col]
		self.root_tag = root_tag
		self.orig_dir = orig_dir

	def add_refsDecl(self):
		for uri in self.refsD:
			RD = etree.Element('refsDecl')
			RD.set('n', 'CTS')
			for i, level in enumerate(self.refsD[uri]['levels']):
				if i == 0:
					mp = '(.+)'
					if level.lower() == 'line':
						rp = "#xpath(/tei:{0}/tei:text/tei:body/tei:div[@type='edition']/tei:l[@n='$1'])".format(self.root_tag, level.lower())
					else:
						rp = "#xpath(/tei:{0}/tei:text/tei:body/tei:div[@type='edition']/tei:div[@n='$1' and @subtype='{1}'])".format(self.root_tag, level.lower())
				c = etree.Element('cRefPattern')
				c.set('n', level.lower())
				c.set('matchPattern', mp)
				c.set('replacementPattern', rp)
				RD.insert(0, c)
				mp += '.(.+)'
				# I need to insert the lower levels of reference at position 0.
				try:
					if self.refsD[uri]['levels'][i+1].lower() == 'line':
						rp = rp.replace(')', "//tei:l[@n='${1}'])".format(self.refsD[uri]['levels'][i+1].lower(), i+2))
					else:
						rp = rp.replace(')', "//tei:div[@n='${1}' and @subtype='{0}'])".format(self.refsD[uri]['levels'][i+1].lower(), i+2))
				except IndexError:
					continue
			self.refsD[uri]['refsDecl'] = RD

	def create_dir_structure(self):
		data_dir = '{}/data'.format(self.orig_dir)
		os.makedirs(data_dir)
		for uri in self.refsD.keys():
			try:
				author, work = uri.split('.')
			except ValueError:
				continue
			try:
				os.makedirs('{0}/{1}/{2}'.format(data_dir, author, work))
			except:
				print(uri)
				continue

	def make_files(self):
		dirs = glob('{}/*'.format(self.orig_dir))
		self.not_changed = []
		for d in dirs:
			if isdir(d) and basename(d) != 'data':
				files = glob('{}/*.xml'.format(d))
				for file in files:
					uri = splitext(basename(file))[0].replace('-', '.')
					with open(file) as f:
						root = etree.parse(f).getroot()
					try:
						root.xpath('//tei:encodingDesc', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0].append(self.refsD[uri]['refsDecl'])
					except KeyError:
						self.not_changed.append('{}, bad URI'.format(file))
						continue
					except IndexError:
						self.not_changed.append('{}, no encodingDesc'.format(file))
						continue
					try:
						root.xpath('//tei:div[@type="edition"]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0].set('n', self.refsD[uri]['urn'])
					except IndexError:
						self.not_changed.append('{}, URN not changed'.format(file))
					try:
						c = root.xpath('//tei:div[@type="textpart" and @subtype="work"]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0].getchildren()
						p = root.xpath('//tei:div[@type="textpart" and @subtype="work"]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0].getparent()
						p.remove(root.xpath('//tei:div[@type="textpart" and @subtype="work"]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0])
						for x in c:
							p.append(x)
					except IndexError:
						self.not_changed.append('{}, no <div subtype="work" to remove'.format(file))
					try:
						c = root[0].getchildren()
						root.replace(root[0], etree.Element('teiHeader'))
						for x in c:
							root[0].append(x)
					except IndexError:
						self.not_changed.append('{}, no teiHeader'.format(file))
					xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n<?xml-model href="http://www.stoa.org/epidoc/schema/latest/tei-epidoc.rng" schematypens="http://relaxng.org/ns/structure/1.0"?>\n'
					for retract in root.xpath("//tei:div[@subtype='retractationes']", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
						retract.set('n', 'retractationes')
						retract.set('subtype', 'section')
					author, work = uri.split('.')
					new_d = '{0}/data/{1}/{2}'.format(self.orig_dir, author, work)
					new_file = '{0}/{1}.xml'.format(new_d, self.refsD[uri]['urn'].split(':')[-1])
					text = etree.tostring(root,
										  encoding='unicode',
										  pretty_print=True)
					text = text.replace('<refsDecl n="CTS">', '  <refsDecl n="CTS">')
					text = text.replace('><cRefPattern', '>\n        <cRefPattern')
					text = text.replace('></refsDecl>', '>\n      </refsDecl>\n    ')
					text = text.replace('<teiHeader>', '<teiHeader>\n    ')
					text = text.replace('  </teiHeader>', '</teiHeader>\n')
					text = xml_header + text
					#text = text.replace('></teiHeader>', '>\n</teiHeader>')
					with open(new_file, mode='w') as f:
						f.write(text)
					self.write_cts_files(root, uri, author, work)

	def write_cts_files(self, root, uri, author, work):
		E = ElementMaker(namespace='http://chs.harvard.edu/xmlns/cts',
						 nsmap={'ti': 'http://chs.harvard.edu/xmlns/cts',
								'xml': 'http://www.w3.org/XML/1998/namespace'})
		author_cts = E.textgroup(E.groupname(
			self.refsD[uri]['author'],
			{"{http://www.w3.org/XML/1998/namespace}lang": 'eng'}),
		urn='{}'.format(self.refsD[uri]['urn'].split('.')[0]))
		#author_cts = etree.Element('ti:textgroup')
		#author_cts.set('xmlns:ti', "http://chs.harvard.edu/xmlns/cts")
		#author_cts.set('urn', '{}'.format(self.refsD[uri]['urn'].split('.')[0]))
		#g_name = etree.Element('ti:groupname')
		#g_name.set('xml:lang', 'eng')
		#g_name.text = root.xpath('//tei:sourceDesc//tei:author', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0].text
		#author_cts.append(g_name)
		with open('{0}/data/{1}/__cts__.xml'.format(self.orig_dir, author), mode='w') as f:
			f.write(etree.tostring(author_cts, encoding='unicode', pretty_print=True))
		text = self.refsD[uri]['title']
		work_cts = E.work(
			E.title(text, {"{http://www.w3.org/XML/1998/namespace}lang": 'eng'}),
			E.edition(
				E.label(text, {"{http://www.w3.org/XML/1998/namespace}lang": 'eng'}),
				E.description('{}, {}'.format(self.refsD[uri]['author'], text),
							  {"{http://www.w3.org/XML/1998/namespace}lang": 'eng'}),
				{'workUrn': '.'.join(self.refsD[uri]['urn'].split('.')[:-1]),
				 'urn': self.refsD[uri]['urn']}),
			{'groupUrn': self.refsD[uri]['urn'].split('.')[0],
			 'urn': '.'.join(self.refsD[uri]['urn'].split('.')[:-1])})
		'''work_cts = etree.Element('ti:work')
		work_cts.set('xmlns:ti', "http://chs.harvard.edu/xmlns/cts")
		work_cts.set('groupUrn', self.refsD[uri]['urn'].split('.')[0])
		work_cts.set('urn', '.'.join(self.refsD[uri]['urn'].split('.')[:1]))
		title = etree.Element('ti:title')
		title.set('xml:lang', 'eng')
		work_cts.append(title)
		edition = etree.Element('ti:edition')
				'''
		with open('{0}/data/{1}/{2}/__cts__.xml'.format(self.orig_dir, author, work), mode='w') as f:
			f.write(etree.tostring(work_cts, encoding='unicode', pretty_print=True))