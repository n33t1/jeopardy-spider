#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import json
from collections import defaultdict
import answerParser

class Jeopardy:
      def __init__(self, soup):
            self.soup = soup
            self.airdate = self.soup.title.get_text().split()[-1]
      
      def toJSON(self):
            return json.dumps(self.__dict__)

class Clue:
      def __init__(self, price, prompt, solution, parsed_soultion, Jtype):
            self.Jtype = Jtype
            self.price = price
            self.prompt = prompt
            self.solution = solution
            self.parsed_soultion = parsed_soultion

      def toJSON(self):
            if self.Jtype == "placeholder":
                  temp = {'Jtype': self.Jtype}

            temp = {'price': self.price, 'prompt': self.prompt, 'solution': self.solution, 'parsed_soultion': self.parsed_soultion, 'Jtype': self.Jtype}
            return temp
            # return json.dumps(self.__dict__)

class Round(Jeopardy):
      def __init__(self, soup, destination_file_path):
            Jeopardy.__init__(self, soup)
            self.hash_num_round = {1: "jeopardy_round", 2: "double_jeopardy_round", 3: "final_jeopardy_round"}
            self.filename = destination_file_path
            self.res = {'keys':[]}
      
      def toJSON(self):
            try:
                  with open(self.filename, 'w') as f:
                        f.write(json.dumps(self.res, indent=4))
            except IOError:
                  print "Couldn't write to file %s" % self.filename

      def parseGame(self):
            for i in range(1, 3):
                  r = self.soup.find(id=self.hash_num_round[i])
                  if r:
                        items = []
                        genres = self.parseRound(r)

                        for key, val in genres.iteritems():
                              temp = {'genre': key, 'questions': val}
                              items.append(temp)
                        self.res['keys'].append(i)
                        self.res[i] = items
            
            # parse final jeopardy
            r = self.soup.find(id=self.hash_num_round[3])
            if r:
                  items = []
                  genres = self.parseFinalRound(r)

                  for key, val in genres.iteritems():
                        temp = {'genre': key, 'questions': val}
                        items.append(temp)
                  self.res['keys'].append(3)
                  self.res[3] = items
            self.toJSON()


      def getClueRowCol(self, s):
            match = re.findall(r'J_(.*?)\'', s)
            if not match:
                  # final jeopardy
                  return 1, 1
            else:
                  # jeopardy round or double jeopardy
                  col, row = map(int, match[0].split('_'))
                  return col, row

      def parseFinalRound(self, r):
            # The final Jeopardy! round
            genres = defaultdict(list)
            category = r.find("td", class_="category_name").get_text()
            question = r.find("td", class_="clue_text").get_text()
            answer = BeautifulSoup(r.find("div", onmouseover=True).get("onmouseover"), "lxml")
            answer = answer.find("em").get_text()
            answerParsed = answerParser.main(answer)

            if re.search(r"^(1 of)", answer):
                  answer = answer.split("&")[0]
                  
            temp = Clue(None, question, answer, answerParsed, "single")
            genres[category].append(temp.toJSON())

            return genres

      def parseRound(self, r):
            categories = [c.get_text() for c in r.find_all("td", class_="category_name")]
            genres = defaultdict(list)

            _clues = r.find_all("td", class_="clue")
            i = 0

            for c in _clues:
                  if c.find("table"):
                        # case where we have daily double
                        if c.find("td", class_=re.compile("clue_value_daily_double")):
                              value = c.find("td", class_=re.compile("clue_value_daily_double"))
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
                              temp = Clue(None, None, None, None, "placeholder")
                              genres[category].append(temp.toJSON())
                              continue

                        answer = BeautifulSoup(c.find("div", onmouseover=True).get("onmouseover"), "lxml")
                        question = question.get_text()
                        s = answer.find("p").get_text()
                        col, row = self.getClueRowCol(s)
                        i = col
                        answer = answer.find("em", class_="correct_response").get_text()
                        answerParsed = answerParser.main(answer)
                        category = categories[col-1]
                        temp = Clue(value, question, answer, answerParsed, _type)
                        genres[category].append(temp.toJSON())
                  else:
                        i += 1
                        if i % 7 == 0: 
                              i = 1
                        category = categories[i-1]
                        temp = Clue(None, None, None, None, "placeholder")
                        genres[category].append(temp.toJSON())
            return genres

# with open("season_1/1985-06-03.html") as f:
#       data = f.read()
#       soup = BeautifulSoup(data, 'html.parser')
#       r = Round(soup, "test.json")
#       r.parseGame()