#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup as soup
import md5
import time
import sys

import logging
logger = logging.getLogger(__name__)


class Fetcher:
	# TODO: parse clue answers
	ERROR_MSG = "ERROR: No game"
	SECONDS_BETWEEN_REQUESTS = 3
	NUM_THREADS = 2

	BASE_URL = "http://j-archive.com/"
	SEASON_LIST = "http://www.j-archive.com/listseasons.php"
	SEASON_URL = "http://www.j-archive.com/showseason.php?season=%s"
	GAME_URL = "http://www.j-archive.com/showgame.php?game_id=%s"

	def __init__(self, api=None):
		self.api = api

	def fetch_game_list_for_season(self, season):
		season_html = self._get_game_list(season)
		game_list = self._parse_all_games_for_season(season_html)
		return game_list

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

	def _get_game_list(self, season):
		logger.debug("Fetching game list for season %s", season)
		return self._download_page(self.SEASON_URL % str(season))

	def _parse_latest_game(self, season_html):
		td = season_html.find_all('td', {'align': 'left'})[0]
		url = td.find("a")["href"]
		game_date = str(td.a.contents[0].split()[2])
		return url, game_date

	def _parse_all_games_for_season(self, season_html):
		tds = season_html.find_all('td', {'align': 'left'})
		res = []
		for td in tds:
			url = td.find("a")["href"]
			game_date = str(td.a.contents[0].split()[2])
			res += [(game_date, url)]
		return res

	def _download_page(self, url, parse=True):
		try:
			if parse:
				logger.debug("Downloading %s", url)
				html = soup(urllib2.urlopen(url), 'lxml')
			else:
				logger.debug("Downloading %s as html string", url)
				html = urllib2.urlopen(url).decode(
					'utf-8').encode('ascii', 'ignore')

			return html
		except (Exception, urllib2.HTTPError) as e:
			logger.error("failed to open %s", url)
			raise e

	def fetch_lastest_game_from_season(self, season, season_options=None):
		"""Download lastest game for the given season with output_type of either html, json or uploading
		to your firebase database (default option).

		Args:
				season(int): Season you want to download.
				*season_options(int): range for season from 1 to season_options inclusively. 

		Returns:
				Beautiful soup object for html page for target game.

		"""
		try:
			if season_options and season not in season_options:
				raise Exception('Season does not exist!')

			game_html = self._get_game_list(season)
			game_url, game_date = self._parse_latest_game(game_html)
			logger.debug(
				"url: %s, game_date: %s fetched successfully.", game_url, game_date)
			return self._download_page(game_url), game_date
		except Exception as e:
			logger.error(e)
			raise

	def fetch_specific_game(self, game_date, game_url):
		"""Download specific game for the given game_date and season with output_type of either html, json or uploading
		to your firebase database.

		Args:
				game_id(str): Game id for the jeopady game you want.
				game_options(dict): a dict of {game_date: game_date} for exisiting games for current season. 

		Returns:
				Beautiful soup object for html page for target game.

		"""
		try:
			logger.debug(
				"url: %s, game_date: %s fetched successfully.", game_url, game_date)
			return self._download_page(game_url)
		except Exception as e:
			logger.error(e)
			raise
