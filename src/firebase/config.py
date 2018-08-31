import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
from utils import service_credentials

# Fetch the service account key JSON file contents
# TODO: replace with relative path
#cred = credentials.Certificate('/Users/n33t1/Dev/jeopardy-crawler/keys/rn-jeopardy-clues-firebase-adminsdk-tjzhw-a8735066d5.json')

cred = credentials.Certificate(service_credentials.getcert())

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
  'databaseAuthVariableOverride': {'uid' : 'crawlerserviceworker'}, 
  'databaseURL': 'https://rn-jeopardy-clues.firebaseio.com/'
})

GAMES_REF = db.reference('/games')
UTILS_REF = db.reference('/utils')