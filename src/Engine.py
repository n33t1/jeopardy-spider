#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

from fetcher import Fetcher
from jeopardyParser import JeopardyParser
from database import FirebaseAPI, SeasonAPI

class Engine:
	def __init__(self):
		self.fetcher = Fetcher()
		self.gameParser = JeopardyParser()
		self.uploader = SeasonAPI(FirebaseAPI())