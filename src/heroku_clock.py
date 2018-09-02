'''
In the heroku branch, the scheduler has been separated from the clock worker
so that it will not be necessary to have a self-writeen background process that
sits idle for the entire day. 

In addition, it seems that logs are not visible until the program is halted with 
the intergrated approach. It would be nice to have a logger, though.
'''
from firebase import GAMES_REF, UTILS_REF, SeasonAPI
from scheduler import Scheduler
from apscheduler.schedulers.blocking import BlockingScheduler

schutil = Scheduler(GAMES_REF, UTILS_REF)

clock = BlockingScheduler()

@clock.scheduled_job('cron', hour=2)
def checkSeason():
  schutil.check_maybe_update_season()

@clock.scheduled_job('cron', hour=2)
def checkGame():
  schutil.check_and_update_game()

@clock.scheduled_job('interval', seconds = 10)
def heartbeat():
  schutil.heartbeat()

clock.start()