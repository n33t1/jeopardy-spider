#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import os
import urllib2
from bs4 import BeautifulSoup
import time
import jparser
import parser
import argparse
import sys
import concurrent.futures as futures

ERROR_MSG = "ERROR: No game"
SECONDS_BETWEEN_REQUESTS = 3
NUM_THREADS = 2

base_url = "http://j-archive.com/"
base_page = urllib2.urlopen(base_url).read()
soup = BeautifulSoup(base_page, "html.parser")

def main(season, output_type):
      try:
            import multiprocessing
            # Since it's a lot of IO let's double # of actual cores
            NUM_THREADS = multiprocessing.cpu_count() * 2
            print 'Using {} threads'.format(NUM_THREADS)
      except (ImportError, NotImplementedError):
            pass

      if season is not None:
            parse_specific_season(season, output_type)
      else:
            parse_season(output_type)

def parse_specific_season(season, output_type):
      url = "http://www.j-archive.com/showseason.php?season=%s" % season

      archive_folder = 'season_%s' % str(season)
      create_archive_dir(archive_folder)

      season_html = download_page(url)
      print "Now download season %s" % str(season)
      parse_game(season_html, archive_folder, output_type)

def parse_season(output_type):
      for line in soup.select('a[href^="showseason.php"]'):
            url = line.get('href')
            url = base_url + url
            season = url.partition("season=")[2]

            archive_folder = 'season_%s' % str(season)
            create_archive_dir(archive_folder)

            season_html = download_page(url)
            print "Now download season %s" % str(season)
            parse_game(season_html, archive_folder, output_type)

def parse_game(season_html, archive_folder, output_type):
      td_al_left = season_html.find_all('td',{'align':'left'})
      i = 1
      with futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            # We submit NUM_THREADS tasks at a time since we don't know how many
            # pages we will need to download in advance
            while i < len(td_al_left):
                  l = []
                  for _ in range(NUM_THREADS):
                        td = td_al_left[i]
                        date = td.a.contents[0]
                        game_date = date.split()[2]

                        url = td.a['href']
                        game_id = url.partition("game_id=")[2]

                        print "Now download game %s" % str(game_date)

                        f = executor.submit(download_and_save_page, url, game_date, archive_folder, output_type)
                        l.append(f)
                        i += 1
                        if i == len(td_al_left):
                              break

                  # Block and stop if we're done downloading the page
                  if not all(f.result() for f in l):
                        break

def download_and_save_page(url, game_date, archive_folder, output_type):
      new_file_name = "%s.html" % game_date if output_type == 'html' else "%s.json" % game_date
      destination_file_path = os.path.join(archive_folder, new_file_name)
      if not os.path.exists(destination_file_path):
            html = download_page(url)
            if ERROR_MSG in html:
                  # Now we stop
                  print "Finished downloading. Now parse."
                  return False
            elif html:
                  html_string = str(html)

                  if output_type == 'html':
                        save_file(html_string, destination_file_path)
                  elif output_type == 'json':
                        html_lxml = BeautifulSoup(html_string, 'lxml')
                        parse_to_json(html_lxml, destination_file_path)
                  else:
                        raise NameError('File type not valid!')

                  time.sleep(SECONDS_BETWEEN_REQUESTS)
      else:
            print "Already downloaded %s" % destination_file_path
      return True

def download_page(url):
      html = None
      try:
            response = urllib2.urlopen(url)
            if response.code == 200:
                  print "Downloading ", url
                  # html = response.read()
                  html = BeautifulSoup(response, "html.parser")
            else:
                  print "Invalid URL: ", url
      except urllib2.HTTPError:
                  print "failed to open ", url
      return html

def save_file(html_string, filename):
      try:
            with open(filename, 'w') as f:
                  f.write(html_string)
      except IOError:
            print "Couldn't write to file %s" % filename

def parse_to_json(html_string, destination_file_path):
      test = jparser.Round(html_string, destination_file_path)
      test.parseGame()

def create_archive_dir(season):
      if not os.path.isdir(season):
            os.mkdir(season)

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

      main(args.season, args.output)
