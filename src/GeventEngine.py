#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

from fetcher import Fetcher
from jeopardyParser import JeopardyParser
from database import FirebaseAPI, SeasonAPI

import traceback
import concurrent.futures as futures
import threading
import gevent.monkey
import gevent.pool
gevent.monkey.patch_all()

import logging
logger = logging.getLogger(__name__)

class GeventEngine:
	def __init__(self):
		self.fetcher = Fetcher()
		self.gameParser = JeopardyParser()
		self.uploader = SeasonAPI(FirebaseAPI())
	
	def process_season(self, season):
		self.uploader.set_season_endpoint(season)
		pool = gevent.pool.Pool(5)
		game_date_url_list = self.fetch_game_list_for_season(season)
		pool.map(self._fetch_parse_and_upload, game_date_url_list)
		pool.join()
		if self.uploader.fetch_keys() != self.all_games:
			raise Exception('Some games was not uploaded for season %s!', season)
		else:
			self.all_games = None
		
	def _fetch_parse_and_upload(self, game_date_url_tuple):
		try:
			game_date, game_url = game_date_url_tuple
			game_soup = self.fetcher.fetch_specific_game(game_date, game_url)
			parsed_game = self.gameParser.parse_game(game_soup)
			self.uploader.upload_game(game_date, parsed_game)
		except Exception:
			logger.error("Processing game %s failed! Error: %s", game_date, traceback.format_exc())
			raise SystemExit

	def fetch_game_list_for_season(self, season):
		try:
			uploaded_games = self.uploader.fetch_keys()
			all_games = self.fetcher.fetch_game_list_for_season(season)
			self.all_games = all_games
			if not uploaded_games:
				return all_games
			return filter(lambda (game_date, _): game_date not in uploaded_games, all_games)
		except Exception as e:
			logger.error("Unable to fetch game list for season %s . Error: %s", season, e)
			raise
