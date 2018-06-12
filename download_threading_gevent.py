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
import threading
import gevent.monkey
gevent.monkey.patch_all()

# TODO: parse clue answers
# TODO: filter media files

ERROR_MSG = "ERROR: No game"
SECONDS_BETWEEN_REQUESTS = 3
NUM_THREADS = 2 

base_url = "http://j-archive.com/"
base_page = urllib2.urlopen(base_url).read()
soup = BeautifulSoup(base_page, "html.parser")

class threadDownload(threading.Thread):
      def __init__(self, que, archive_folder, output_type):
            threading.Thread.__init__(self)
            self.que = que
            self.archive_folder = archive_folder
            self.output_type = output_type

      def run(self):               
            length = len(self.que)
            coroutineNum = length # TODO: gevent wont be triggered if coroutineNum > length. need to be fixed. 
            for i in range(coroutineNum):
                  jobs = []
                  left = i * (length // coroutineNum)

                  if (i + 1) * (length // coroutineNum) < length:            
                        right = (i+1) * (length // coroutineNum)
                  else:
                        right = length
                  
                  print left, right, length

                  for td in self.que[left:right]:
                        url = td.find("a")["href"]
                        game_date = td.a.contents[0].split()[2]
                        jobs.append(gevent.spawn(download_and_save_page, url, game_date, self.archive_folder, self.output_type))
                  gevent.joinall(jobs)

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
      tdlist = season_html.find_all('td',{'align':'left'})
      l = len(tdlist)

      queList = []
      threadNum = 6 # threads we are using here
      for i in range(threadNum):
            que = [] #Queue.Queue()
            queDate = [] #Queue.Queue()
            left = i * (l // threadNum)
            if (i+1) * (l // threadNum) < l:            
                  right = (i+1) * (l // threadNum)
            else:
                  right = l

            for td in tdlist[left:right]:
                  que.append(td)
            queList.append(que)

      threadList = []
      for i in range(threadNum):
            threadList.append(threadDownload(queList[i], archive_folder, output_type))
      for thread in threadList:
            thread.start() # starting multithreading
      for thread in threadList:
            thread.join()

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
