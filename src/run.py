#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

from fetcher import Fetcher
from jeopardyParser import JeopardyParser
from database import FirebaseAPI, SeasonAPI
from scheduler import Scheduler
from apscheduler.schedulers.blocking import BlockingScheduler

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
