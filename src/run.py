# from firebase import GAMES_REF, UTILS_REF, SeasonAPI
# from scheduler import Scheduler
# from apscheduler.schedulers.blocking import BlockingScheduler

import logging
from logging.config import fileConfig

fileConfig('logging_config.ini')

logger = logging.getLogger()
logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)

from downloader import Downloader
from jeopardyParser import JeopardyParser

downloader = Downloader()
gameParser = JeopardyParser()

game_soup = downloader.download_specific_game('6079', {'6079': 'Friday, July 27, 2018'})
s = gameParser.parse_game(game_soup)
# print s



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