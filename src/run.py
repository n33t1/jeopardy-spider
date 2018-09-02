# from firebase import GAMES_REF, UTILS_REF, SeasonAPI
# from scheduler import Scheduler
# from apscheduler.schedulers.blocking import BlockingScheduler

import logging
from logging.config import fileConfig

fileConfig('logging_config.ini')
logger = logging.getLogger()

from downloader import Downloader

d = Downloader(34, "json")

# schutil = Scheduler(GAMES_REF, UTILS_REF)

# clock = BlockingScheduler()

# @clock.scheduled_job('cron', hour=2)
# def checkSeason():
#     schutil.check_maybe_update_season()

# @clock.scheduled_job('cron', hour=2)
# def checkGame():
#     schutil.check_and_update_game()

# if __name__ == "__main__":
#     clock.start()