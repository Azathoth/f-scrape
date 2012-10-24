#!/usr/bin/python

import os
import time
import argparse
import urllib
import re

def main():
	args = initArgs()

	if (not checkFlags(args)):
		print('Error: no flags supplied')
		exit(1)

	while (True):

		if (args.V):
			t = time.localtime()

			print('[' + str(t[0]) + '-' + str(t[1]) + '-' + str(t[2]) + ' ' + str(t[3]) + ':' + str(t[4]) + '] ' + 'Scraping...')

		index = fetchIndex()

		urls = parseURLs(args, index)

		getSWFs(args, urls)

		if (args.V): print('Scrape complete')

		time.sleep(args.T)

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
	flags.add_argument('-A', dest='A', action='store_true',
											help='scrape [A]')
	flags.add_argument('-Q', dest='Q', action='store_true',
											help='scrape [?]')
	parser.add_argument('-t', dest='T', action='store',
											type=int, default=300, metavar='SECONDS',
											help='sets refresh rate in seconds')
	parser.add_argument('-v', dest='V', action='store_true',
											help='enable verbose output')
	parser.add_argument('-o', dest='O', action='store_true',
											help='organize downloads based on type (creates subdirectories)')
	parser.add_argument(action='store', dest='PATH', metavar='PATH')

	return parser.parse_args()

def checkFlags(ns):
	if (not (ns.H or  ns.L or ns.G or ns.P or ns.Q or ns.J or ns.A)):
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
	flags = dict({'H': ns.H, 'L': ns.L, 'G': ns.G, 'P': ns.P, 'J': ns.J, 'A': ns.A, '?': ns.Q});
	urls = []

	for k, v in flags.items():
		if (v):
			if (verbose): print(k)
			if (k == '?'):
				k = '\?'
			exp = re.compile(r'<td>\[<a[^>]*?>[^/]*?<\/a>\]<\/td><td>\[' + k + '\]<\/td>')
			matched = exp.finditer(index)
			for line in matched:
				exp = re.compile(r'href=\"(.*?\.swf)\"')
				swf = exp.search(line.group())
				if (verbose): print('http:'+swf.group(1))
				urls.append((k, 'http:'+swf.group(1)))

	print('')

	return urls

def getSWFs(ns, urls):
	verbose = ns.V
	organize = ns.O

	for t, u in urls:
		
		path = ns.PATH

		if (path[len(path)-1] != '/'):
			path += '/'

		exp = re.compile(r'[^/]*?\.swf')
		fname = exp.search(u).group()

		if (len(fname) > 251):
			fname = fname[:251]

		if (organize):
			if (not os.path.isdir(path + t)):
				os.makedirs(path + t, 0755)
				if (verbose): print('creating dir \"' + path + '\"')

			path = path + t + '/'

		if (not os.path.isfile(path + fname)):
			if (verbose): print('GET ' + u)		

			req = urllib.urlopen(u)
			swf = ''

			for line in req:
				swf += line

			try:
				if (verbose): print('writing file \"' + path + fname + '\"')
				fh = open(path + fname, 'w')
				fh.write(swf)
				fh.close()
			except Exception:
				pass

if __name__ == '__main__':
	main()
