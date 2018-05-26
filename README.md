# jeopardy-parser
Python crawler for jeopardy games on [J! Archive](http://j-archive.com/).

## Setup
```bash
git clone https://github.com/n33t1/jeopardy-parser.git
cd jeopardy-parser
pip install -r requirements.txt
```

This crawler provides 2 kind of output file formats: json and html. You can define the format you want with `-o html` or `-o json`.

If you want to download all seasons up to date, run `python download.py`. If you want to download a specific season in html files, say season 34, run `python download.py -s 34 -o html`.

Examplary json output file is included [here](https://github.com/n33t1/jeopardy-parser/blob/master/2002-09-09.json). For each clue, we have the following attributes:

* Jtype:
  * "single": single jeopardy. Prices for the corresponding clue should be either 200, 400, 600, 800 or 1000.
  * "double": daily doubles. Prices various. 
  * "placeholder": clue was missing from J! Archive website. All other fields are defined as null. 
* price
* prompt
* solution

Each game contains the following fields:
* keys: rounds in this game. If a game has keys equal to [1, 2], then it means that game onlys has Jeopardy! Round and Double Jeopardy! Round. 
* 1: stands for Jeopardy! Round
* 2: stands for Double Jeopardy! Round. Might be missing for some games. 
* 3: stands for Final Jeopardy! Round. Might be missing for some games. 