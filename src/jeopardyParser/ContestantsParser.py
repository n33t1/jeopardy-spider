#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as soup
import re
import json

class ContestantsParser:
    """Parser for contestants info.

    Args:
        game(bs4 object): bs4 object for current game.

    Attributes:
		ids (list): Unique ids for contests for current game. Is player's firstname+lastname. 
		Say if player is Jane Doe, the unique id for her will be janedoe. 
		info (list): A list containing player info in the format of {"player_id": player_id,
		"player_info": player_info}. Player id is player's firstname+lastname and player_info 
		is the brief description for the player. 

    """

    def __init__(self, game):
        self.ids = []
        self.game = game
        self.info = self.findContestants()

    def findContestants(self):
        res = []
        contestants = self.game.find_all("p", class_="contestants")
        for c in contestants:
            player_name = c.find("a").get_text()
            player_id = player_name.split(" ")[0]
            self.ids.append(player_id)
            player_info = c.get_text()
            res.append({"player_id": player_id, "player_info": player_info})
        return res
