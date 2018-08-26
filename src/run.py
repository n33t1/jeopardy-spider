# from jparser import JeopardyParser
from downloader import Downloader

import parser
import argparse

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Script to download and parse jeopardy games.')
	parser.add_argument('-o', '--output',
						help='output file type, currently support html or json',
						default='json',
						choices=set(('html', 'json')))

	# still need to check range for season
	parser.add_argument('-s', '--season',
						help='jeopardy season to download',
						type=int)

	args = parser.parse_args()
	Downloader(args.season, args.output)