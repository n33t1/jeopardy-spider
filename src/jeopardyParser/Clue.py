#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

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
		clue = {'Jtype': self.Jtype}
		if self.Jtype == "placeholder":
			return clue
		
		clue.update({'price': self.price, 'prompt': self.prompt, 'solution': self.solution,
                    'parsed_soultion': self.parsed_soultion, 'right': self.right, 'wrong': self.wrong, 'id': self.id})
		
		if self.Jtype == "single":
			return clue
        
		# Jtype is "double"
		clue.update({'dailyDoublePrice': self.dailyDoublePrice})
		return clue
