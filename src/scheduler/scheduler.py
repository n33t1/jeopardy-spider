'''

We want to have a scheduler that runs every day to check whether there is a epsode posted.

More research need to be done on Python Scheduler, but these posts is a good start:
https://devcenter.heroku.com/articles/clock-processes-python
https://stackoverflow.com/questions/21214270/scheduling-a-function-to-run-every-hour-on-flaska

Essentially, we want this scheduler to check whether a new game if added. And there are 
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
'''

"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google
Python Style Guide`_. Docstrings may extend over multiple lines.
Sections are created with a section header and a colon followed by a
block of indented text.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:   
http://google.github.io/styleguide/pyguide.html

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

    self.run()

  def run(self):
    self.scheduler = BlockingScheduler()
    self.scheduler.add_job(self.check_and_update_game, 'interval', seconds=5)
    self.scheduler.add_job(self.check_maybe_update_season, 'interval', seconds=5)
    # TODO: update and test cron scheduler
    # self.scheduler.add_job(self.myJob, 'cron', day_of_week='*', hour=17)
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
      season = self._get_last_season()
      api = SeasonAPI(season)
      api.upload_game(current_date, {"a": {"Asd": "Adsa"}, "b": "S"})
    else:
      # TODO
      print "timestamp, checked, utils/GAME_MD5 did not change"
