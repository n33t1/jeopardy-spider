#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)


class SeasonAPI:
	def __init__(self, FirebaseAPI, season=None):
		self.GAMES_REF = FirebaseAPI.GAMES_REF
		self.UTILS_REF = FirebaseAPI.UTILS_REF
		if season:
			self.set_season_endpoint(season)
		logger.debug("Initalized API for season %s .", season)
	
	def set_season_endpoint(self, season):
		self.season = season
		self.endpoint = self.GAMES_REF.child('season-' + str(season))

	def get_seasons(self):
		return self.GAMES_REF.child('seasons').get() 

	def set_seasons(self, season):
		try:
			self.GAMES_REF.child('seasons').set(season)
		except Exception as e:
			print e
			raise

	def get_from_UTILS(self, key):
		return self.UTILS_REF.child(key).get()

	def post_to_UTILS(self, key, new_MD5):
		try:
			self.UTILS_REF.child(key).set(new_MD5)
		except Exception as e:
			print e
			raise

	def _fetch_keys(self):
		try:
			logger.debug("Fetching keys for season %s ...", self.season)
			keys = self.endpoint.child('keys').get()
			return keys.keys()
		except Exception as e:
			logger.error("Error fetching keys for season %s. Error: %s", self.season, e)
			raise

	def _update_keys(self, game_date):
		try:
			logger.debug("Updating keys for season %s game date %s ...", self.season, game_date)
			self.endpoint.child('keys').child(game_date).set(1)
		except Exception as e:
			logger.error("Error updating keys for season %s game date %s. Error: %s", self.season, game_date, e)
			raise 

	def upload_game(self, game_date, game_details):
		try:
			# TODO: async.parallel
			# Having two functions success or fail at the same time
			self._update_keys(game_date)
			self.endpoint.child(game_date).set(game_details)
			logger.debug("%s uploaded successfully!", game_date)
		except Exception as e:
			print e
			raise e

	def delete_season(self):
		try:
			self.endpoint.delete()
			logger.debug("%s deleted successfully!", self.season)
		except Exception as e:
			print e
			raise e

    # def read_keys(self):
    #     keys = self._fetch_keys()
    #     print keys
