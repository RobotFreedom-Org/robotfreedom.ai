#!/usr/bin/python
# -*- coding: utf-8 -*-
  
"""
Description: AI motivation interface.
Author: HipMonsters.com  
License: MIT License  
""" 
import json  
from nltk.sentiment import SentimentIntensityAnalyzer  

class Motivations(object):

   def __init__(self, robot,config, cognitive_control, motivations, 
                personality , lt_memory, triples,  low_memory_mode ):
      """
      
      """
      self.robot        = robot   
      self.config       = config
      self.personality  = personality
      self.discount     = personality.discount
      self.novelty      = 1 - self.discount 
      self.motivations  = motivations 
      self.lt_memory    = lt_memory
      self.triples      = triples

      self.low_memory_mode   = low_memory_mode 
      self.sia = SentimentIntensityAnalyzer() 
      
      self.cognitive_control  = cognitive_control
      self.episodic_memory    = cognitive_control.episodic_memory
      self.objectives         = cognitive_control.objectives
      self.scrs               = cognitive_control.scrs
      self.f_scr              = 0 
      self.debug              =  False

      with open(self.config.DATA_PATH + self.robot + "/priorities.json") as f:
           data = ''
           for row in f:
              data += row  
           data = json.loads(data)

      self.priorities    = data["priorities"]
      self.current_object = "engagement"
    
 
   def check_status(self):
      """
      """

      unmet  = []
      met    = []
      for key, val in self.motivations.items():
         if val < 0:
            unmet.append(key)
         elif val > 0:
            met.append(key)

      return [met, unmet]
   
   def analyze_resp(self, resp):
       """
         {'neg': 0.0, 'neu': 0.266, 'pos': 0.734, 'compound': 0.8516}
         should be with sentences.
       """ 
       self.scrs = self.sia.polarity_scores(resp) 
        
       if (self.scrs["neu"] > self.scrs["pos"])  and (self.scrs["neu"] > self.scrs["neg"]):
            temp_scr = 0
           
       elif self.scrs["pos"] > self.scrs["neg"]:
            temp_scr = self.scrs["pos"] 
       else:
            temp_scr =  -1 * self.scrs["neg"] 

       if temp_scr == 0:
          self.f_scr =  .1
       else: 
          self.f_scr =  temp_scr

   def analyze_stimuli(self, stimuli, stimuli_history):
       """
         {'neg': 0.0, 'neu': 0.266, 'pos': 0.734, 'compound': 0.8516}
         should be with sentences.
       """   
       #  _pos = moods["happy"]
       #  _neu = moods["bored"]
       #  _neg = moods["sad"] + moods["anger"] + moods["disgust"] 

       ##do grph databse. 
       stimuli_history     =  [v["stimuli_class"] for v in stimuli_history] 
       resp =  stimuli_history[4:] + [stimuli]  

       _scrs     = self.lt_memory.stimuli_resp(resp)  
 
       self.scrs = _scrs[0]  


       if (self.scrs["neu"] > self.scrs["pos"])  and (self.scrs["neu"] > self.scrs["neg"]):
            temp_scr = 0
       #    xzx xzz
      # need ot have objects and strageties change more often
       elif self.scrs["pos"] > self.scrs["neg"]:
            temp_scr = self.scrs["pos"] 
       else:
            temp_scr =  -1 * self.scrs["neg"] 

       if temp_scr == 0:
          self.f_scr =  .1
       else: 
          self.f_scr =  temp_scr
   
   def objective(self, met, unmet, indif , mood ):
       """ 
       Objective 
       {"engagement": [-1 ,.5], "novelty": [-1, .05] , "acquisition" : [-1, .5],
         "creating" : [-1, .25],  "processing": [1, .25] , "empathy" :[-1,.5]} 
      
       """ 
       objective = "engagement"
       p_iunmet = 0
       p_met    = 0

      # edges = self.episodic_memory.related( objective, "objectives", None , return_data = True) 
 
       scores = {}
       for key, val in self.objectives.items(): 
           
           factor  = 1.0

           if mood == "happy": 
               if key == self.current_object:
                    factor = 2

           scores[key] = 0.0
            
           iunmet = len([1 for v in unmet  if v in val["unmet"]])
           imet   = len([1 for v in met    if v in val["met"]])
           imood  = len([1 for v in val["mood"] if v == mood])  
           scores[key] = (1*iunmet + .8*imet + .5*imood)*factor

       sorted_scores =  sorted(scores.items(), key=lambda item: item[1],reverse=True)
       objective = sorted_scores[0][0] 
  
       self.current_object = objective     

       return objective, scores
   
   def stimuli_goal_factors(self, stimuli_class):
        
        edges = self.episodic_memory.related( stimuli_class, "stimuli_goal_factors", None , return_data = True) 
        return [[e["s"], e["o"], e["data"] ] for e, scr, v in edges]
 
   def goal_achievement(self, stimuli, stimuli_class,stimuli_history, signal,  amplitude, adjusted, stimuli_datetime, epoch):
      """
      """
       
      self.scrs  = {}

      reaction = {}
      reaction["sentiment"] = 0.0

      if stimuli_class in ["ext-speech", "speech"]  :  
          self.analyze_resp(signal)   
          adjusted  = self.f_scr   
          reaction["sentiment"] = self.f_scr   
          for key, wrds in self.cognitive_control.reaction_keywords.items():
               reaction[key] = sum([v for k, v in wrds if k in signal])
      else:
          self.analyze_stimuli(stimuli_class, stimuli_history) 
          adjusted  = self.f_scr   
          reaction["sentiment"] = self.f_scr  
 
      for key, val in self.motivations.items():
          self.motivations[key] = val * self.discount

      edges = self.episodic_memory.related( stimuli_class, "stimuli_goal_factors", None , return_data = True) 
      edges =  [[e["s"], e["o"], e["data"] ] for e, scr, v in edges]
 
      if edges == None:
          t = open("do_graph_edges.error.log", "a")
          t.write(stimuli_class + "\n")  

      if len(edges) == 0:
          t = open("do_graph_edges.error.log", "a")
          t.write(stimuli_class + "\n")   
 
 
      if self.debug:
          print(edges)
      
      for frm, goal, prop in edges: 
                
               wght = prop["weight"] * 5

               if self.debug: 
                   print("wght     " , wght ) 
                   print("tot      " , adjusted*wght*self.novelty*amplitude  )

               adj = adjusted*wght*self.novelty 

               if self.motivations[goal] == 0:
                   if adj > 0:
                        self.motivations[goal] =  adj
               else:
                   wght = adj #self.motivations[goal] * adj 
                  
                   tot  = self.motivations[goal]  + wght
                   if tot < 0:
                        self.motivations[goal] =  0 
                   elif tot > 1:
                        self.motivations[goal] =  1.0 
                   else: 
                       self.motivations[goal] =  tot
 

               if self.debug:
                   print(goal, self.motivations[goal], wght, adjusted*wght*self.novelty )
                 
                   
      for key, val in self.motivations.items():
          if self.debug:
              print(key, val)
          self.motivations[goal] = round(val,5)

          if self.motivations[goal] > 1:
              self.motivations[goal] = 1.0
          if self.motivations[goal] < .5:
              self.motivations[goal] = 0
  
      unmet   = []
      met     = []
      indif   = [] 

      for goal, val in self.motivations.items():
         
         if goal not in ["epoch", "stimuli_time", "dt",
                         "SentimentAnalyzerScr", "SentimentAnalyzer",  "creating" ]: 
             if val <= .25:
                unmet.append(goal)

             elif val >= .5:
                met.append(goal)

             else:
                indif.append(goal)  
 
      return [met, unmet, indif, self.f_scr, self.scrs, reaction]
