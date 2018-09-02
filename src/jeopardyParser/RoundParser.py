#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as soup
import re
from collections import defaultdict
from Clue import Clue
from answerParser import parse_answer

import logging
logger = logging.getLogger(__name__)

class RoundParser:
    def __init__(self, game, contestants):
		self.game = game
		self.contestants = contestants
		self.hash_num_round = {
			1: "jeopardy_round", 2: "double_jeopardy_round", 3: "final_jeopardy_round"}
		info = {'keys': [], 'game_count': {}, 'contestants_info': self.contestants.info,
				'contestants_keys': self.contestants.ids}
		self.res = {'info': info}
		self.value_hash = {}
		self.run()

    def __str__(self):
        import json
        return json.dumps(self.res, indent=4)

    def run(self):
        # parse first 2 rounds
        for i in range(1, 3):
			logger.info('Parsing Round %s ...', i)
			r = self.game.find(id=self.hash_num_round[i])
			if r:
				items = []
				genres, cnt = self.parseRound(r)

				for key, val in genres.iteritems():
					temp = {'genre': key, 'questions': val}
					items.append(temp)
				self.res['info']['keys'].append(i)
				self.res['info']['game_count'][i] = cnt
				self.res[i] = items

        # parse final jeopardy
        r = self.game.find(id=self.hash_num_round[3])
        if r:
			logger.info('Parsing Final Round ...')
			items = []
			genres = self.parseFinalRound(r)

			for key, val in genres.iteritems():
				temp = {'genre': key, 'questions': val}
				items.append(temp)
			self.res['info']['keys'].append(3)
			self.res['info']['game_count'][3] = 1
			self.res[3] = items

    def _getClueRowCol(self, s):
        match = re.findall(r'J_(.*?)\'', s)
        if not match:
            # final jeopardy
            return 1, 1
        else:
            # jeopardy round or double jeopardy
            col, row = map(int, match[0].split('_'))
            return col, row

    def _createValueHash(self, _clues):
        for c in _clues:
            if c.find("table"):
                answer = soup(
                    c.find("div", onmouseover=True).get("onmouseover"), "lxml")
                s = answer.find("p").get_text()
                _, row = self._getClueRowCol(s)

                if row in self.value_hash:
                    continue

                if c.find("td", class_=re.compile("clue_value_daily_double")):
                    continue
                else:
                    value = c.find("td", class_=re.compile("clue_value"))
                    value = value.get_text().split("$")[1].replace(",", "")
                    self.value_hash[row] = value

    def parseRound(self, r):
        categories = [c.get_text()
                      for c in r.find_all("td", class_="category_name")]
        genres = defaultdict(list)

        _clues = r.find_all("td", class_="clue")
        self._createValueHash(_clues)
        cnt = 0

        i = 0

        for c in _clues:
            if c.find("table"):
                # case where we have daily double
                if c.find("td", class_=re.compile("clue_value_daily_double")):
                    value = c.find("td", class_=re.compile(
                        "clue_value_daily_double"))
                    _type = "double"
                else:
                    value = c.find("td", class_=re.compile("clue_value"))
                    _type = "single"

                value = value.get_text().split("$")[1].replace(",", "")

                question = c.find("td", class_="clue_text")
                if question.find('a'):
                    i += 1
                    if i % 7 == 0:
                        i = 1
                    category = categories[i-1]
                    temp = Clue("placeholder")
                    genres[category].append(temp.toJSON())
                    continue

                answer = soup(
                    c.find("div", onmouseover=True).get("onmouseover"), "lxml")
                right, wrong = None, None
                if answer.find_all("td", class_="right"):
                    right = [s.get_text()
                             for s in answer.find_all("td", class_="right")]
                if answer.find_all("td", class_="wrong"):
                    wrong = [s.get_text()
                             for s in answer.find_all("td", class_="wrong")]
                    if 'Triple Stumper' in wrong:
                        wrong = self.contestants.ids
                question = question.get_text()
                s = answer.find("p").get_text()
                col, row = self._getClueRowCol(s)

                i = col
                answer = answer.find(
                    "em", class_="correct_response").get_text()

                answerParsed = parse_answer(answer)
                category = categories[col-1]
                _id = str(col) + str(row)

                if _type is "double":
                    dailyDoublePrice = value
                    value = self.value_hash[row]
                    temp = Clue(_type, value, question, answer,
                                answerParsed, right, wrong, _id, dailyDoublePrice)
                else:
                    temp = Clue(_type, value, question, answer,
                                answerParsed, right, wrong, _id)

                genres[category].append(temp.toJSON())
                cnt += 1
            else:
                i += 1
                if i % 7 == 0:
                    i = 1
                category = categories[i-1]
                temp = Clue("placeholder")
                genres[category].append(temp.toJSON())

        self.value_hash = {}
        return genres, cnt 

    def parseFinalRound(self, r):
        # The final Jeopardy! round
        genres = defaultdict(list)
        category = r.find("td", class_="category_name").get_text()
        question = r.find("td", class_="clue_text").get_text()
        answer = soup(
            r.find("div", onmouseover=True).get("onmouseover"), "lxml")
        right, wrong = None, None
        if answer.find_all("td", class_="right"):
            right = [s.get_text()
                     for s in answer.find_all("td", class_="right")]
        if answer.find_all("td", class_="wrong"):
            wrong = [s.get_text()
                     for s in answer.find_all("td", class_="wrong")]
            if 'Triple Stumper' in wrong:
                wrong = self.contestants.ids

        answer = answer.find("em").get_text()
        answerParsed = parse_answer(answer)

        if re.search(r"^(1 of)", answer):
            answer = answer.split("&")[0]

        temp = Clue("single", None, question, answer,
                    answerParsed, right, wrong)
        genres[category].append(temp.toJSON())

        return genres
