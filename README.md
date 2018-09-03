# jeopardy-spider
Python spider for jeopardy games on [J! Archive](http://j-archive.com/). It provides the option of monitoring new games added to J! Archive and upload to firebase database if so. 

This project is made of two parts: a spider for monitoring and uploading newly added Jeopardy episodes in [heroku_scheduler](./src/heroku_scheduler.py) and a crawler for scraping and uploading a season of Jeopardy games in [run](./src/run.py). 

## Setup
```bash
git clone https://github.com/n33t1/jeopardy-parser.git
cd jeopardy-parser
pip install -r requirements.txt
```

Some fancy AI/NLP stuff we can do:
  1. Better Roman Numerials detection and smarter parsing for answers. Something to detect the semantic meaning.  
  2. Classification over `What if` and `Who is`.
