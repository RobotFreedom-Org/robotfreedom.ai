#!/usr/bin/python
# -*- coding: utf-8 -*-
  
"""
Description: AI Emotions interface.
Author: HipMonsters.com  
License: MIT License  
""" 

class Emotions():

   def __init__(self, robot ,cognitive_control, moods, personality , low_memory_mode):
       """
       
       """
       self.robot        = robot  
       self.personality = personality
       self.discount    = personality.discount
       self.novelty     = 1 - self.discount 
       self.moods       = moods 

       self.cognitive_control   = cognitive_control
       self.episodic_memory     = self.cognitive_control.episodic_memory
       self.low_memory_mode    = low_memory_mode    
        
       self.emotion_factors =  self.cognitive_control.emotion_factors
       self.emotion_flip    =  self.cognitive_control.emotion_flip

   def save(self , stimuli_time , epoch ):
      """
      
      """
      return None  
       
   def stimuli(self, stimuli , stimuli_class, 
               amplitude ,emotional_suppressors  ):
       """
       
       """ 

       edges = self.episodic_memory.related( stimuli_class, "emotion_factors", None , return_data = True) 
 
       abj_fac = .001
       for edge, scr, val in edges: 
               wght = edge["data"]["weight"]
               mood = edge["o"] 
               adj = 1  
               self.moods[mood] = self.moods[mood]  +  amplitude*wght + adj
     
               self.moods[mood]  = round( self.moods[mood], 5)  
               if  self.moods[mood] < 0:
                   self.moods[mood] = 0
               elif  self.moods[mood] > 100:
                   self.moods[mood] = 100 
                      
       abj_fac_2 = .001
       for mood, weight in emotional_suppressors.items():   
          if mood in  self.moods:  
             # self.moods[mood] = (1 - abj_fac_2)*self.moods[mood]  +  weight*abj_fac_2  
              self.moods[mood]  = round( self.moods[mood], 5)   
          

   def situation(self, situations,   amplitude ,emotional_suppressors  ):
       """
       
       """ 
       for situation in situations:

         edges = self.episodic_memory.related( situation, "situational_factors", None , return_data = True) 
         
         abj_fac = .001

       for edge, scr, val in edges: 
               wght = edge["data"]["weight"]
               mood = edge["o"]   
               adj = 1#prop["adj"]*abj_fac 
               self.moods[mood] = self.moods[mood]  +  amplitude*wght + adj
     
               self.moods[mood]  = round( self.moods[mood], 5)  
               if  self.moods[mood] < 0:
                   self.moods[mood] = 0
               elif  self.moods[mood] > 100:
                   self.moods[mood] = 100 
                      
       abj_fac_2 = .001
       for mood, weight in emotional_suppressors.items():   
          if mood in  self.moods:  
             # self.moods[mood] = (1 - abj_fac_2)*self.moods[mood]  +  weight*abj_fac_2  
              self.moods[mood]  = round( self.moods[mood], 5)   
            
            
   def reflection(self, met , unmet ,indif, amplitude, reactions ):
       """ 
       self.moods = {"happy": 0.5, "sad": 0.0, "fear": 0.0, "disgust" : 0.0,
                      "anger" : 0.0, "bored": 0.0, "surprised" : 0.0,
                       "stimuli_time" : "initial"  , "epoch" : -1} 

                       

       """

       f_scr     = reactions["sentiment"]
       self.f_scr = f_scr

       val     = 0.0
       i_met   = len(met)
       i_unmet = len(unmet)
       i_indif = len(indif)
       # should get from experience
       amplitude = amplitude * self.novelty 
       #https://mindfulartstherapy.com.au/the-six-basic-emotions-happiness-sadness-disgust-fear-surprise-and-anger/
       self.moods["sad"]        =  self.moods["sad"]*self.discount
       self.moods["happy"]      =  self.moods["happy"]*self.discount
       self.moods["bored"]      =  self.moods["bored"]*self.discount
       self.moods["surprised"]  =  self.moods["surprised"]*self.discount
       self.moods["fear"]       =  self.moods["fear"]*self.discount
       self.moods["disgust"]    =  self.moods["disgust"]*self.discount
       self.moods["anger"]      =  self.moods["anger"]*self.discount 

       if i_met > 0:
          self.moods["anger"]               =  self.moods["anger"]  - .25*amplitude 
          
       if i_met < i_unmet: 
          self.moods["sad"]                 =  self.moods["sad"]    + amplitude
          self.moods["happy"]               =  self.moods["happy"]  - .25*amplitude 
       

       elif  i_met > i_unmet:  
          self.moods["sad"]                 =  self.moods["sad"]    - amplitude
          self.moods["happy"]               =  self.moods["happy"]  + amplitude
     

       if i_indif < i_met + i_unmet   : 
          self.moods["bored"]                =  self.moods["bored"]      -  amplitude
          self.moods["surprised"]            =  self.moods["surprised"]  +  .1*amplitude 

       elif i_indif > i_met + i_unmet:  
          self.moods["bored"]                =  self.moods["bored"]      +  amplitude
          self.moods["surprised"]            =  self.moods["surprised"]  -  amplitude 
      
       if self.f_scr < -.8:
          self.moods["sad"]                 =  self.moods["sad"]     + 6*amplitude
          self.moods["happy"]               =  self.moods["happy"]   - 6*amplitude 
          self.moods["disgust"]             =  self.moods["disgust"] + 3*amplitude 
          self.moods["fear"]                =  self.moods["fear"]    + 6*amplitude 
          self.moods["anger"]               =  self.moods["anger"]   + amplitude 
          self.moods["bored"]               =  self.moods["bored"]   - amplitude
           
       elif self.f_scr < -.5:
          self.moods["sad"]                 =  self.moods["sad"]     + 4*amplitude
          self.moods["happy"]               =  self.moods["happy"]   - 4*amplitude 
          self.moods["disgust"]             =  self.moods["disgust"] + 2*amplitude 
          self.moods["fear"]                =  self.moods["fear"]    + 4*amplitude 
          self.moods["bored"]               =  self.moods["bored"]   - amplitude

       elif self.f_scr < 0:  ##-.1
          self.moods["sad"]                 =  self.moods["sad"]     +  amplitude
          self.moods["disgust"]             =  self.moods["disgust"] +  amplitude 
          self.moods["happy"]               =  self.moods["happy"]   -  amplitude 
          self.moods["bored"]               =  self.moods["bored"]   -  amplitude

       elif self.f_scr ==0:
          self.moods["bored"]                =  self.moods["bored"]   + amplitude
          self.moods["fear"]                 =  self.moods["fear"]    - amplitude  

       elif self.f_scr >.8:
          self.moods["sad"]                 =  self.moods["sad"]     - 6*amplitude
          self.moods["happy"]               =  self.moods["happy"]   + 6*amplitude 
          self.moods["disgust"]             =  self.moods["disgust"] - 6*amplitude 
          self.moods["fear"]                =  self.moods["fear"]    - 6*amplitude 
          self.moods["anger"]               =  self.moods["anger"]   - amplitude 
          self.moods["bored"]               =  self.moods["bored"]   - amplitude

       elif self.f_scr >.5:
          self.moods["sad"]                 =  self.moods["sad"]     - 4*amplitude
          self.moods["happy"]               =  self.moods["happy"]   + 4*amplitude 
          self.moods["disgust"]             =  self.moods["disgust"] - 4*amplitude 
          self.moods["fear"]                =  self.moods["fear"]    - 4*amplitude 
          self.moods["anger"]               =  self.moods["anger"]   - amplitude 
          self.moods["bored"]               =  self.moods["bored"]   - amplitude

       elif self.f_scr > 0: #.1 
          self.moods["bored"]               =  self.moods["bored"]   - amplitude
          self.moods["sad"]                 =  self.moods["sad"]     - amplitude
          self.moods["happy"]               =  self.moods["happy"]   + amplitude 
          self.moods["disgust"]             =  self.moods["disgust"] - amplitude 
          self.moods["fear"]                =  self.moods["fear"]    - amplitude 
          self.moods["anger"]               =  self.moods["anger"]   - amplitude 
       
       
       
   def mood(self):
       """
       
       """
       t_moods =  [[key, val] for key, val in self.moods.items() if key not in ['epoch','stimuli_time'] ]
       moods = sorted(t_moods, key=lambda item: item[1]) 
       self.current_mood  = moods[-1][0] 

       return  self.current_mood
        
