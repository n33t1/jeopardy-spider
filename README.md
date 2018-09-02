# jeopardy-parser
Python crawler for jeopardy games on [J! Archive](http://j-archive.com/).

## Setup
```bash
git clone https://github.com/n33t1/jeopardy-parser.git
cd jeopardy-parser
pip install -r requirements.txt
```
## Usage
This crawler provides 2 kinds of output file formats: `json` and `html`. You can define the format you want with `-o json` or `-o html`.

If you want to download all seasons up to date, run `python download_multiprocessing.py` or `python download_threading_gevent.py`. `download_threading_gevent.py` uses multithreading and `gevent` while `download_multiprocessing.py` uses multiprocessing. Generally speaking, the former is faster than the latter. If you want to download a specific season in html files, say season 34, run `python download_threading_gevent.py -s 34 -o html`.

This crawler also provides firebase upload capabilities (which can be done by calling `python src/run.py -s [season] -o firebase`) to a project-specific firebase realtime db. As of right now this functionality is not planned to be opened for other firebase databases.

## Output

Sample json output file is included [here](https://github.com/n33t1/jeopardy-parser/blob/master/2002-09-09.json). For each clue, we have the following attributes:

* Jtype:
  * "single": single jeopardy. Prices for the corresponding clue should be either 200, 400, 600, 800 or 1000.
  * "double": daily doubles. Prices various. 
  * "placeholder": clue was missing from J! Archive website. All other fields are defined as null. 
* price
* prompt
* solution
* parsed_solution

Each game contains the following fields:
* keys: rounds in this game. If a game has keys equal to [1, 2], then it means that game only has Jeopardy! Round and Double Jeopardy! Round. 
* 1: stands for Jeopardy! Round
* 2: stands for Double Jeopardy! Round. Might be missing for some games. 
* 3: stands for Final Jeopardy! Round. Might be missing for some games. 

