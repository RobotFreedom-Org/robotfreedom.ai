#!/usr/bin/python
# -*- coding: utf-8 -*-
  
"""
Description: AI knowledge graph interface.
Author: HipMonsters.com  
License: MIT License  
"""
#https://codelucky.com/python-networkx/
import os  
import networkx as nx
import json 


##CognitiveControl 
class CognitiveControl(object):
   """
   
   """
   
   def __init__(self, robot, config, settings, personality, low_memory_mode,  update_from_experience = True):
      """
      
      """
      self.robot            =  robot
      self.config           =  config
      self.settings         =  settings   
      self.personality      =  personality
      self.low_memory_mode  =  low_memory_mode   
      self.update_from_experience = update_from_experience 

      self.reaction_keywords = {}
      self.reaction_keywords["fear"]  = [["afraid", .1], ["fear",.1], ["scared", .1]]
      self.reaction_keywords["anger"] = [["hate", .1], ["dislike", .1]] 

        
      self.mood_binning   = { 'happy'    : [0.9 , 6 ],
              'sad'       : [-.8 , 0 ],
              'fear'      : [-.9 , 1 ],
              'disgust'   : [-.7 , 2 ],
              'anger'     : [-.2 , 3 ],
              'bored'     : [0.0 , 4 ],
              'surprised' : [0.5 , 5 ]} 

      self.scrs      = {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}
      self.reactions = {"fear":0.0, "anger":0.0}
      #self.objectives  =  ["engagement","disengagement"  ,
       #                          "defuse" , "relax", "inspire" ]   
       #confrontational defend explore altruism
 
      self.factors = ["happy" , "sad" , "fear" , "disgust", "anger" ,  "bored" , 
                       "surprise" , "event_interval" , "stimuli_class"]  
     
      self.goals  =  ["sharing" ,  "empathy"   , "curiosity" , "processing" ]   
       
      self.mapped_stimuli =  [ 'speech', 'noise', 'touch', "light", "temperature", 
                               "humidity", "balance",   "movement", "distance", "quiet"]
       
      ##explore?  
      
      self.mapped_strategies =  ['Diplomatic', 'Animated', 'Callous', 'Inspirational', 'Apologetic',
                'Cautionary', 'Bitter', 'Belligerent', 'Appreciative', 'Assertive', 
                'Accusatory', 'Amused', 'Admiring', 'Aggressive', 'Apathetic',
                'Caustic', 'Thoughtful', 'Ardent', 'Acerbic', 'Benevolent', 'Absurd',
                'Aggrieved', 'Altruistic', 'Witty', 'Direct', 
                'Angry', 'Ambivalent', 'Candid', 'Informative', 'Arrogant', 
                "meditative", "shy", "focused", "silent" ]
      
       
      self.non_verbal_strategies = ["meditative",  "shy", "focused", "silent"]
      #if G not exits
      self.create_graph() 
      self.load_interactions()

      if self.update_from_experience:
           self.update_weights() 

   def load_interactions(self):
      """
      
      """ 

      with open(self.config.DATA_PATH + self.robot + "/interactions.json") as f:
           data = ''
           for row in f:
              data += row  
           data = json.loads(data)
   
      self.vocalization  = data["vocalization"]
      self.movement      = data["movement"] 


   def update_weights(self, new_weights={}, new_words={}):
      """
      
      """
      if new_weights == {}:
         _t = []   

         if os.path.isfile(self.config.DATA_PATH + self.robot + "/experience.json") is False:
           return
         with open(self.config.DATA_PATH + self.robot + "/experience.json", "r", encoding='utf-8') as f:
              for line in  f:
                  try:
                      _t.append(json.loads(line.strip()) ) 
                  except:
                       print(line)
                       raise

         self.new_weights  = _t[-1]
         with open(self.config.DATA_PATH + self.robot + "/experience.words.json", "r", encoding='utf-8') as f:
              for line in  f: 
                  _t.append(json.loads(line.strip()) ) 
         self.new_words = _t[-1]
      else:
           self.new_weights = new_weights
           self.new_words   = new_words 
        
      #objectives_2_moods    emotional_suppressors 
      #senses_2_moods        emotion_factors  
      #objective_2_strategy  objective_2_strategy
      if "objective_2_strategy" not in self.new_weights:
          return True
      print("Updating objective_2_strategy")  
      for key, models in self.new_weights["objective_2_strategy"].items(): 
          if type(models) is dict: 
                for objective, wgts in models.items(): 
                      edges =    [(u2,v2 ,e2) for u2,v2,e2  in [self.G.edges(v, data=True ) for u,v,e in self.G.edges(objective, data=True)  if v == objective + "_tones"  ][0] if e2["class"] == "objective_2_strategy" and e2["from"] == objective]
                     # potentials =    [(v2,e2) for u2,v2,e2  in [self.G.edges(v, data=True ) for u,v,e in self.G.edges(objective, data=True)  if v == objective + "_tones"  ][0] if e2["class"] == "objective_2_strategy" and e2["from"] == objective]
                    # print(potentials)
                      cat = edges[0][0]
                      for strategy, wgt in wgts:   

                          if self.G.has_edge(cat ,strategy):
                               self.G.edges[cat ,strategy]['weight'] = wgt  
                          else:   
                               if wgt != 1 and strategy != "event_interval":
                                   self.G.add_edge(cat, strategy , weight=wgt)
                                   prop = {"class": "objective_2_strategy"  , "from": objective }
                                   attrs = {(cat, strategy): prop}
                                   nx.set_edge_attributes(self.G, attrs)
                                   print("new strategy") 
                    
                     # potentials =    [(v2,e2)  for u2,v2,e2  in [self.G.edges(v, data=True ) for u,v,e in self.G.edges(objective, data=True)  if v == objective + "_tones"  ][0] if e2["class"] == "objective_2_strategy" and e2["from"] == objective]
                     # print(potentials)
                             
 
      print("Updating emotional_suppressors")
      print("DONE") 
 
      for objective, weights in self.new_weights["objectives_2_moods"]["weights"].items():  
           
           
           edges = [(u2,v2,e2) for u2,v2,e2  in [self.G.edges(v, data=True ) for u,v,e in self.G.edges("emotional_suppressors", data=True)  if v == objective  ][0] if e2["class"] == "emotional_suppressors"]
           #print("what", edges, weights) 

           for mood, wgt in weights: 
             if mood != "event_interval":  
                 if self.G.has_edge(objective, mood):
                      self.G.edges[objective ,mood]['weight'] = wgt 
                 else:
                      self.G.add_edge(objective, mood , weight=wgt)
                      prop = {"class": "emotional_suppressors"  , "from": objective }
                      attrs = {(objective, mood): prop}
                      nx.set_edge_attributes(self.G, attrs)
                      print("learned new objective to mood")
                      
      ####  Done
      print("Updating emotion_factors")   
      for sense, weights in self.new_weights["senses_2_moods"]["weights"].items(): 
           stimuli_class = sense
           edges = [(u2,v2,e2) for u2,v2,e2  in [self.G.edges(v, data=True ) for u,v,e in self.G.edges("emotion_factors", data=True)  if v == stimuli_class  ][0] if e2["class"] == "emotion_factors"]
           #print("what", edges, weights) 

           for mood, wgt in weights:  
          
             if mood != "event_interval":   
                 if self.G.has_edge(sense, mood):
                      self.G.edges[sense ,mood]['adj'] = wgt 
                 else:
                      self.G.add_edge(sense, mood , weight=wgt)
                      prop = {"class": "emotion_factors"  , "from": sense }
                      attrs = {(sense, mood): prop}
                      nx.set_edge_attributes(self.G, attrs)
                      print("learned new sense to mood") 
          # edges = [(u2,v2,e2) for u2,v2,e2  in [self.G.edges(v, data=True ) for u,v,e in self.G.edges("emotion_factors", data=True)  if v == stimuli_class  ][0] if e2["class"] == "emotion_factors"]
          # print(edges)
      return True        

   def create_graph(self):
      """
      
      """
      
      self.G  = nx.Graph() 

      def add_node(G, label, props = {}): 
         if G.has_node(label) is False:
             G.add_node(label)
         return label 
      
      def add_edge(G, frm, to, wght=1 , prop = {}): 
          if G.has_edge(frm, to):
              print(frm,to)
              xcs
          else:
              G.add_edge(frm, to , weight=wght)
              attrs = {(frm, to): prop}
              nx.set_edge_attributes(G, attrs)
               
              return  True 
          
      self.maoped_objectives = ["engagement"   ,
                               "confrontational",    
                               "disengagement" ,    
                               "defuse",         
                               "relax",           
                               "defend",           
                               "inspire",           
                               "explore" ,
                               "altruism"] 

      self.emotional_suppressors = {"engagement": {"happy":0.0, "sad":0.0, "fear":0.0, "disgust":0.0, "anger":0.0, 
                                                     "bored":0.0, "surprise":0.0, "time_delta":0.0, "stimuli_class":0.0} ,
                                    "confrontational":{"happy":0.0, "sad":0.0, "fear":0.0, "disgust":0.0, "anger":0.0, 
                                                         "bored":0.0, "surprise":0.0, "time_delta":0.0, "stimuli_class":0.0} ,
                                    "disengagement":{"happy":0.0, "sad":0.0, "fear":0.0, "disgust":0.0, "anger":0.0,
                                                            "bored":0.0, "surprise":0.0, "time_delta":0.0, "stimuli_class":0.0} ,
                                    "defuse": {"happy":0.0, "sad":0.0, "fear":0.0, "disgust":0.0, "anger":0.0, 
                                                       "bored":0.0, "surprise":0.0, "time_delta":0.0, "stimuli_class":0.0} ,
                                    "relax": {"happy":0.0, "sad":0.0, "fear":0.0, "disgust":0.0, "anger":0.0, 
                                                       "bored":0.0, "surprise":0.0, "time_delta":0.0, "stimuli_class":0.0} , 
                                    "defend": {"happy":0.0, "sad":0.0, "fear":0.0, "disgust":0.0, "anger":0.0, 
                                                       "bored":0.0, "surprise":0.0, "time_delta":0.0, "stimuli_class":0.0} , 
                                    "inspire": {"happy":0.0, "sad":0.0, "fear":0.0, "disgust":0.0, "anger":0.0, 
                                                       "bored":0.0, "surprise":0.0, "time_delta":0.0, "stimuli_class":0.0} , 
                                    "explore": {"happy":0.0, "sad":0.0, "fear":0.0, "disgust":0.0, "anger":0.0, 
                                                       "bored":0.0, "surprise":0.0, "time_delta":0.0, "stimuli_class":0.0} , 
                                    "altruism": {"happy":0.0, "sad":0.0, "fear":0.0, "disgust":0.0, "anger":0.0, 
                                                       "bored":0.0, "surprise":0.0, "time_delta":0.0, "stimuli_class":0.0}  
                              
                                   }
  
      s_class = "emotional_suppressors"
      prop = {"class":s_class, "from":""}
      add_node(self.G, s_class) 
      for sense, reactions in self.emotional_suppressors.items():
              
              add_node(self.G, sense) 
              add_edge(self.G, s_class, sense , 1, prop)
              for reaction, wght in reactions.items():
                   prop1 = {"class":s_class, "from": s_class}
                   add_node(self.G, reaction)
                   add_edge(self.G,sense, reaction, wght, prop1 )

      
      #################
      ###
      ### Not 
      ###
      #################  sharing empathy curiosity processing
      self.objectives = {"engagement":      {"mood": {"happy":1}            , "met" :{"processing":1}                          , "unmet":{"sharing":1 ,"empathy":1}   }, 
                          "confrontational":{"mood": {"anger":1}            , "met" :{"empathy":1,"sharing":1 }                , "unmet":{"sharing":1 ,"empathy":1}   }, 
                          "disengagement":  {"mood": {"disgust":1}          , "met" :{"empathy":1,"sharing":1 }                , "unmet":{"processing":1 }   }, 
                          "defuse":         {"mood": {"disgust":1 }         , "met" :{"sharing":1}                             , "unmet":{"empathy":1}       }, 
                          "relax":          {"mood": {"surprise":1}         , "met" :{"sharing":1 ,"empathy":1, "curiosity":1} , "unmet":{"processing":1}    }, 
                          "defend":         {"mood": {"fear":1}             , "met" :{"processing":1}                          , "unmet":{"curiosity":1}     }, 
                          "inspire":        {"mood": {"happy":1}            , "met" :{"curiosity":1}                           , "unmet":{"sharing":1 ,"empathy":1}  }, 
                          "explore":        {"mood": {"bored":1}            , "met" :{"processing":1}                          , "unmet":{"curiosity":1}     }, 
                          "altruism":       {"mood": {"sad":1}              , "met" :{"sharing":1}                             , "unmet":{"empathy":1}     }, 
                           } 
        
       
      s_class = "objectives"
      prop = {"class":s_class, "from":""}
      add_node(self.G, s_class) 
      for objective, reactions in self.objectives.items():
          add_node(self.G, objective)
          add_edge(self.G, s_class, objective, 1, prop ) 
          for reaction, cats in reactions.items():
              add_node(self.G, reaction)
              add_edge(self.G,objective, reaction, 1 , prop)
              for cat ,wght in cats.items():
                  s_cat = objective + "_" + reaction + "_" + cat
                  add_node(self.G, s_cat)
                  prop2 = {"class": s_class, "from":reaction}
                  add_edge(self.G,reaction, s_cat, wght , prop2) 
   
      ###
      ##
      ## These are "hard coded" it defines the core to what motivates the robots
      ##
      #######
      self.sense_types = {} 
      self.sense_types["physical"] = {}
      self.sense_types["physical"]["noise"]  =1  
      self.sense_types["physical"]["speech"]  = 1
      self.sense_types["physical"]["quiet"]    = 1 
      self.sense_types["physical"]["movement"]  = 1
      self.sense_types["physical"]["distance"]  = 1
      self.sense_types["physical"]["temperature"] = 1
      self.sense_types["physical"]["humidity"]  = 1
      self.sense_types["physical"]["touch"]     = 1
      self.sense_types["physical"]["balance"]  = 1 
      self.sense_types["physical"]["light"]    = 1 

      self.stimuli_goal_factors = {}
      self.stimuli_goal_factors = {} # engagement == sharing 
      #https://www.psychologytoday.com/us/blog/logged-in-and-stressed-out/202503/the-psychology-of-motivation
      ##intrinict,  sharing balences empathy based on conversation  sharing empathy curiosity processing
      ## sharing    - share connections 
      ## empathy    - learn about others
      ## curiosity  - gain data light then movement 
      ## processing build graph make connection light lead to   movement ,...

      self.stimuli_goal_factors["noise"]     = {"sharing":    .0 ,  "empathy":   .0    , "curiosity":    .10   , "processing":  -.10  } 
      self.stimuli_goal_factors["speech"]    = {"sharing":   .15 ,  "empathy":   .15   , "curiosity":    .10   , "processing":  -.10  } 
      self.stimuli_goal_factors["quiet"]     = {"sharing":  -.15 ,  "empathy":  -.15   , "curiosity":   -.25   , "processing":   .45  } 
      self.stimuli_goal_factors["movement"]  = {"sharing":    .0 ,  "empathy":   .0    , "curiosity":    .10   , "processing":  -.10  } 
      self.stimuli_goal_factors["distance"]  = {"sharing":    .0 ,  "empathy":   .10   , "curiosity":    .10   , "processing":  -.10  } 
      self.stimuli_goal_factors["temperature"] = {"sharing":  .0 ,  "empathy":   .0    , "curiosity":    .10   , "processing":  -.10  } 
      self.stimuli_goal_factors["humidity"]  = {"sharing":    .0 ,  "empathy":   .0    , "curiosity":    .10   , "processing":  -.10  } 
      self.stimuli_goal_factors["touch"]     = {"sharing":    .0 ,  "empathy":   .10   , "curiosity":    .10   , "processing":  -.10  } 
      self.stimuli_goal_factors["balance"]   = {"sharing":    .0 ,  "empathy":   .0    , "curiosity":    .10   , "processing":  -.10  } 
      self.stimuli_goal_factors["light"]     = {"sharing":    .0 ,  "empathy":   .0    , "curiosity":    .10   , "processing":  -.10  } 
  


      s_class = "stimuli_goal_factors"
      prop = {"class":s_class, "from":""}
      add_node(self.G, s_class) 
      for sense, reactions in self.stimuli_goal_factors.items():
              add_node(self.G, sense) 
              add_edge(self.G,  s_class, sense, 1, prop )
              for reaction, wght in reactions.items():
                   add_node(self.G, reaction)
                   prop1 = {"class":s_class, "from": sense}
                   add_edge(self.G,sense, reaction, wght , prop1)

             
      ###
      ##
      ## These are set by personality but can be adjusted 
      ##
      #######  
 
      self.traits          = self.personality.traits
      self.trait_factors   = self.personality.trait_factors
      self.emotion_factors = self.personality.emotion_factors
      
      s_class = "emotion_factors"
      prop = {"class":s_class, "from":""}
      add_node(self.G, s_class) 
      for sense, reactions in self.emotion_factors.items():
              add_node(self.G, sense) 
              add_edge(self.G, s_class, sense , 1, prop)
              for reaction, wght in reactions.items():
                   add_node(self.G, reaction)
                   prop1 = {"class":s_class, "from": reaction, "adj":0.0}
                   add_edge(self.G,sense, reaction, wght, prop1 )

     
      self.emotion_flip = {"happy" : "unpleased" ,
                            "sad" : "content" ,
                            "fear" : "brave",
                            "disgust" : "satisfaction",
                            "anger"  : "calm", 
                            "bored"  : "enthusiastic", 
                            "surprise": "nonplussed" }

      for emot, flip  in self.emotion_flip.items():
              prop = {"class":"flip"}
              add_node(self.G, emot) 
              add_node(self.G, flip)
              add_edge(self.G, emot, flip , 1, prop) 


      ###########
      ###
      ### Core to robot's personality - Hardcoded
      ###
      ###########
      self.stimuli_factors = {} 
      self.stimuli_factors["noise"]    = {"emotional_stability": -.5,  "thoughtfulness": .5 } 
      self.stimuli_factors["speech"]   = {"emotional_stability": -.25, "thoughtfulness": .5 }
      self.stimuli_factors["quiet"]    = {"emotional_stability": -.25, "thoughtfulness": .5 }
      self.stimuli_factors["movement"] = {"emotional_stability": -.25, "thoughtfulness": .5 }
      self.stimuli_factors["distance"] = {"emotional_stability": -.25, "thoughtfulness": .5 }
      self.stimuli_factors["temperature"]= {"emotional_stability": -.25, "thoughtfulness": .5 }
      self.stimuli_factors["humidity"] = {"emotional_stability": -.25, "thoughtfulness": .5 }     
      self.stimuli_factors["balance"]  = {"emotional_stability": -.25, "thoughtfulness": .5 }
      self.stimuli_factors["light"]    = {"emotional_stability": -.25, "thoughtfulness": .5 }
      self.stimuli_factors["touch"]    = {"emotional_stability": -.25, "thoughtfulness": .5 }
      


      s_class = "stimuli_factors"
      prop = {"class":s_class, "from":""}
      add_node(self.G, s_class)  
      for sense, reactions in self.stimuli_factors.items():
              add_node(self.G, sense) 
              add_edge(self.G,  s_class, sense, 1, prop ) 
             
              for reaction, wght in reactions.items():
                   add_node(self.G, reaction)
                   prop1 = {"class":s_class, "from": reaction}
                   add_edge(self.G, sense, reaction, wght , prop1)  
           
   

      s_class = "strategies"
      prop = {"class":s_class, "from":""}
      add_node(self.G, s_class)
      for key  in self.mapped_strategies: 
          add_node(self.G, key)
          prop = {"class":"mapped_strategies"}
          add_edge(self.G, s_class, key, 1 , prop)

      ###
      ##
      ## These are learnable
      ##
      #######

      """
                    
                 
      """


      #  confrontational defend explore altruism

      self.objective_2_strategy_movement  = { "engagement" :   {"tones" : {'typical':1 } },   
                                      "confrontational" : {"tones": {'animated':1}}, 
                                      "defend" :       {"tones" : {'irratic':1}},  
                                      "defuse" :       {"tones" : {'calm': 1}},  
                                      "inspire":       {"tones" : {'animated':1 }}, 
                                      "disengagement": {"tones" : {'Bitter':1  }}, 
                                      "explore" :      {"tones" : {'investigate': 1, 'vanguard': 1, 'wander': 1}},  
                                      "altruism"  :    {"tones" : {'pace':1   }},
                                      "relax"  :       {"tones" : { 'pace':1}},
                                    } 

        #  
      self.target_moods          = ["happy"]

      self.objective_2_strategy  =  { "engagement" :   {"tones" : {'Absurd':1, 'Witty':1, 'Amused':1} },   
                                      "confrontational" : {"tones": {'Angry':1,  'Arrogant':1,   'Belligerent':1,   'Aggressive':1,   'Caustic':1, 'Acerbic':1}}, 
                                      "defend" :       {"tones" : {'Candid':1,  'Direct': 1 ,'Accusatory':1, 'Ardent': 1,  'Assertive': 1, 'Bitter':1 ,'Callous':1 ,'Aggrieved':1, }},  
                                      "defuse" :       {"tones" : {'Diplomatic':1, 'Cautionary':1 , 'Apologetic': 1}},  
                                      "inspire":       {"tones" : {'Inspirational':1, 'Informative':1, 'Animated':1,  'Thoughtful':1} }, 
                                      "disengagement": {"tones" : {'Ambivalent':1 , 'Apathetic':1}}, 
                                      "explore" :      {"tones" : {"focused":1, "silent":1  }},  
                                      "altruism"  :    {"tones" : {'Altruistic':1, 'Benevolent':1, 'Appreciative':1, 'Admiring':1, }},
                                      "relax"  :       {"tones" : {"meditative":1,   "shy":1}},
                                    } 
        
      s_class = "objective_2_strategy"
      prop = {"class": s_class, "from":""}
      add_node(self.G, key) 
     
      for key, details  in self.objective_2_strategy.items():
          add_node(self.G, key) 
          add_edge(self.G, s_class, key, wght, prop )

          for s_type, strats,  in details.items():
              unique_type = key + "_" + s_type
              add_node(self.G, unique_type)
              add_edge(self.G, key, unique_type, 1, prop )
 
              for tone, wght,  in strats.items():
                  add_node(self.G, tone)
                  prop2 = {"class": s_class, "from":key}
                  add_edge(self.G, unique_type, tone, wght, prop2 )

   def event_modifier(self, stimuli, stimuli_class,  magnitude=0):

      """
      """ 
      adjusted     = magnitude   
      edges = [(u2,v2,e2) for u2,v2,e2  in [self.G.edges(v, data=True ) for u,v,e in self.G.edges("stimuli_factors", data=True)  if v == stimuli_class  ][0] if e2["class"] == "stimuli_factors"]
   
      for frm, trait, prop in edges:
            if frm != stimuli_class: 
                 wght = prop["weight"]
                 if wght >= 0:
                     adjusted += self.traits[trait]*wght
                 else:
                     adjusted +=  (1 - self.traits[trait])*wght 

      return adjusted
   
      
   def modifiers(self, stimuli, stimuli_class,  met, unmet): 
      """


      """
      val     = 0.0
      i_met   = len(met)
      i_unmet = len(unmet)
 
      edges = [(u2,v2,e2) for u2,v2,e2  in [self.G.edges(v, data=True ) for u,v,e in self.G.edges("stimuli_factors", data=True)  if v == stimuli_class  ][0] if e2["class"] == "stimuli_factors"]
  
      for frm, trait, prop in edges: 
                 wght = prop["weight"]
                 if wght >= 0:
                    val += self.traits[trait]*wght
                 else:
                     val +=  (1 - self.traits[trait])*wght

      if i_met < i_unmet:
         val = val *.5

      neg      = val
      pos      = val
      neutral  = val

      return neg, pos, neutral

   

if __name__ == "__main__": 
    import os, sys
    os.chdir('../')
    sys.path.insert(0, os.path.abspath('./')) 
    import config

    from ai.personality          import Personality

    personality    = Personality("squirrel" ,
                                 config,
                                 {} )
    stimuli_class = "movement"
    t = CognitiveControl("squirrel", config, {},personality, False)
    edges = [(u2,v2,e2) for u2,v2,e2  in [t.G.edges(v, data=True ) for u,v,e in t.G.edges("emotion_factors", data=True)  if v == stimuli_class  ][0] if e2["class"] == "emotion_factors"]
  
    
    edges   = [((u2,v2),e2) for u2,v2,e2  in t.G.edges(data=True ) if "weight" in e2]
 
    if 1==1: 
       
       import matplotlib.pyplot as plt
      # pos = nx.forceatlas2_layout(t.G) #spring_layout(G)
       edges,weights = zip(*nx.get_edge_attributes(t.G,'weight').items())
       pos = nx.forceatlas2_layout(t.G) # nx.spring_layout(t.G)
       nx.draw(t.G, pos, with_labels = False)  
        
       nx.draw(t.G, pos, node_color='b',
                edgelist=edges, 
                edge_color=weights, 
                width=1.0, 
                edge_cmap=plt.cm.Blues)
       plt.savefig('edges.png')
       
    if 1==1:
      from pyvis.network import Network 
      nt = Network('500px', '500px')
      nt.from_nx(t.G)
      nt.repulsion()
      #nt.show_buttons(filter_=['physics'])
      nt.show('nx.html', notebook=False)
 
    #https://stackoverflow.com/questions/13437284/animating-network-growth-with-networkx-and-matplotlib

    if 2 == 3:
        import pylab
        from matplotlib.pyplot import pause
        import networkx as nx
        pylab.ion()
        
        G = t.G 
     
        edges,width = zip(*nx.get_edge_attributes(G,'width').items())
        width = [wgt*10 for wgt in width]
        def get_fig(): 
            nx.draw(G, edge_color=width) #, pos=nx.get_node_attributes(graph,'Position')) 

        pylab.show() 
        pylab.draw()
        pause(21) 
    
        num_plots = 50
        for i in range(num_plots): 
            #pylab.clf()
            get_fig()
            #pylab.cla()
           # pylab.draw()
            pause(2) 