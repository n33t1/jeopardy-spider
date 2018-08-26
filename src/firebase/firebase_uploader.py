from firebase import firebase
import json
import os
import parser
import argparse

base_url = "https://rn-jeopardy-clues.firebaseio.com"
firebase = firebase.FirebaseApplication(base_url, authentication=None)
isRemoving = False

def main(i):
      if isRemoving:
            # ideally we should check if season exist in db first with try catch block
            remove(i)
            print "removed season%s successfully!" % i
      else:
            add(i)
            print "uploaded season%s successfully!" % i
      
def add(i):
      season = 'season_%s' % i
      archive_folder = season
      season_url = "/" + 'season-%s' % i
      keys = firebase.get(base_url + '/games' + season_url + '/keys', None) or []
      cnt = len(keys)
      # # dates = [f.split('.')[0] for f in os.listdir(season)]
      for filename in os.listdir(archive_folder):
            game_date = filename.split('.')[0]
            if game_date not in keys:
                  print game_date
                  firebase.patch(base_url + '/games' + season_url + '/keys', {cnt: game_date})
                  # print base_url + '/games' + season_url + '/keys'
                  cnt += 1

                  destination_file_path = os.path.join(archive_folder, filename)
                  with open(destination_file_path) as json_file:
                        json_data = json.load(json_file)
                        firebase.patch(base_url + '/games' + season_url + "/" + game_date, json_data)
                        # print base_url + '/games' + season_url + "/" + game_date

def remove(i):
      season_url = '/games/' + 'season-%s' % i
      firebase.delete(season_url, None)

if __name__ == "__main__":
      parser = argparse.ArgumentParser(description='Script to upload json files to Firebase')
      parser.add_argument('-s', '--season',
                        help='season you want to upload to firebase',
                        type=str)

      parser.add_argument('-r', '--remove',
                        help='boolean flag for removing season', 
                        action='store_true')

      args = parser.parse_args()
      isRemoving = args.remove

      main(args.season)