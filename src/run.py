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
from apscheduler.schedulers.blocking import BlockingScheduler
from GeventEngine import GeventEngine

# init fetcher, parser and uploader
fetcher = Fetcher()
gameParser = JeopardyParser()
uploader = SeasonAPI(FirebaseAPI())

schutil = Scheduler(fetcher, gameParser, uploader)
clock = BlockingScheduler()

@clock.scheduled_job('cron', hour=2)
def checkSeason():
  schutil.check_maybe_update_season()

@clock.scheduled_job('cron', hour=2)
def checkGame():
  schutil.check_and_update_game()

clock.start()
