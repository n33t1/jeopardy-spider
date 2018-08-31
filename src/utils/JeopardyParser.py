#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import json
from collections import defaultdict
import answerParser

class JeopardyParser:
  def __init__(self, soup):
    self.soup = soup
    self.airdate = self.soup.title.get_text().split()[-1]
    self.contestants = Contestants(soup)
  
  def toJSON(self):
    return json.dumps(self.__dict__)

class Clue:
  def __init__(self, Jtype, price=None, prompt=None, solution=None, parsed_soultion=None, right=None, wrong=None, id=None, dailyDoublePrice=None):
    self.Jtype = Jtype
    self.price = price
    self.prompt = prompt
    self.solution = solution
    self.dailyDoublePrice = dailyDoublePrice
    self.parsed_soultion = parsed_soultion
    self.id = id or 'null'
    self.right = right or 'null'
    self.wrong = wrong or 'null'

  def toJSON(self):
    if self.Jtype == "placeholder":
      temp = {'Jtype': self.Jtype}
    elif self.Jtype == "double":
      temp = {'price': self.price, 'dailyDoublePrice': self.dailyDoublePrice, 'prompt': self.prompt, 'solution': self.solution, \
        'parsed_soultion': self.parsed_soultion, 'Jtype': self.Jtype, 'right': self.right, 'wrong': self.wrong, 'id': self.id}
    else:
      temp = {'price': self.price, 'prompt': self.prompt, 'solution': self.solution, \
        'parsed_soultion': self.parsed_soultion, 'Jtype': self.Jtype, 'right': self.right, 'wrong': self.wrong, 'id': self.id}

    return temp

class Contestants:
  def __init__(self, soup):
    self.soup = soup
    self.ids = []
    self.info = self.findContestants()
  
  def findContestants(self):
    res = []
    contestants = self.soup.find_all("p", class_="contestants")
    for c in contestants:
      player_name =  c.find("a").get_text()
      player_id = player_name.split(" ")[0]
      self.ids.append(player_id)
      player_info = c.get_text()
      res.append({"player_id": player_id, "player_info": player_info})
    return res

class Round(JeopardyParser):
  def __init__(self, soup, **kwargs):
    self.filename = kwargs.get('destination_file_path', None)
    self.game_date = kwargs.get('game_date', None)

    JeopardyParser.__init__(self, soup)
    self.hash_num_round = {1: "jeopardy_round", 2: "double_jeopardy_round", 3: "final_jeopardy_round"}
    temp = {'keys':[], 'contestants_info': self.contestants.info, 'contestants_keys': self.contestants.ids}
    self.res = {'info': temp}
    self.value_hash = {}
  
  def toJSON(self):
    try:
      with open(self.filename, 'w') as f:
        f.write(json.dumps(self.res, indent=4))
    except IOError as e:
      print "Couldn't write to file %s" % self.filename
      raise e

  def uploadToFirebase(self, api):
    try:
      api.upload_game(self.game_date, self.res)
    except Exception as e:
      # TODO: replace with log
      print e
      raise e

  def parseGame(self):
    for i in range(1, 3):
      r = self.soup.find(id=self.hash_num_round[i])
      if r:
        items = []
        genres = self.parseRound(r)

        for key, val in genres.iteritems():
            temp = {'genre': key, 'questions': val}
            items.append(temp)
        self.res['info']['keys'].append(i)
        self.res[i] = items
    
    # parse final jeopardy
    r = self.soup.find(id=self.hash_num_round[3])
    if r:
      items = []
      genres = self.parseFinalRound(r)

      for key, val in genres.iteritems():
        temp = {'genre': key, 'questions': val}
        items.append(temp)
      self.res['info']['keys'].append(3)
      self.res[3] = items

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
    right, wrong = None, None
    if answer.find_all("td", class_="right"):
      right = [s.get_text() for s in answer.find_all("td", class_="right")]
    if answer.find_all("td", class_="wrong"):
      wrong = [s.get_text() for s in answer.find_all("td", class_="wrong")]
      if 'Triple Stumper' in wrong:
        wrong = self.contestants.ids
              
    answer = answer.find("em").get_text()
    answerParsed = answerParser.main(answer)

    if re.search(r"^(1 of)", answer):
      answer = answer.split("&")[0]
        
    temp = Clue("single", None, question, answer, answerParsed, right, wrong)
    genres[category].append(temp.toJSON())

    return genres
  
  def createValueHash(self, _clues):
    for c in _clues:
      if c.find("table"):
        answer = BeautifulSoup(c.find("div", onmouseover=True).get("onmouseover"), "lxml")
        s = answer.find("p").get_text()
        col, row = self.getClueRowCol(s)

        if row in self.value_hash:
          continue

        if c.find("td", class_=re.compile("clue_value_daily_double")):
          continue
        else:
          value = c.find("td", class_=re.compile("clue_value"))
          value = value.get_text().split("$")[1].replace(",", "")
          self.value_hash[row] = value 

  def parseRound(self, r):
    categories = [c.get_text() for c in r.find_all("td", class_="category_name")]
    genres = defaultdict(list)

    _clues = r.find_all("td", class_="clue")
    self.createValueHash(_clues)

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
          temp = Clue("placeholder")
          genres[category].append(temp.toJSON())
          continue

        answer = BeautifulSoup(c.find("div", onmouseover=True).get("onmouseover"), "lxml")
        right, wrong = None, None
        if answer.find_all("td", class_="right"):
          right = [s.get_text() for s in answer.find_all("td", class_="right")]
        if answer.find_all("td", class_="wrong"):
          wrong = [s.get_text() for s in answer.find_all("td", class_="wrong")]
          if 'Triple Stumper' in wrong:
            wrong = self.contestants.ids
        question = question.get_text()
        s = answer.find("p").get_text()
        col, row = self.getClueRowCol(s)

        i = col
        answer = answer.find("em", class_="correct_response").get_text()
        answerParsed = answerParser.main(answer)
        category = categories[col-1]
        _id = str(col) + str(row)

        if _type is "double":
          dailyDoublePrice = value 
          value = self.value_hash[row]
          temp = Clue(_type, value, question, answer, answerParsed, right, wrong, _id, dailyDoublePrice)
        else: 
          temp = Clue(_type, value, question, answer, answerParsed, right, wrong, _id)

        genres[category].append(temp.toJSON())
      else:
        i += 1
        if i % 7 == 0: 
          i = 1
        category = categories[i-1]
        temp = Clue("placeholder")
        genres[category].append(temp.toJSON())
    self.value_hash = {}
    return genres

# with open("season_1_html/1985-01-03.html") as f:
#       data = f.read()
#       soup = BeautifulSoup(data, 'html.parser')
#       r = Round(soup, "test.json")
#       r.parseGame()