from config import GAMES_REF, UTILS_REF

class SeasonAPI:
  def __init__(self, season):
    self.season = season
    self.endpoint = GAMES_REF.child('season-' + str(season))
    # self.keys = self._fetch_keys()
    # print "keys: ", self.keys
  
  def _fetch_keys(self):
    try:
      keys = self.endpoint.child('keys').get()
      return keys.keys()
    except Exception as e:
      print e
      raise e
  
  def _update_keys(self, game_date):
    try:
      self.endpoint.child('keys').child(game_date).set(1)
    except Exception as e:
      print e
      raise e

  def upload_game(self, game_date, game_details):
    """Uploading a new game to firebase. 
    We add game_date to /game/season-<s>/keys and add game details 
    to /game/season-<s>/game_date

        Args:
            game_date (str): yyyy-mm-dd
            game_details (dict): see TODO
        """
    try:
      # TODO: async.parallel
      # Having two functions success or fail at the same time
      self._update_keys(game_date)
      self.endpoint.child(game_date).set(game_details)
      print "%s uploaded successfully!" % game_date
    except Exception as e:
      print e
      raise e
  
  def delete(self):
    try:
      # TODO: async.parallel
      # Having two functions success or fail at the same time
      self._update_keys(game_date)
      self.endpoint.child(game_date).set(game_details)
      print "%s uploaded successfully!" % game_date
    except Exception as e:
      print e
      raise e
  
  # def read(self):
  # 	pass
