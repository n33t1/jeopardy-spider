#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import traceback
import concurrent.futures as futures
import threading
import gevent.monkey
import gevent.pool
gevent.monkey.patch_all()

import logging
logger = logging.getLogger(__name__)

class GeventEngine:
	def __init__(self, fetcher, gameParser, uploader):
		self.fetcher = fetcher
		self.gameParser = gameParser
		self.uploader = uploader
	
	def process_season(self, season):
		self.uploader.set_season_endpoint(season)
		pool = gevent.pool.Pool(5)
		game_date_url_list = self.fetch_game_list_for_season(season)
		pool.map(self._fetch_parse_and_upload, game_date_url_list)
		pool.join()
		if len(self.uploader.fetch_keys()) != len(map(lambda (game_date, _): game_date, self.all_games)):
			raise Exception('Some games was not uploaded for season %s!', season)
		else:
			logger.debug("Season %s uploaded successfully!", season)
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

			# if uploaded_game is empty, meaning that season was not created in firebase DB
			if not uploaded_games:
				# we just return all games here 
				return all_games
			
			return filter(lambda (game_date, _): game_date not in uploaded_games, all_games)
		except Exception as e:
			logger.error("Unable to fetch game list for season %s . Error: %s", season, e)
			raise
