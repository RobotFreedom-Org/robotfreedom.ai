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
                personality ,    low_memory_mode ):
      """
      
      """
      self.robot        = robot   
      self.config       = config
      self.personality = personality
      self.discount    = personality.discount
      self.novelty     = 1 - self.discount 
      self.motivations  =  motivations 

      self.low_memory_mode   = low_memory_mode 
      self.sia = SentimentIntensityAnalyzer() 
      
      self.cognitive_control  = cognitive_control
      self.G          = cognitive_control.G
      self.objectives = cognitive_control.objectives
      self.scrs       = cognitive_control.scrs
      self.f_scr      = 0 
      self.debug      = False

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
       print("scrs", self.scrs)
       if self.scrs["pos"] > self.scrs["neg"]:
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

       edges = [(u2,v2,e2) for u2,v2,e2  in [self.G.edges(v, data=True ) for u,v,e in self.G.edges("objectives", data=True) ][0] if e2["class"] == "objectives" and v2 != "objectives"]
    
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
       if self.debug:
           print(self.motivations)
           print(met)
           print(unmet)
           print(mood)
           print(sorted_scores)
  
       self.current_object = objective     

       return objective

       
   
   def goal_achievement(self, stimuli, stimuli_class, signal,  amplitude, adjusted, stimuli_datetime, epoch):
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
          adjusted  = 1

      for key, val in self.motivations.items():
          self.motivations[key] = val * self.discount 

 
      edges = [(u2,v2,e2) for u2,v2,e2  in [self.G.edges(v, data=True ) for u,v,e in self.G.edges("stimuli_goal_factors", data=True)  if v == stimuli_class  ][0] if e2["class"] == "stimuli_goal_factors"]
      if self.debug:
          print(edges)
      
      for frm, goal, prop in edges: 
            
            if goal != 'stimuli_goal_factors': 
               wght = prop["weight"] *5

               if self.debug:
                 #  print("novelty  " , self.novelty )
                 #  print("adjusted " , adjusted )
                #   print("f_scr    " , self.f_scr ) 
                   print("wght     " , wght )
               #    print("[goal]   " , self.motivations[goal]  )
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
