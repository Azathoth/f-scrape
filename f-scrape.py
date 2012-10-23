#!/usr/bin/python

import os
import argparse
import urllib
import re

def main():
	args = initArgs()

	if (not checkFlags(args)):
		print('Error: no flags supplied')
		exit(1)

	index = fetchIndex()

	urls = parseURLs(args, index)

	getSWFs(args, urls)

def initArgs():
	parser = argparse.ArgumentParser(description='scrape files from /f/')

	flags = parser.add_argument_group('flags')
	flags.add_argument('-H', dest='H', action='store_true',
											help='scrape [H]')
	flags.add_argument('-L', dest='L', action='store_true',
											help='scrape [L]')
	flags.add_argument('-G', dest='G', action='store_true',
											help='scrape [G]')
	flags.add_argument('-P', dest='P', action='store_true',
											help='scrape [P]')
	flags.add_argument('-J', dest='J', action='store_true',
											help='scrape [J]')
	flags.add_argument('-Q', dest='Q', action='store_true',
											help='scrape [?]')
	parser.add_argument('-v', dest='V', action='store_true',
											help='enable verbose output')
	parser.add_argument('-o', dest='O', action='store_true',
											help='organize downloads based on type (creates subdirectories)')
	parser.add_argument(action='store', dest='PATH', metavar='PATH')

	return parser.parse_args()

def checkFlags(ns):
	if (not (ns.H or  ns.L or ns.G or ns.P or ns.Q or ns.J)):
		return False
	else:
		return True

def fetchIndex():
	req = urllib.urlopen('http://boards.4chan.org/f/')

	content = ''

	for line in req:
		content += line

	return content

def parseURLs(ns, index):
	verbose = ns.V
	flags = dict({'H': ns.H, 'L': ns.L, 'G': ns.G, 'P': ns.P, 'J': ns.J, '?': ns.Q});
	urls = []

	for k, v in flags.items():
		if (v):
			if (verbose): print(k)
			exp = re.compile(r'<tr><td>\d+<\/td><td class=\"\"><span class=\"name\">.*?\[' + k + '\].*?<\/tr>')
			matched = exp.finditer(index)
			for line in matched:
				exp = re.compile(r'href=\"(.*?\.swf)\"')
				swf = exp.search(line.group()+'\n')
				if (verbose): print('http:'+swf.group(1))
				urls.append((k, 'http:'+swf.group(1)))
			if (verbose): print('\n')

	return urls

def getSWFs(ns, urls):
	verbose = ns.V

	for t, u in urls:
		if (verbose): print('GET ' + u)

		req = urllib.urlopen(u)
		swf = ''

		for line in req:
			swf += line

		exp = re.compile(r'[^/]*?\.swf')
		fname = exp.search(u).group()

		storeFile(ns, t, fname, swf)

def storeFile(ns, cat, fname, swf):
	verbose = ns.V
	organize = ns.O
	path = ns.PATH

	if (path[len(path)-1] != '/'):
		path += '/'

	if (organize and not os.path.isdir(path + cat)):
		os.makedirs(path + cat, 0755)
		if (verbose): print('creating dir \"' + path + cat + '\"')

	if (not os.path.isfile(path + cat + '/' + fname)):
		if (verbose): print('writing file \"' + path + cat + '/' + fname + '\"')
		fh = open(path + cat + '/' + fname, 'w')
		fh.write(swf)
		fh.close()

if __name__ == '__main__':
	main()
