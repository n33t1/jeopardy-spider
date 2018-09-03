# jeopardy-spider
Python spider for jeopardy games on [J! Archive](http://j-archive.com/). This library provide 2 options: a spider monitoring and uploading newly added Jeopardy episodes in [heroku_scheduler](./src/heroku_scheduler.py) and a crawler with gevent for scraping and uploading a season of Jeopardy games in [run](./src/run.py). 

## Setup

```bash
git clone https://github.com/n33t1/jeopardy-parser.git
cd jeopardy-spider
pip install -r requirements.txt
```

Then you will need to set up firebase, download admin keys and store them in `./keys/rn-jeopardy-admin-keys.json` in order to use Firebase database.

TODO: Heroku set up guidence goes here 

## Example

Examplery use of crawling Jeopady games by season:

```bash
python src/run.py -s 34 -d # delete season 34 from firebase DB
python src/run.py -s 34 -u # upload season 34 to firebase DB
```

TODO: Heroku example goes here 

## TODO

Some fancy AI/NLP stuff we can do:
  1. Better Roman Numerials detection and smarter parsing for answers. Something to detect the semantic meaning.  
  2. Classification over `What if` and `Who is`.
