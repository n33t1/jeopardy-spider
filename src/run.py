# from jparser import JeopardyParser
# TODO: currently we need to run firebase/config.py in order to import
# because it's a singleton
# better solutions?
from firebase import GAMES_REF, UTILS_REF, SeasonAPI
# from scheduler import Scheduler

# scheduler = Scheduler(GAMES_REF, UTILS_REF)

# api = SeasonAPI(14)
# test = {"a": {"Asd": "Adsa"}, "b": "S"}
# api.upload_game("2018-08-28", test)

	
# sched.start()


from downloader import Downloader

api = SeasonAPI(24)
d = Downloader(24, 'json', api)
d.download_and_parse_game(24)

# import parser
# import argparse

# if __name__ == "__main__":
# 	parser = argparse.ArgumentParser(description='Script to download and parse jeopardy games.')
# 	parser.add_argument('-o', '--output',
# 						help='output file type, currently support html or json',
# 						default='json',
# 						choices=set(('html', 'json', 'firebase')))

# 	# still need to check range for season
# 	parser.add_argument('-s', '--season',
# 						help='jeopardy season to download',
# 						type=int)

# 	args = parser.parse_args()

# 	api = SeasonAPI(args.season)
# 	Downloader(args.season, args.output, api)
