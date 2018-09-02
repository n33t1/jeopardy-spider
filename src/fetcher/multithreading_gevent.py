#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.abspath(__file__ + "/../../"))

# from utils import RoundParser
import logging
import urllib2
from bs4 import BeautifulSoup as soup
import md5
import time
import sys
import concurrent.futures as futures
import threading
import gevent.monkey
gevent.monkey.patch_all()

import logging
logger = logging.getLogger(__name__)

# TODO: we should really use multothreading in src.run() instead of here
# the downloader should run the html object and pass it into parser in src.run()
# we should try to seperate downloader and parser as much as we can


class threadDownload(threading.Thread):
    def __init__(self, que, archive_folder, func):
        threading.Thread.__init__(self)
        self.que = que
        self.archive_folder = archive_folder
        self.func = func

    def run(self):
        length = len(self.que)
        # TODO: gevent wont be triggered if coroutineNum > length. need to be fixed.
        coroutineNum = length
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
                jobs.append(gevent.spawn(self.func, url,
                                         game_date, self.archive_folder))
            gevent.joinall(jobs)


class Fetcher:
	# TODO: parse clue answers
	# TODO: filter media files

	ERROR_MSG = "ERROR: No game"
	SECONDS_BETWEEN_REQUESTS = 3
	NUM_THREADS = 2

	BASE_URL = "http://j-archive.com/"
	SEASON_LIST = "http://www.j-archive.com/listseasons.php"
	SEASON_URL = "http://www.j-archive.com/showseason.php?season=%s"
	GAME_URL = "http://www.j-archive.com/showgame.php?game_id=%s"
	# BASE_PAGE = urllib2.urlopen(BASE_URL).read()
	# soup = soup(BASE_PAGE, "html.parser")

	def __init__(self, api=None):
		self.api = api
	
	def get_latest_season(self):
		logger.debug("Fetching latest season ...")
		season_list_html = self._download_page(self.SEASON_LIST)
		td = season_list_html.find_all('td')[0]
		url = td.find("a")["href"]
		lastest_season = td.a.contents[0].split()[1]
		return url, lastest_season

	def get_MD5(self, url):
		try:
			html = urllib2.urlopen(url).read()
			return md5.new(html).hexdigest()
		except Exception as e:
			logger.error('Error getting MD5 for %s ! Error: %s', url, e)
			raise

	def _get_all_games_for_season(self, season):
		def _parser_season(season_html):
			td = season_html.find_all('td', {'align': 'left'})[0]
			url = td.find("a")["href"]
			game_date = td.a.contents[0].split()[2]
			return url, game_date

		logger.debug("Parsing game list for season %s", season)
		season_url = self.SEASON_URL % str(season)
		season_html = self._download_page(season_url)
		return _parser_season(season_html)

	def _download_page(self, url, parse=True):
		try:
			if parse:
				logger.debug("Downloading %s", url)
				html = soup(urllib2.urlopen(url), 'lxml')
			else:
				logger.debug("Downloading %s as html string", url)
				html = urllib2.urlopen(url).decode('utf-8').encode('ascii', 'ignore')
			
			return html
		except (Exception, urllib2.HTTPError) as e:
			logger.error("failed to open %s", url)
			raise e

	def fetch_lastest_game_from_season(self, season, output_type="firebase", season_options=None):
		"""Download lastest game for the given season with output_type of either html, json or uploading
		to your firebase database (default option).

		Args:
			season(int): Season you want to download.
			output_type(str): Output type, being html, json or uploading to firebase.
			*season_options(int): range for season from 1 to season_options inclusively. 

		Returns:
			Beautiful soup object for html page for target game.

		"""
		try:
			if season_options and season not in season_options:
				raise Exception('Season does not exist!')
			
			game_url, game_date = self._get_all_games_for_season(season)
			logger.debug("url: %s, game_date: %s fetched successfully.", game_url, game_date)
			return self._download_page(game_url), game_date
		except Exception as e:
			logger.error(e)
			raise
	
	def download_specific_game(self, game_id, game_options, output_type="firebase"):
		"""Download specific game for the given game_date and season with output_type of either html, json or uploading
		to your firebase database.

		Args:
			game_id(str): Game id for the jeopady game you want.
			game_options(dict): a dict of {game_id: game_date} for exisiting games for current season. 
			output_type(str): Output type, being html, json or uploading to firebase.

		Returns:
			Beautiful soup object for html page for target game.

		"""
		try:
			if game_id not in game_options.keys():
				raise Exception('Game does not exist!')
			
			game_date = game_options[game_id]
			game_url = self.GAME_URL % game_id
			logger.debug("url: %s, game_date: %s fetched successfully.", game_url, game_date)
			return self._download_page(game_url)
		except Exception as e:
			logger.error(e)
			raise


	# def parse_specific_season(self):
	# 	url = self.SEASON_URL % self.season

	# 	season_str = str(self.season)

	# 	archive_folder = 'season_%s' % season_str
	# 	self.create_archive_dir(archive_folder)

	# 	season_html = self.download_page(url)
	# 	print "Now download season %s" % season_str
	# 	self.parse_game(season_html, archive_folder)	

	# def download_season(self, season, output_type="firebase"):
	# 	"""download the entire season with output_type of either html, json or uploading
	# 	to your firebase database (default option).

	# 	Args:
	# 		season(int): Season you want to download.
	# 		output_type(str): What format you want the output to be.

	# 	Returns:
	# 		The return value. True for success, False otherwise.

	# 	"""
	# 	pass

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
		tdlist = season_html.find_all('td', {'align': 'left'})
		l = len(tdlist)

		queList = []
		threadNum = 6  # threads we are using here
		for i in range(threadNum):
			que = []  # Queue.Queue()
			queDate = []  # Queue.Queue()
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
			threadList.append(threadDownload(
				queList[i], archive_folder, self.download_and_save_page))
		for thread in threadList:
			thread.start()  # starting multithreading
		for thread in threadList:
			thread.join()

	def download_and_save_page(self, url, game_date=None, archive_folder=None):
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
				elif self.output_type == 'firebase':
					html_lxml = BeautifulSoup(html_string, 'lxml')
					self.upload_to_firebase(html_lxml, game_date)
				else:
					raise NameError('File type not valid!')

				time.sleep(self.SECONDS_BETWEEN_REQUESTS)
		else:
			print "Already downloaded %s" % destination_file_path
		return True

	def save_file(self, html_string, filename):
		try:
			with open(filename, 'w') as f:
				f.write(html_string)
		except IOError:
			print "Couldn't write to file %s" % filename

	def parse_to_json(self, html_string, destination_file_path):
		test = Round(html_string, destination_file_path=destination_file_path)
		test.parseGame()
		test.toJSON()

	def upload_to_firebase(self, html_string, game_date):
		print "upload_to_firebase called!"
		test = Round(html_string, game_date=game_date)
		test.parseGame()
		test.uploadToFirebase(self.api)

	def create_archive_dir(self, season):
		if not os.path.isdir(season):
			os.mkdir(season)
