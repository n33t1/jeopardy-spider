"""
We want to have a scheduler that runs every day to check whether there is an new epsode posted.

More research need to be done on Python Scheduler, but these posts are a good start:
https://devcenter.heroku.com/articles/clock-processes-python
https://stackoverflow.com/questions/21214270/scheduling-a-function-to-run-every-hour-on-flaska

Essentially, we want this scheduler to check whether a new game is added. And there are 
two things we need to check:
  1. Season list: http://j-archive.com/listseasons.php
  2. Game/episode list for lastest season: http://j-archive.com/showseason.php?season=34

Plan A (trashed, see below):
Steps:
1. We record last time when we send the If-Modified-Since request. Write to log.
2. Send new If-Modified-Since request every day. If we receive 304 as response, then it means the nothing
new was added. But if we receive 200 as response, then we should 
  1. update last_time to current timestamp 
  2. if a new season is added:
    1. add season to firebase rn-jeopardy-clues/games/season
  2. go to 3
  3. if a new game is added:
  download, parser and update to firebase. Add to rn-jeopardy-clues/season-<s> and update yyyy-mm-dd to rn-jeopardy-clues/season-<s>/keys
  return True
  4. Write to log

Sadly, since J! Archive server does not return If-Modified-Since (response attached as following), we need plan B.
  Date: Sun, 26 Aug 2018 19:48:25 GMT
  Server: Apache/2.2.29 (Unix) mod_ssl/2.2.29 OpenSSL/1.0.1e-fips mod_fcgid/2.3.9 mod_bwlimited/1.4
  X-Powered-By: PHP/5.5.37
  Connection: close
  Transfer-Encoding: chunked
  Content-Type: text/html; charset=utf-8

Plan B:
  Similar to the steps in Plan A, but now we are comparing previous md5 and current md5, instead of reponses 
  for If-Modified-Since request. 

ENDPOINTS we need:
  * rn-jeopardy-clues/games/seasons: INT, last_season
  * rn-jeopardy-clues/games/season-<last_season>: list[::-1] is the last episode
"""

import md5
import requests
import urllib2
import datetime
from firebase.SeasonAPI import SeasonAPI
from downloader.multithreading_gevent import Downloader

from apscheduler.schedulers.blocking import BlockingScheduler

# TODO: setup logging
import logging

class Scheduler:
    def __init__(self, GAMES_REF, UTILS_REF):
        self.UTILS_REF = UTILS_REF
        self.GAMES_REF = GAMES_REF

        # disables autorun for heroku since scheduling is handled externally.
        # self.run()

    # not called from heroku
    def run(self):
        self.scheduler = BlockingScheduler()
        self.scheduler.add_job(self.check_and_update_game,
                               'cron', day_of_week='*', hour=2)
        self.scheduler.add_job(self.heartbeat, 'cron', day_of_week='*', hour=2)
        self.scheduler.add_job(
            self.check_maybe_update_season, 'cron', day_of_week='*', hour=2)
        # for debugging with smaller time intervals
        # self.scheduler.add_job(self.check_and_update_game, 'interval', seconds=10)
        # self.scheduler.add_job(self.check_maybe_update_season, 'interval', seconds=10)

        self.scheduler.start()

    def _calc_date_diff(self, last_updated_date):
        today = datetime.date.today()
        prev = datetime.datetime.strptime(last_updated_date, "%d-%m-%Y").date()
        diff = today - prev
        return diff.days

    def _get_last_season(self):
        return self.GAMES_REF.child('seasons').get()

    def _set_last_season(self, season):
        self.GAMES_REF.child('seasons').set(season)

    def _get_from_UTILS(self, key):
        return self.UTILS_REF.child(key).get()

    def _post_to_UTILS(self, key, new_MD5):
        try:
            self.UTILS_REF.child(key).set(new_MD5)
        except Exception as e:
            print e
            raise

    def _get_curr_MD5(self, url):
        html = urllib2.urlopen(url).read()
        return md5.new(html).hexdigest()

    def heartbeat(self):
        import time
        self.UTILS_REF.child('heartbeat').set(str(int(time.time())))

    def check_maybe_update_season(self):
        print "_check_season called!"
        last_updated_date = self._get_from_UTILS('LAST_UPDATED_TIME')
        date_diff = self._calc_date_diff(last_updated_date)
        if date_diff > 3:
            self.check_and_update_season()

    def check_and_update_season(self):
        prev_MD5 = self._get_from_UTILS('SEASON_MD5')
        prev_MD5 = prev_MD5.encode('utf8')
        SEASON_URL = "http://j-archive.com/listseasons.php"
        curr_MD5 = self._get_curr_MD5(SEASON_URL)
        # TODO: log timestamp
        if prev_MD5 != curr_MD5:
            print "updated utils/SEASON_MD5 to", curr_MD5
            self._post_to_UTILS('SEASON_MD5', curr_MD5)
            oldSeason = self._get_last_season()
            self._post_to_UTILS('last_season', oldSeason + 1)
            api = SeasonAPI(oldSeason + 1)
            Downloader(oldSeason + 1, 'firebase', api)
        else:
            # TODO
            print "timestamp, checked, utils/SEASON_MD5 did not change"

    def check_and_update_game(self):
        print "check_and_update_game called!"
        last_season = self._get_last_season()
        last_season = str(last_season)
        prev_MD5 = self._get_from_UTILS('GAME_MD5')
        prev_MD5 = prev_MD5.encode('utf8')
        GAME_URL = "http://j-archive.com/showseason.php?season=" + last_season
        curr_MD5 = self._get_curr_MD5(GAME_URL)
        # TODO: log timestamp
        if prev_MD5 != curr_MD5:
            print "updated utils/GAME_MD5 to", curr_MD5
            self._post_to_UTILS('GAME_MD5', curr_MD5)
            current_date = datetime.datetime.today().strftime('%Y-%m-%d')
            print "updated utils/LAST_UPDATED_TIME to", current_date
            self._post_to_UTILS('LAST_UPDATED_TIME', current_date)
            self._upload_to_firebase(last_season)
        else:
            # TODO
            print "timestamp, checked, utils/GAME_MD5 did not change"

    def _upload_to_firebase(self, season):
        season = int(season)
        api = SeasonAPI(season)
        d = Downloader(season, 'firebase', api)
        d.download_and_parse_game(season)
