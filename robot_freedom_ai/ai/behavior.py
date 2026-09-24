#!/usr/bin/python
# -*- coding: utf-8 -*- 
"""
Description: AI behavior interface.
Author: HipMonsters.com  
License: MIT License  
"""
  
import datetime 
import json   
from ai.motivations          import Motivations
from ai.emotions             import Emotions
from ai.experience           import Experience 
from ai.wayfinder            import WayFinder   
from ai.sensors_fusion       import SensorFusion  

class Behavior():

   def __init__(self, robot, config, settings , personality, cognitive_control, st_memory , lt_memory, triples, low_memory_mode ):
       """
       S-O-R Theory with Personality Traits
       
       
       """ 
       self.prior_response = ""
       self.stimuli_type   = "" 
       self.stimuli_class  = ""
       self.amplitude      = ""
       self.stimuli_time   = "" 
       self.stimuli_type   = ""    
       self.stimuli_class  = "" 
       self.amplitude      = "" 
       self.stimuli_time   = "" 
       self.scrs           = "" 
       self.scr            = "" 
       self.met            = "" 
       self.umet           = "" 
       self.indif          = "" 
       self.mood           = "" 
       self.objective      = ""  
       self.objectives     = []  
       self.robot                  = robot
       self.config                 = config
       self.settings               = settings
       self.low_memory_mode        = low_memory_mode
       ## Core components
       self.cognitive_control      =  cognitive_control
       self.st_memory              =  st_memory
       self.lt_memory              =  lt_memory

       self.last_stimuli      = None
       self.stimuli_time      = -1
       self.epoch            = 0
       self.last_update      = None 
       self.situation   ={}
              
       
       self.debug       = False
       self.personality = personality  

       self.discount    = self.personality.discount 
       self.novelty     = 1 - self.discount  
       self.objective   = self.personality.defaults["objective"]
       self.strategy    = self.personality.defaults["strategy"]

       self.triples      = triples
       self.wayfinder    = WayFinder(0,  1, 0)   
       self.sensor_fusion = SensorFusion(st_memory , lt_memory, triples)

       row = self.st_memory.last_memory
       if "moods" in row:
            moods       = row["moods"]
       else:
            moods =  {"happy": 1.5, "sad":     0.0,
                      "fear":  0.0, "disgust": 0.0, 
                      "anger": 0.0, "bored":   0.0, 
                      "surprised": 0.0  }
            
       self.emotions    = Emotions(self.robot, 
                                   self.cognitive_control,
                                   moods, 
                                   self.personality ,  
                                   self.low_memory_mode)
       if "motivations" in row: 
           motivations = row["motivations"]
       else:  
           motivations = {"engagement":  .5, "novelty":  .5,
                          "acquisition": .5, "creating": .5, 
                          "processing":  .5, "empathy": .5}  
           
       self.motivations = Motivations(self.robot, 
                                      self.config, 
                                      self.cognitive_control,
                                      motivations,
                                      self.personality,  
                                      self.lt_memory,
                                      self.triples,
                                      self.low_memory_mode)
       
       self.experience  = Experience(self.robot , 
                                      self.config,
                                      self.cognitive_control,
                                      self.personality,  
                                      self.st_memory,
                                      self.lt_memory,
                                      self.low_memory_mode)
       
       self.emotional_suppressors = self.experience.emotional_suppressors(self.objective ,
                                                                          self.strategy ,
                                                                          "wakeup" )


   def behavior(self, mood, modifier):
       """
       """
       return 1
   
   def determine_class(self, event, cat, met, umet, modifier):
       """
       suppressors
       """
       return event + " " + cat
   
   def remember(self, n = 5):
        _t  = self.st_memory.memory["stimuli_sequence"][-n: ]
        return [self.st_memory.memory["stimuli"][v] for v in _t ]       
 
   def save_memory(self, stimuli ,stimuli_class, signal ,  amplitude , 
                   prior_response, scr, scrs, mood, moods,  objective ,  strategy,  motivations,  
                   emotional_suppressors, interval,  epoch, stimuli_time):
       """
       stimuli
       """
        
       str_stimuli_time = str(stimuli_time) 

       time_stamp =stimuli_time.timestamp()
       self.st_memory.memory["kb"].update("emotion"     , "current", mood, time_stamp)  
       self.st_memory.memory["kb"].update("objective"   , "current", objective, time_stamp)
       self.st_memory.memory["kb"].update("strategy"    , "current", str(strategy), time_stamp)
       self.st_memory.memory["kb"].update("stimuli_class", "current", stimuli_class, time_stamp)    

       for key, prop in self.situation.items(): 
          if key != "last_stimuli":
              self.st_memory.memory["kb"].update(key, "current", prop["code"] ,time_stamp, prop) 
 
       for  goal in self.met : 
              self.st_memory.memory["kb"].add(goal, "current", "umet" , prop) 
  
       for  goal in self.met : 
              self.st_memory.memory["kb"].add(goal, "current", "met" , prop) 
  
       for  goal in self.met : 
              self.st_memory.memory["kb"].add(goal, "current", "indif" , prop) 

       maxwgt = -1000
       primary_motivation = "unknown"
       for motivation, wgt in  motivations.items(): 
          if wgt > maxwgt:
             primary_motivation = motivation  
             maxwgt = wgt 
          
       self.st_memory.memory["kb"].add("motivation"  , "current", primary_motivation)  
       
       self.st_memory.memory["stimuli_sequence"].append(str_stimuli_time)
       self.st_memory.memory["stimuli"][str_stimuli_time] = {"stimuli" :  stimuli ,
                                                             "stimuli_class" : stimuli_class, 
                                                             "amplitude" : amplitude ,
                                                             "signal" : signal ,
                                                             "prior_response" : prior_response,
                                                             "scr" : scr ,
                                                             "scrs" : scrs,
                                                             "motivations" : motivations ,
                                                             "mood" : mood ,
                                                             "moods" : moods ,
                                                             "objective" : objective ,
                                                             "strategy" : str(strategy) ,
                                                             "emotional_suppressors" : emotional_suppressors,
                                                             "stimuli_time" : str_stimuli_time ,
                                                             "event_interval" : interval,
                                                             "situation": self.situation,
                                                             "epoch" : epoch ,
                                                              "met"   :    self.met,   
                                                              "umet" :    self.umet, 
                                                              "indif" :    self.indif }
       ## move to main as some point
       with open(self.config.DATA_PATH + self.robot + "/stimuli.json", "a") as f:
            f.write( json.dumps(self.st_memory.memory["stimuli"][str_stimuli_time])  + "\n")
            
       self.last_update      = datetime.datetime.now() 
       

   def reflection(self):
        """

        Stimuli ->
        emotions  (stimuli_emotions_fit) #heavily weighted down
        goals     (emotions_goals_fit) #heavily weighted down
        strategy  (strategy_scr_fit, strategy_goals_fit)
        response  (word_whts, emotions_scr_fit, goal_scr_fit)
           
        """
        self._space  = "          "
        print("\rSelf-Reflection : Initiating " + self._space  , end="" )  

        self.experience.reflect() 
        print("\rSelf-Reflection Complete    " + self._space , end="" )   
       
        self.cognitive_control.update_weights()
        print("\rWeights Updated             " + self._space , end="" )   
        
        return True   
          
                
   def stimuli(self, stimuli_type, stimuli_class, signal,  amplitude, prior_response,user_detected,
               epoch, stimuli_time , last_moved,   last_talked, interval, chatting, 
               mobile=False, time_since_last_change=-1, current_direction="f",other={}):
       """
       S-O-R Theory with Personality Traits
       Stimuli Observation Response
       Stimuli -> personality + desires + experience -> emotions -> response
  AES hormone profiles (cortisol, adrenaline, testosterone suppression, dopamine deficit, oxytocin block, serotonin depletion)

  
       """


       #1. what is want is the to use Altruistic quotes to prompt the llm.tone_v1_122

       #2. cognitive_control loads in common sense to help determine topics
   
       #3. determine if goal is met using nlp from verbal response.else

       #4. Do a follow up questions when confused ask "do you feel engaged?"
      
       #5. the use xgboost to learn score to pick strategy

 
       
       stimuli_history         = self.remember()

      
       self.epoch          = epoch
       self.user_detected  = user_detected
       self.prior_response = prior_response
       self.stimuli_type   = stimuli_type 
       self.stimuli_class  = stimuli_class
       self.amplitude      = amplitude
       self.stimuli_time   = stimuli_time 

       ## higher order classification of event TODO modifier
       # event_class event_cat = self.determine_class(stimuli, stimuli_class)

       ### Can learn to adjust stimuli class and amplitude- learn to like what you dont like
       self.emotional_suppressors    = self.experience.emotional_suppressors(self.objective, 
                                                                              stimuli_class)
       
       ## How personality affects how event seen
       adjusted_modifier       = self.cognitive_control.event_modifier(stimuli_type, 
                                                                       stimuli_class, 
                                                                       amplitude)
 
       ## Check status of motivations
       met, umet, indif, scr, scrs, reaction = self.motivations.goal_achievement(stimuli_type, 
                                                                       stimuli_class,
                                                                       stimuli_history,
                                                                       signal,
                                                                       amplitude, adjusted_modifier , 
                                                                       stimuli_time,  epoch) 
       
       self.sensor_fusion.update(stimuli_class,amplitude,stimuli_time , user_detected, scr, scrs) 
       
       self.situation = self.sensor_fusion.reason() 


       self.scrs  = scrs
       self.scr   = scr 
       self.met   = met
       self.umet  = umet
       self.indif = indif
       # update emotions based on class and modifier
       self.emotions.stimuli(stimuli_type, 
                             stimuli_class, 
                             adjusted_modifier,  
                             self.emotional_suppressors  )
       
       #self.emotions.situation(self.situation) 
       
       if self.debug:
           print((met, umet, indif, adjusted_modifier, scr))
            
       # update emotions based on class and modifier
       self.emotions.reflection(met, umet , indif,  adjusted_modifier , reaction ) 
       self.mood = self.emotions.mood() 
    
       self.objective    ,self.objectives      = self.motivations.objective(met, umet, indif ,self.mood ) 
       self.strategy      = self.experience.strategy(self.objective, 
                                                          interval , 
                                                          last_moved,
                                                          last_talked, 
                                                          self.mood,
                                                          chatting)
       
       if mobile: 
           self.locomotion_goals = []
           x,y,z,dist = self.wayfinder.calc_x_y_z(time_since_last_change, 1, 1, 0, 1)

           if ["distance", "proximity-foward-left", "proximity-foward-right"] :  
                self.wayfinder.sense(["wall", x, y, z])
       
           self.wayfinder.reasoning(current_direction, 
                                    time_since_last_change, 
                                    self.locomotion_goals)   

       # calculate new emotion 
       self.save_memory(stimuli_type ,stimuli_class, signal , amplitude , self.prior_response,
                        self.scr, self.scrs,  self.mood, self.emotions.moods, 
                        self.objective , self.strategy,  self.motivations.motivations ,   
                        self.emotional_suppressors, interval, epoch, stimuli_time)
      
         