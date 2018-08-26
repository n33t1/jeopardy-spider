#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.abspath(__file__ + "/../"))

from utils import JeopardyParser as jparser

import urllib2
from bs4 import BeautifulSoup
import time
import sys
import concurrent.futures as futures
import threading
import gevent.monkey
gevent.monkey.patch_all()

class threadDownload(threading.Thread):
	def __init__(self, que, archive_folder, func):
			threading.Thread.__init__(self)
			self.que = que
			self.archive_folder = archive_folder
			self.func = func

	def run(self):               
			length = len(self.que)
			coroutineNum = length # TODO: gevent wont be triggered if coroutineNum > length. need to be fixed. 
			for i in range(coroutineNum):
				jobs = []
				left = i * (length // coroutineNum)

				if (i + 1) * (length // coroutineNum) < length:            
						right = (i+1) * (length // coroutineNum)
				else:
						right = length
				
				print left, right, length

				for td in self.que[left:right]:
						url = td.find("a")["href"]
						game_date = td.a.contents[0].split()[2]
						jobs.append(gevent.spawn(self.func, url, game_date, self.archive_folder))
				gevent.joinall(jobs)
				
class Downloader:
	# TODO: parse clue answers
	# TODO: filter media files

	ERROR_MSG = "ERROR: No game"
	SECONDS_BETWEEN_REQUESTS = 3
	NUM_THREADS = 2 

	BASE_URL = "http://j-archive.com/"
	SEASON_URL = "http://www.j-archive.com/showseason.php?season=%s"
	BASE_PAGE = urllib2.urlopen(BASE_URL).read()
	soup = BeautifulSoup(BASE_PAGE, "html.parser")

	def __init__(self, season, output_type):
		self.season = season
		self.output_type = output_type
		self.run()

	def run(self):
		try:
				import multiprocessing 
				# Since it's a lot of IO let's double # of actual cores
				self.NUM_THREADS = multiprocessing.cpu_count() * 2
				print 'Using {} threads'.format(self.NUM_THREADS)
		except (ImportError, NotImplementedError):
				pass

		if self.season is not None:
				self.parse_specific_season()
		else:
				self.parse_season()

	def parse_specific_season(self):
		url = self.SEASON_URL % self.season

		season_str = str(self.season)

		archive_folder = 'season_%s' % season_str
		self.create_archive_dir(archive_folder)

		season_html = self.download_page(url)
		print "Now download season %s" % season_str
		self.parse_game(season_html, archive_folder)

	def parse_season(self):
		for line in self.soup.select('a[href^="showseason.php"]'):
				url = line.get('href')
				url = self.BASE_URL + url
				season = url.partition("season=")[2]

				season_str = str(season)

				archive_folder = 'season_%s' % season_str
				self.create_archive_dir(archive_folder)

				season_html = self.download_page(url)
				print "Now download season %s" % season_str
				self.parse_game(season_html, archive_folder)

	def parse_game(self, season_html, archive_folder):
		tdlist = season_html.find_all('td',{'align':'left'})
		l = len(tdlist)

		queList = []
		threadNum = 6 # threads we are using here
		for i in range(threadNum):
				que = [] #Queue.Queue()
				queDate = [] #Queue.Queue()
				left = i * (l // threadNum)
				if (i+1) * (l // threadNum) < l:            
					right = (i+1) * (l // threadNum)
				else:
					right = l

				for td in tdlist[left:right]:
					que.append(td)
				queList.append(que)

		threadList = []
		for i in range(threadNum):
				threadList.append(threadDownload(queList[i], archive_folder, self.download_and_save_page))
		for thread in threadList:
				thread.start() # starting multithreading
		for thread in threadList:
				thread.join()

	def download_and_save_page(self, url, game_date, archive_folder):
		new_file_name = "%s.html" % game_date if self.output_type == 'html' else "%s.json" % game_date
		destination_file_path = os.path.join(archive_folder, new_file_name)
		if not os.path.exists(destination_file_path):
				html = self.download_page(url)
				if self.ERROR_MSG in html:
					# Now we stop
					print "Finished downloading. Now parse."
					return False
				elif html:
					html_string = str(html)

					if self.output_type == 'html':
							self.save_file(html_string, destination_file_path)
					elif self.output_type == 'json':
							html_lxml = BeautifulSoup(html_string, 'lxml')
							self.parse_to_json(html_lxml, destination_file_path)
					else:
							raise NameError('File type not valid!')

					time.sleep(self.SECONDS_BETWEEN_REQUESTS)  
		else:
				print "Already downloaded %s" % destination_file_path
		return True

	def download_page(self, url):
		html = None
		try:
				response = urllib2.urlopen(url)
				if response.code == 200:
					print "Downloading ", url 
					# html = response.read()
					html = BeautifulSoup(response, "html.parser")
				else:
					print "Invalid URL: ", url
		except urllib2.HTTPError:
					print "failed to open ", url
		return html

	def save_file(self, html_string, filename):
		try:
				with open(filename, 'w') as f:
					f.write(html_string)
		except IOError:
				print "Couldn't write to file %s" % filename

	def parse_to_json(self, html_string, destination_file_path):
		test = jparser.Round(html_string, destination_file_path)
		test.parseGame()
				
	def create_archive_dir(self, season):
		if not os.path.isdir(season):
				os.mkdir(season)
