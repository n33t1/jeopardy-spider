#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import logging
from logging.config import fileConfig

fileConfig('logging_config.ini')

logger = logging.getLogger()
logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)

import parser
import argparse
import traceback

from fetcher import Fetcher
from jeopardyParser import JeopardyParser
from database import FirebaseAPI, SeasonAPI
from scheduler import Scheduler
from engine import GeventEngine


def run(args):
    try:
        # init fetcher and check for season range
        season = args.season
        fetcher = Fetcher()
        _, lastest_season = fetcher.get_latest_season()
        if season not in xrange(1, int(lastest_season) + 1):
            raise Exception('Season out of range!')

        # init parser and uploader
        gameParser = JeopardyParser()
        uploader = SeasonAPI(FirebaseAPI())

        if args.upload:
            engine = GeventEngine(fetcher, gameParser, uploader)
            engine.process_season(season)
        elif args.delete:
            uploader.delete_season(season)

    except Exception:
        logger.error('Task failed! Error: %s', traceback.format_exc())
        raise SystemExit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Script to upload or delete Jeopardy games from Firebase DB by season')

    parser.add_argument('-s', '--season', type=int, required=True,
                        help='jeopardy season to process')

    parser.add_argument('-d', '--delete', action='store_true',
                        help='set to true if you want to delete season')

    parser.add_argument('-u', '--upload', action='store_true',
                        help='set to true if you want to upload season')

    args = parser.parse_args()

    if not args.delete and not args.upload:
        parser.error(
            'At least one of upload or delete season action is required to specificity!')

    run(args)
