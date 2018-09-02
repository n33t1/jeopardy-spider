#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

from ContestantsParser import ContestantsParser
from RoundParser import RoundParser

import logging
logger = logging.getLogger(__name__)

class JeopardyParser:
	def __init__(self):
		logger.debug('Jeopardy Parser created!')
	
	def parse_game(self, game):
		contestants = ContestantsParser(game)
		rounds = RoundParser(game, contestants)
		return rounds.res
