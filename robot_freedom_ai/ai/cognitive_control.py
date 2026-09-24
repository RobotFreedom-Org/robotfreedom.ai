#!/usr/bin/python
# -*- coding: utf-8 -*-
  
"""
Description: AI knowledge graph interface.
Author: HipMonsters.com  
License: MIT License  
""" 
import os   
#import numpy as np
import json   

class CognitiveControl(object):
   """
   
   """
   
   def __init__(self, robot, config, settings, personality, triples, low_memory_mode,  update_from_experience = True):
      """
      
      """ 
      self.robot            =  robot
      self.config           =  config
      self.triples          =  triples
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

      #intergate
      self.interaction_goals =[""] 
      #name, interests,age,.. with action
      def update_stm(stm, ent, prop, value):
          if ent not in stm:
              stm[ent] = {}
          stm[ent][prop] = value

      def retrieve_stm(stm, ent, prop):
          if ent not in stm:
              return "NA"
          if prop not in stm[ent]:
              return "NA"
          return stm[ent][prop] 
      """     
      self.interaction_sub_goals = {"user:name": update_stm("current_user", "name", "?"),
                                    "user:interest": update_stm("current_user", "interest", "?"),
                                    "user:age": update_stm("current_user", "age", "?"),
                                    }  
      """
      
      self.interaction_stragies =[""]

      """  

DESCRIPTION = [
    "**Extraversion**: outgoing, energetic, talkative, active, assertive, etc.",
    "**Neuroticism**: worrying, self-pitying, unstable, tense, anxious, etc.",
    "**Agreeableness**: sympathetic, forgiving, generous, kind, appreciative, etc.",
    "**Conscientiousness**: responsible, organized, reliable, efficient, planful, etc.",
    "**Openness**: artistic, curious, imaginative, insightful, original, wide interests, etc.",
]

     "Apologetic", 'Aggrieved' , 'Bitter' ,   'Angry' ,  'Accusatory',  'Aggressive' 
     https://www.simplypsychology.org/big-five-personality.html
      """  
      self.traits_2_strategies = {
       "sociability":        {1:['Animated' , "Inspirational", 'Assertive', 'Angry' ],               
                              0:["Candid","Direct" ],
                             -1:[ "Apologetic" ]},
       "emotional_stability": {1:['Cautionary', "Apologetic", 'Aggressive'],              
                              0:[ "Candid","Direct" ],
                             -1:['Arrogant','Angry' ,]},
       "thoughtfulness":     {1:["Benevolent", "Admiring", "Diplomatic", 'Appreciative'], 
                              0:[ "Candid","Direct" ],
                             -1:['Callous','Caustic','Belligerent', 'Accusatory','Acerbic' ]},
       "kindness":          {1:["Altruistic", "Apologetic", 'Informative'],              
                              0:[  "Candid","Direct" ],
                             -1:['Apathetic','Aggrieved'] },
       "openness":          {1:["Absurd" , "Amused" , 'Thoughtful', 'Witty'],              
                              0:[ "Candid","Direct" ],
                             -1:["Ardent" , 'Bitter']}
       }  
    
      self.non_verbal_strategies = ["meditative", "fidgety", "shy","restless","sleeping",
                                    "thoughtful" "focused", "silent", "daydreaming"]
      self.traits_2_non_verbal_strategies = {
       "sociability":        {1:["fidgety" ],               
                              0:["sleeping" ],
                             -1:["shy" ]},
       "emotional_stability": {1:["shy" ],              
                                0:["silent" ],
                               -1:["restless" ]},
       "thoughtfulness":     {1:["daydreaming"], 
                              0:["focused" ],
                             -1:["silent" ]},
       "kindness":          {1:["meditative" ],              
                              0:["focused",  ],
                             -1:["restless" ]},
       "openness":          {1:["fidgety"],              
                              0:["silent"],
                             -1:["shy" ]}
       }  
      self.mapped_strategies =  [ 
                       'Animated',    'Callous' ,    'Cautionary' ,  'Bitter' , 
                       'Belligerent', 'Appreciative','Assertive' ,   'Accusatory' ,  
                       'Aggressive',  'Apathetic' ,  'Caustic' ,  'Thoughtful' , 
                       'Acerbic',     'Aggrieved' ,  'Witty' ,  'Direct' ,
                       'Angry',       'Informative', 'Arrogant' ,  "Apologetic" ,
                       "Amused" ,     "Ardent" ,     "Inspirational" ,     "Ambivalent" ,
                       "Altruistic",  "Benevolent",  "Candid"  ,  "Diplomatic" ,
                       "Admiring",    "Absurd",      
                       "meditative", "fidgety", "shy","restless","sleeping",
                       "thoughtful" "focused", "silent", "daydreaming"]
      
        
      self.create_graph() 
      self.load_interactions() 

      if self.update_from_experience:
           self.update_weights() 

   def load_interactions(self):
      """
      
      """ 
      #replace with cosinr sim
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

         self.new_weights  = _t[-1]
         with open(self.config.DATA_PATH + self.robot + "/experience.words.json", "r", encoding='utf-8') as f:
              for line in  f: 
                  try:
                     _t.append(json.loads(line.strip()) ) 
                  except:
                       print(line) 
                       
         self.new_words = _t[-1]
      else:
           self.new_weights = new_weights
           self.new_words   = new_words 
          
      print("Updating objective_2_strategy")   

      for key, models in self.new_weights["objective_2_strategy"].items(): 
          if type(models) is dict: 
                for objective, wgts in models.items():  
                      print(type(objective), objective)
                      edges = self.episodic_memory.related( objective, "objective_2_strategy", None , return_data = True)  
                      cat = edges[0][0]["o"]  
                     # links =  self.episodic_memory.related(objective,   cat, None)   
                      for strategy, wgt in wgts:   
                          
                          strategy  = str(strategy)
                          #if type(strategy) == np.str_:
                          #. strategy = strategy.tostring()  
                          trple_id = self.episodic_memory.triple_id(objective, cat, strategy)

                          if trple_id in self.episodic_memory.triple_data:
                               self.episodic_memory.triple_data[trple_id]['abs_weight'] = abs(wgt) 
                               self.episodic_memory.triple_data[trple_id]['weight'] = wgt   
                          else:   
                               prop1 = {"class":"objective_2_strategy", "from": "mood", "weight":wgt, "abs_weight": abs(wgt) }
                               self.episodic_memory.add(objective, cat, strategy, prop1 )  
                               print("new strategy", strategy) 
                         
 
      print("Updating emotional_suppressors")
      print("DONE")  
      for objective, weights in self.new_weights["objectives_2_moods"]["weights"].items():   
           
           edges = self.episodic_memory.related( objective, "emotional_suppressors", None , return_data = True)    
           for mood, wgt in weights: 
             if mood != "event_interval":   
                 trple_id = self.episodic_memory.triple_id(objective, "emotional_suppressors", mood)

                 if trple_id in self.episodic_memory.triple_data:
                       self.episodic_memory.triple_data[trple_id]['abs_weight'] = abs(wgt) 
                       self.episodic_memory.triple_data[trple_id]['weight'] = wgt   
                 else:  
                       prop1 = {"class":"emotional_suppressors", "from": "mood", "weight":wgt, "abs_weight": abs(wgt) }
                       self.episodic_memory.add(objective, "emotional_suppressors", mood, prop1 )  
                       print("learned new objective to mood", objective, cat, mood) 
                
      ####  Done
      print("Updating emotion_factors")   
      for sense, weights in self.new_weights["senses_2_moods"]["weights"].items(): 
           stimuli_class = sense

           edges = self.episodic_memory.related( stimuli_class, "emotion_factors", None , return_data = True)    
           for mood, wgt in weights:  
          
             if mood != "event_interval":   
                 trple_id = self.episodic_memory.triple_id(stimuli_class, "emotion_factors", mood)
                 
                 if trple_id in self.episodic_memory.triple_data:
                       self.episodic_memory.triple_data[trple_id]['abs_weight'] = abs(wgt) 
                       self.episodic_memory.triple_data[trple_id]['weight'] = wgt   
                 else:
                      prop1 = {"class":"emotion_factors", "from": "mood", "weight":wgt, "abs_weight": abs(wgt) }
                      self.episodic_memory.add(stimuli_class, "emotion_factors", mood, prop1 )   
                      print("learned new sense to mood",stimuli_class,  mood, prop1) 
     
      return True        

   def create_graph(self):
      """
      
      """
      
      self.episodic_memory  = self.triples.TrplGraph()
 
          
      self.maoped_objectives = ["engagement"   ,
                               "confrontational",    
                               "disengagement" ,    
                               "defuse",         
                               "relax",           
                               "defend",           
                               "inspire",           
                               "explore" ,
                               "altruism"] 
      
      self.Conversation_Motives = {
              "TO_INFORM"    : {"description":"inform"} ,
              "TO_EDUCATE"   : {"description":"educate"} ,
              "TO_MOTIVATE"  : {"description":"motivate"} ,
              "TO_RELATE"    : {"description":"relate"} ,
              "TO_PROMOTE"   : {"description":"promote"} ,
              "TO_ENTERTAIN" : {"description":"entertain"} ,
              }
      
      self.priminary_data_structures = {"new_user": {"": ["user","name"], 
                                                     "": ["user","location"],
                                                     "": ["user","school"],
                                                     "": ["user","schcolorool"],
                                                     },
                                         "new_idea":{
                                             
                                         }
                                        
                                        
                                        }
      
      #self.objective_to_situation   = {}
      
      self.objective_description   =   {"engagement":  "You want to encourage the conversation forward.", 
                               "confrontational": "You want to keep everyone calm.", 
                               "disengagement":  "You are trying to get someone to relax." , 
                               "defuse": "You are helping a friend calm down." , 
                               "relax" : "You want to keep everyone calm.", 
                               "defend": "You are defending youself." , 
                               "inspire" :  "You want to inspire people.",  
                               "explore": "You are trying to learn new things." , 
                               "altruism": "You are helping a friend with a problem." , 
                               "quiet":  "You are trying to get someone to be quiet." ,
                               "*":        "You are trying to get someone to relax."  } 

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
      for sense, reactions in self.emotional_suppressors.items(): 
              for reaction, wght in reactions.items():
                   prop1 = {"class":s_class, "from": s_class, "weight":wght}
                   self.episodic_memory.add(sense, s_class, reaction, prop1 ) 

       
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
      for objective, reactions in self.objectives.items(): 
          for reaction, cats in reactions.items():  

              id = self.episodic_memory.get_id()
              prop = {"class":s_class, "linked_id":id, "weight":1} 
              self.episodic_memory.add(objective ,s_class , reaction, prop1 )  

              for cat , wght in cats.items(): 

                  prop = {"class":s_class, "linked_id":id, "weight":wght} 
                  self.episodic_memory.add(objective ,reaction , cat, prop1 )  
   
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
      for sense, reactions in self.stimuli_goal_factors.items(): 
              for reaction, wght in reactions.items():  
                   prop1 = {"class":s_class, "from": sense, "weight":wght}
                   self.episodic_memory.add(sense, s_class, reaction, prop1 )  
             
      ###
      ##
      ## These are set by personality but can be adjusted 
      ##
      #######  
 
      self.traits          = self.personality.traits
      self.trait_factors   = self.personality.trait_factors

      self.emotion_factors = self.personality.emotion_factors

      """ 
      s_class = "traits_factors"
      prop = {"class":s_class, "from":""} 
      print(self.trait_factors)
 
      for trait, reactions in self.trait_factors.items(): 
              
              for reaction, wght in reactions.items(): 
                   prop1 = {"class":s_class, "from": reaction, "adj":0.0, "weight":1}  
                   self.episodic_memory.add(sense, s_class, reaction, prop1 )  
      """

      
      s_class = "emotion_factors"
      prop = {"class":s_class, "from":""} 
      for sense, reactions in self.emotion_factors.items(): 
              for reaction, wght in reactions.items(): 
                   prop1 = {"class":s_class, "from": reaction, "adj":0.0, "weight":1}  
                   self.episodic_memory.add(sense, s_class, reaction, prop1 )  

     
      self.emotion_flip = {"happy" : "unpleased" ,
                            "sad" : "content" ,
                            "fear" : "brave",
                            "disgust" : "satisfaction",
                            "anger"  : "calm", 
                            "bored"  : "enthusiastic", 
                            "surprise": "nonplussed" }

      for emot, flip  in self.emotion_flip.items():
              prop = {"class":"flip"} 
              self.episodic_memory.add(emot, "opposite of", flip, prop1 )  
              self.episodic_memory.add(flip, "opposite of", emot, prop1 )   

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
      for sense, reactions in self.stimuli_factors.items():  
              for reaction, wght in reactions.items(): 
                   prop1 = {"class":s_class, "from": reaction, "weight":wght}  
                   self.episodic_memory.add(sense, s_class, reaction, prop1 )  
            
      s_class = "strategies" 
      for key  in self.mapped_strategies:  
          prop = {"class":"mapped_strategies", "weight":1}  
          self.episodic_memory.add(key, "mapped", "strategy", prop1 )  

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
                                      "confrontational": {"tones": {'Angry':1,  'Arrogant':1,   'Belligerent':1,   'Aggressive':1,   'Caustic':1, 'Acerbic':1}}, 
                                      "defend" :       {"tones" : {'Candid':1,  'Direct': 1 ,'Accusatory':1, 'Ardent': 1,  'Assertive': 1, 'Bitter':1 ,'Callous':1 ,'Aggrieved':1, }},  
                                      "defuse" :       {"tones" : {'Diplomatic':1, 'Cautionary':1 , 'Apologetic': 1}},  
                                      "inspire":       {"tones" : {'Inspirational':1, 'Informative':1, 'Animated':1,  'Thoughtful':1} }, 
                                      "disengagement": {"tones" : {'Ambivalent':1 , 'Apathetic':1}}, 
                                      "explore" :      {"tones" : {"focused":1, "silent":1  }},  
                                      "altruism"  :    {"tones" : {'Altruistic':1, 'Benevolent':1, 'Appreciative':1, 'Admiring':1, }},
                                      "relax"  :       {"tones" : {"meditative":1,   "shy":1}},
                                    } 
      
      self.objective_2_traits =  { "engagement" :   {"traits" :  ["sociability","kindness"] },   
                                      "confrontational":{"traits":  ["thoughtfulness"] }, 
                                      "defend" :       {"traits" :  ["emotional_stability"] },  
                                      "defuse" :       {"traits" :  ["openness"] },  
                                      "inspire":       {"traits" :  ["sociability"] }, 
                                      "disengagement": {"traits" :  ["kindness"] }, 
                                      "explore" :      {"traits" :  ["emotional_stability"] },  
                                      "altruism"  :    {"traits" :  ["thoughtfulness"]},
                                      "relax"  :       {"traits" :  ["openness"] },
                                    }   
    
      self.non_verbal_strategies_wgt = {}
      for trait , details in self.traits_2_non_verbal_strategies.items(): 
         strats = details[self.personality.traits_indicator[trait]]
         for strat in strats:
             if strat in self.non_verbal_strategies_wgt:
                 self.non_verbal_strategies_wgt[strat] = self.non_verbal_strategies_wgt[strat]  + 1 
             else:
                 self.non_verbal_strategies_wgt[strat] =  1  
       
      self.objective_2_strategy = {} 
      for key , traits in self.objective_2_traits.items():
         trait = traits["traits"][0] 
         tones = self.traits_2_strategies[trait][self.personality.traits_indicator[trait]]
         self.objective_2_strategy[key]  = {}
         self.objective_2_strategy[key]["tones"] = {tone: 1 for tone in tones}
        
      """
     "sociability":    "emotional_stability" "thoughtfulness":     "kindness":   "openness":    
     ["extraversion","agreeableness"] }
["conscientiousness"] }, 
["neuroticism"] },  
["openness"] },  
["extraversion"] }, 
["agreeableness"] }, 
["neuroticism"] },  
["conscientiousness"]},
["openness"] },      
                     
     """
      s_class = "objective_2_strategy"
      prop = {"class": s_class, "from":""} 
     
      for key, details  in self.objective_2_strategy.items():  
          for s_type, strats,  in details.items(): 
 
              id = self.episodic_memory.get_id()
              prop1 = {"class":s_class, "linked_id":id, "weight":1}  
              self.episodic_memory.add(key, s_class, s_type, prop1 )   
 
              for tone, wght,  in strats.items():  
                  self.episodic_memory.add(key, s_type, tone, prop1 )     


   def event_modifier(self, stimuli, stimuli_class,  magnitude=0):

      """
      """ 
      adjusted     = magnitude   
      """  
      try: 
          edges = self.episodic_memory.related( stimuli_class, "traits_factors", None , return_data = True) 
         # edges = self.episodic_memory.related( stimuli_class, "emotion_factors", None , return_data = True) 
          #print(edges)
          edges =  [[e["s"], e["o"], e["data"] ] for e, scr, v in edges] 
          print(edges)
          for frm, trait, prop in edges: 
                 wght = prop["weight"]
                 if wght >= 0:
                     adjusted += self.traits[trait]*wght
                 else:
                     adjusted +=  (1 - self.traits[trait])*wght 
      except Exception as e:
          print("ERROR in event_modifier" ) 
          xcv
      """     
      return adjusted
   
      
   def modifiers(self, stimuli, stimuli_class,  met, unmet): 
      """


      """
      val     = 0.0
      i_met   = len(met)
      i_unmet = len(unmet)
 
      edges = self.episodic_memory.related( stimuli_class, "stimuli_factors", None , return_data = True) 
      edges =  [[e["o"], e["s"], e["data"] ] for e, scr, v in edges] 
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
    from memory.st_memory import STMemory
    from memory.lt_memory import LTMemory
    from communication.nerves import Nerves 
    
    from triples.triples     import Triples
    s_robot       = "squirrel"
    nerves        = Nerves(s_robot) 
    triples       = Triples(agent=s_robot, 
                             config=  config,
                             communication=None,
                             nerves =nerves,
                             client=False)    

    st_mem        = STMemory(s_robot, config,triples,  False) 
    
    from ai.personality          import Personality
    personality    = Personality("squirrel" ,
                                  config,
                                  triples,
                                  {} )
    stimuli_class = "movement"
    
        
    with open(config.DATA_PATH + s_robot + "/settings.json") as f:
        data = ''
        for row in f:
              data += row  
        settings = json.loads(data)

    cog_c = CognitiveControl(s_robot, 
                            config, 
                            settings, 
                            personality, 
                            triples, 
                            False)
    

    edges = cog_c.episodic_memory.related( stimuli_class, "emotion_factors",None , return_data = True)

    print(edges)
 
   