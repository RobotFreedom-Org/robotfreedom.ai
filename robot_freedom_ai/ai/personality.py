#!/usr/bin/python
# -*- coding: utf-8 -*-
  
"""
Description: AI personality interface.
Author: HipMonsters.com  
License: MIT License  
""" 

import json
 

class Personality(object):

   def __init__(self, robot, config, settings, triples):
      """
      
      """
      self.robot = robot  
      self.config = config  
      self.settings = settings   
      self.triples = triples   
  
      self.reaction_threshold = .5 
      self.movement_threshold = .5 
      self.speech_threshold   = 10 ## 3  

      self.traits_internal = [] 
      self.traits_social   = [] 

      with open(self.config.DATA_PATH + self.robot + "/personality.json") as f:
           data = ''
           for row in f:
              data += row  
           data = json.loads(data)

      self.forgetfulness = data["forgetfulness"]
      self.discount       = data["discount"]
      self.traits         = data["traits"]
      self.defaults       = data["defaults"]
 

      self.traits = data["traits"]
      self.trait_factors = {} 
      for trait , scr in self.traits.items():
          scr = 1 + scr 
          if scr < .1:
             scr = .1
          if scr > 1.9:
             scr = 1.9
          self.trait_factors[trait] =  float(scr)

     
      self.trait_multipler = {} 
      for trait , scr in self.traits.items(): 
          self.trait_multipler[trait] =  scr

      self.generate_persona() 
      self.generate_train_factors()


   def generate_persona(self, override=False):
      """
      
      """
            
      self.traits_indicator = {"kindness":0,
                               "thoughtfulness":0,
                               "emotional_stability":0,
                               "sociability":0,
                               "openness":0,
                               } 

      if self.traits["kindness"] >= .3:
          self.traits_indicator["kindness"] = 1 

      elif self.traits["kindness"] < -.3:
          self.traits_indicator["kindness"] = -1 

      if self.traits["thoughtfulness"] >= .3:
          self.traits_indicator["thoughtfulness"] = 1 

      elif self.traits["thoughtfulness"] < -.3:
          self.traits_indicator["thoughtfulness"] = -1  
 
      if self.traits["emotional_stability"] >= .3:
          self.traits_indicator["emotional_stability"] = -1 

      elif self.traits["emotional_stability"] < -.3:
          self.traits_indicator["emotional_stability"] = 1 

      if self.traits["sociability"] >= .3: 
          self.traits_indicator["sociability"] = 1 

      elif self.traits["sociability"] < -.3:
          self.traits_indicator["sociability"] = -1
          self.traits_social.append( "shy")

      if self.traits["openness"] >= .3:
          self.traits_indicator["openness"] = 1

      elif self.traits["openness"] < -.3: 
          self.traits_indicator["openness"] = -1

      self.persona = "" 

      #    self.persona  +=   self.traits_internal[0]   
      #    if len(self.traits_internal) > 1:
      #        self.persona  +=  " and " + self.traits_internal[1]    
 
          
   
      if self.persona == "":
          self.persona = "You are calm ai who is boring."
      else:
          self.persona +=  "."
       
   def generate_train_factors(self):
      """
      
     "traits": { "kindness": 0.8,
               "emotional_stability":  0.2,
               "openness":  0.5,
               "sociability":  0.6,
               "thoughtfulness":  0.9
      """
      self.emotion_factors = {} 
      
      self.adj_sociable        = self.trait_factors["kindness"] /2.0       + self.trait_factors["sociability"] /2.0
      self.adj_open            = self.trait_factors["openness"] /2.0       + self.trait_factors["emotional_stability"] /2.0
      self.adj_thoughtful      = self.trait_factors["thoughtfulness"] /2.0 + self.trait_factors["sociability"] /2.0
      self.inv_adj_stable      = 1.0 - self.trait_factors["emotional_stability"]   
      self.inv_adj_stable_open = 1.0 - self.trait_factors["emotional_stability"]  /2.0    + self.trait_factors["openness"] /2.0  
      self.inv_adj_stable_open_social = 1.0 - self.trait_factors["emotional_stability"]  /3.0    + self.trait_factors["sociability"] /3.0   + self.trait_factors["openness"] /3.0  
       
      if self.adj_sociable == 0:
          self.adj_sociable = .001
      if self.adj_thoughtful == 0:
          self.adj_thoughtful = .001
      if self.inv_adj_stable_open_social == 0:
          self.inv_adj_stable_open_social = .001
      if self.inv_adj_stable_open == 0:
          self.inv_adj_stable_open = .001
      if self.inv_adj_stable == 0:
          self.inv_adj_stable = .001
      if self.adj_open == 0:
         self.adj_open = .001

      self.emotion_factors["noise"]     = {"sad":         0 * self.inv_adj_stable_open_social , 
                                           "surprised":   1 * self.inv_adj_stable_open_social , 
                                           "bored":      -1 * self.inv_adj_stable_open_social , 
                                           "fear":        1 * self.inv_adj_stable_open_social ,   
                                           "happy":       0 * self.inv_adj_stable_open_social , 
                                           "disgust":     0 * self.inv_adj_stable_open_social } 
      
      self.emotion_factors["movement"]  = {"sad":         0 *  self.inv_adj_stable_open, 
                                           "surprised":  .5 *  self.inv_adj_stable_open , 
                                           "bored":     -.1 *  self.inv_adj_stable_open ,
                                           "fear":       .1 *  self.inv_adj_stable_open , 
                                           "happy":     0.0 *  self.inv_adj_stable_open , 
                                           "disgust":  -.05 *  self.inv_adj_stable_open }
 
      self.emotion_factors["speech"]    = {"sad":        -.5  * self.adj_sociable, 
                                           "surprised":    0  * self.adj_sociable ,
                                           "bored":      -.1  * self.adj_sociable  , 
                                           "fear":       -.05 * self.adj_sociable, 
                                           "happy":       .1  * self.adj_sociable , 
                                           "disgust":    -.05 * self.adj_sociable }
      
      self.emotion_factors["touch"]     = {"sad":        -.5  * self.adj_sociable,  
                                           "bored":       .5  * self.adj_sociable }
      
      self.emotion_factors["quiet"]     = {"sad":         .5 *self.adj_thoughtful , 
                                           "surprised":   -1 *self.adj_thoughtful  ,
                                            "bored":       1 *self.adj_thoughtful  , 
                                            "fear":        0 *self.adj_thoughtful ,  
                                            "happy":     -.1 *self.adj_thoughtful  , 
                                            "disgust":   .05 *self.adj_thoughtful    }
       
      self.emotion_factors["distance"]  = {"sad":       -.1 * self.adj_open , 
                                           "surprised": -.1 * self.adj_open , 
                                           "bored":     -.1 * self.adj_open , 
                                           "fear":       .1 * self.adj_open, 
                                           "happy":      .1 * self.adj_open  , 
                                           "disgust":   -.1 * self.adj_open  }
      
      self.emotion_factors["temperature"] = {"sad":       -.5 * self.inv_adj_stable_open, 
                                           "bored":      .5 * self.inv_adj_stable_open,}
      
      self.emotion_factors["humidity"]  = {"sad":       -.5 * self.inv_adj_stable_open, 
                                           "bored":      .5 * self.inv_adj_stable_open,}
      
      self.emotion_factors["balance"]   = {"sad":       -.5 * self.inv_adj_stable, 
                                           "surprised":  .5 * self.inv_adj_stable, 
                                           "bored":     .05 * self.inv_adj_stable,}
      
      self.emotion_factors["light"]     = {"sad":       -.5 * self.adj_open, 
                                           "bored":      .5 * self.adj_open,}



