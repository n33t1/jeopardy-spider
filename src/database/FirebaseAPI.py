import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import service_credentials
from SeasonAPI import SeasonAPI

class FirebaseAPI:
	def __init__(self):
		# TODO
		# cred = credentials.Certificate(service_credentials.getcert())
		cred = credentials.Certificate('/Users/n33t1/Dev/jeopardy-crawler/keys/rn-jeopardy-clues-firebase-adminsdk-tjzhw-a8735066d5.json')

		# Initialize the app with a service account, granting admin privileges
		firebase_admin.initialize_app(cred, {
			'databaseAuthVariableOverride': {'uid': 'crawlerserviceworker'},
			'databaseURL': 'https://rn-jeopardy-clues.firebaseio.com/'
		})

		self._GAMES_REF = db.reference('/games')
		self._UTILS_REF = db.reference('/utils')

	@property
	def GAMES_REF(self):
		return self._GAMES_REF
	
	@property
	def UTILS_REF(self):
		return self._UTILS_REF
