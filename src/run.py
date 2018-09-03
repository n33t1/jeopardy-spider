#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import logging
from logging.config import fileConfig

fileConfig('logging_config.ini')

logger = logging.getLogger()
logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)

from fetcher import Fetcher
from jeopardyParser import JeopardyParser
from database import FirebaseAPI, SeasonAPI
from scheduler import Scheduler
from engine import GeventEngine

# init fetcher, parser and uploader
fetcher = Fetcher()
gameParser = JeopardyParser()
uploader = SeasonAPI(FirebaseAPI())

engine = GeventEngine(fetcher, gameParser, uploader)

# example: uploading season 2 to firebase DB
engine.process_season(3)

# # example: deleting season 3 from firebase DB
# uploader.delete_season(3)
