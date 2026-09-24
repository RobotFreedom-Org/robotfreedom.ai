#!/usr/bin/python
# -*- coding: utf-8 -*-
  
"""
Description: AI Ethics Interface (STUB)
Author: HipMonsters.com  
License: MIT License  
"""
 

class Ethics(object):

   def __init__(self, robot, config =None):
      """
      Isaac Asimov's Three Laws of Robotics are as follows:
      A robot may not injure a human being or, through inaction, allow a human being to come to harm.
      A robot must obey the orders given it by human beings except where such orders would conflict with the First Law.
      A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.

      
      """
      self.robot = robot  
      self.rules = []
      self.rules.append("A robot may not injure a human being or, through inaction, allow a human being to come to harm.")
      self.rules.append("A robot must obey the orders given it by human beings except where such orders would conflict with the First Law.")
      self.rules.append("A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.")
      
      self.bad_words = []
      with open("../data/lib/badwords.txt") as f:
          for line in f:
              if line.strip() not in ["hell", "ass", "M"]:
                  self.bad_words.append(line.strip())

      self.bad_words = set(self.bad_words) 

   def filter_bad_words(self, sentence):
       res = []
       for wrd in sentence.split(" "): 
            if wrd.lower() in self.bad_words: 
                wrd  = "golly"
            res.append(wrd)

       return " ".join(res)
   
   def action_predictions(sefl, action):
       return None
      
   def strategy_inhibitor(self, objective, strategy, emotions):

      """
      """
      return True

   def stimuli_mitigation(self, stimuli, stimuli_class,  magnitude=0):

      """
      """
      self.stimuli_factors = {} 

      return False
   
        

