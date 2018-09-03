#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

import logging
logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, fetcher, gameParser, uploader):
        self.fetcher = fetcher
        self.gameParser = gameParser
        self.uploader = uploader

        # init season attribute for uploader/SeasonAPI to be latest season
        _, lastest_season = fetcher.get_latest_season()
        uploader.set_season_endpoint(lastest_season)

    # not called from heroku
    def run(self):
        self.scheduler = BlockingScheduler()
        self.scheduler.add_job(self.check_and_update_game,
                               'cron', day_of_week='*', hour=2)
        self.scheduler.add_job(
            self.check_maybe_update_season, 'cron', day_of_week='*', hour=2)

        # for debugging with smaller time intervals
        # self.scheduler.add_job(self.check_and_update_game, 'interval', seconds=10)
        # self.scheduler.add_job(self.check_maybe_update_season, 'interval', seconds=10)

        self.scheduler.start()

    def _calc_date_diff(self, last_updated_date):
        today = datetime.date.today()
        prev = datetime.datetime.strptime(last_updated_date, "%Y-%m-%d").date()
        diff = today - prev
        return diff.days

    def _get_last_season(self):
        return self.uploader.get_seasons()

    def _set_last_season(self, season):
        self.uploader.set_seasons(season)

    def _get_from_UTILS(self, key):
        return self.uploader.get_from_UTILS(key)

    def _post_to_UTILS(self, key, new_MD5):
        self.uploader.post_to_UTILS(key, new_MD5)

    def _get_curr_MD5(self, url):
        return self.fetcher.get_MD5(url)

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
        if prev_MD5 != curr_MD5:
            logger.debug("New season added! Updating utils/SEASON_MD5 ...")
            self._post_to_UTILS('SEASON_MD5', curr_MD5)
            oldSeason = self._get_last_season()
            self._post_to_UTILS('last_season', oldSeason + 1)
            self.uploader.set_season_endpoint(oldSeason + 1)
        else:
            logger.debug("Season list reamins the same. No new season added.")

    def check_and_update_game(self):
        lastest_season = self._get_last_season()
        prev_MD5 = self._get_from_UTILS('GAME_MD5')
        prev_MD5 = prev_MD5.encode('utf8')
        GAME_URL = "http://j-archive.com/showseason.php?season=" + \
            str(lastest_season)
        curr_MD5 = self._get_curr_MD5(GAME_URL)
        if prev_MD5 != curr_MD5:
            logger.debug(
                "New game added! Updating utils/GAME_MD5 and utils/LAST_UPDATED_TIME ...")
            self._post_to_UTILS('GAME_MD5', curr_MD5)
            current_date = datetime.datetime.today().strftime('%Y-%m-%d')
            self._post_to_UTILS('LAST_UPDATED_TIME', current_date)
            self._fetch_parse_and_upload(lastest_season)
        else:
            logger.debug("Game list remains the same. No new game added.")

    def _fetch_parse_and_upload(self, season):
        latest_game, latest_game_date = self.fetcher.fetch_lastest_game_from_season(
            season)
        parsed_game = self.gameParser.parse_game(latest_game)
        self.uploader.upload_game(latest_game_date, parsed_game)
