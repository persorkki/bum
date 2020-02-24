#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
	Bum.py A neat little script that downloads album cover art from Apple itunes servers
	The Bum's lost!
	Usage:
		>bum.py -s "search term"
	or
		>bum.py 
		and the program will ask you for a search term. quotes not needed
"""

import os
import sys

import requests
import string
import argparse
from progress.bar import Bar
from multiprocessing import Pool
import multiprocessing

def run(val):
	"""
	Main, runs the multiprocessing pool and handles the search
	"""
	queryString = val.replace(" ", "%20")
	res = requests.get(url=f"https://itunes.apple.com/search?term={queryString}&entity=album")

	if res.ok:
		r = res.json()
		with Bar('Downloading files', max=len(r['results'])) as bar:
			p = Pool(20)
			for __ in p.imap(download, r['results']):
				bar.next()
	else:
		exit(1)

def fix_filename(name):
	"""
	Returns a valid filename as string by using a whitelist approach
	name: str
	"""
	
	valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
	return ''.join(c for c in name if c in valid_chars)

def download(source):
	"""
	Downloads a file
	source: str
	"""
	
	suffix = '.png'
	folder = os.path.join("downloads", fix_filename(source['artistName']))
	os.makedirs(folder, exist_ok=True)
	dest = os.path.join(folder, fix_filename(source['collectionName'] + "_" + str(source['collectionId']) + "_" + suffix ))
	if os.path.exists(dest):
		print ("File already exists, skipping - ", dest)
		return
	else:
		#request the biggest artwork they have, in .png, instead of the default
		r = requests.get(source['artworkUrl100'].replace('100x100bb.jpg', "10000x10000bb.png"))
		if r.ok:
			with open(dest, 'wb') as f:
				f.write(r.content)

if __name__ == "__main__":
	#for PyInstaller
	multiprocessing.freeze_support()

	#argparse is not very useful here, could probably just use sys.argv to save lines
	parser = argparse.ArgumentParser(description='simple commandline options')
	parser.add_argument('-s',dest='search',help="Name to search for (album, artist)")
	args = parser.parse_args()
	
	if args.search == None:
		sterm = input('Give a search term (Ctrl+C to cancel):')
		run(sterm)
	else:
		run(args.search)
	
