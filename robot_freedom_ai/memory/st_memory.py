#!/usr/bin/python
# -*- coding: utf-8 -*- 
"""
Description: AI knowledge graph interface.
Author: HipMonsters.com  
License: MIT License  
""" 
import os 
import subprocess  
import json  

 
class STMemory(object):
   """
   Short Term Memory
   """
   
   def __init__(self, robot, config, triples, low_memory_mode ):
      """
      
      """
      
      self.robot            = robot
      self.config           =  config 
      self.triples          =  triples 
      self.low_memory_mode  =  low_memory_mode    
      self.kb               = self.triples.TrplGraph()

      #  sharing empathy curiosity processing
      example_recs = {"stimuli": "sense", "stimuli_class": "speech", "amplitude": 1, 
                 "signal": "", "scr": 1.0, "scrs" : {}, "prior_response": {},
                 "motivations": {"sharing": 0.5375, "empathy": 0.678125, "curiosity": 0.58375,  "processing": 0.125  }, 
                 "mood": "happy", 
                 "moods":{"happy": 0.5, "sad": 0.0, "fear": 0.0, "disgust" : 0.0, "anger" : 0.0, "bored": 0.0, "surprised" : 0.0},
                 "objective": "engagement", 
                 "strategy": "quiet", 
                 "event_interval" :1,
                 "stimuli_time": "0.118326", "epoch": 1}

      if not os.path.exists(self.config.DATA_PATH + self.robot + "/stimuli.json"):
          f =  open(self.config.DATA_PATH + self.robot + "/stimuli.json", 'w')  
          f.write(json.dumps(example_recs)) 
          f.close()   
      self.memory = {} 
      self.memory["stimuli"] = {} 
      self.memory["kb"]      =  self.triples.TrplGraph(remote=True)     

      self.memory["stimuli_sequence"] = []
      self.memory["stimuli_counter"]  = {} 
       
      cmds = ["tail", 
              "-100", 
              self.config.DATA_PATH + self.robot + "/stimuli.json"]
      result = subprocess.run(cmds, capture_output=True, text=True) 
      results = result.stdout 

      recs = [] 
      for line in results.split("\n"): 
              try:
                  row = json.loads(line.strip()) 
                  if "stimuli_time" in  row:
                      recs.append([row["stimuli_time"] , row ])
              except Exception as e:
                  print("Warning a stimuli memory is corrupt!") 
                  print(str(e)) 
                  print(line)

      if len(recs) == 0: 
          recs.append([example_recs["stimuli_time"] , example_recs ])
      
          
      for dt, row in recs: 
         self.memory["stimuli"][dt] = row   
     
      motivations = {"sharing":  .5,  "empathy":    .5,
                     "curiosity": .5, "processing": .5 } 
      
      for key , wgt in motivations.items():
          if key not in row["motivations"]:
              row["motivations"][key] = .5
 
      _to_delete = []
      for key , wgt in row["motivations"].items():
      
          if key not in  motivations: 
              _to_delete.append(key)
          elif wgt > .1:
            row["motivations"][key] = .1
          
          elif wgt < -.1:
            row["motivations"][key] = -.1 

      for key in _to_delete:
         del row["motivations"][key]
                    
      self.last_memory_dt = dt
      self.last_memory    = row

      maxwgt = -1000
      primary_motivation = "unknown"
      for motivation, wgt in   row["motivations"].items(): 
          if wgt > maxwgt:
             primary_motivation = motivation  
             maxwgt = wgt
              
          
      self.memory["kb"].add("motivation"  , "current", primary_motivation)    
      self.memory["kb"].add("emotion"  , "current", row["mood"])  
      self.memory["kb"].add("objective", "current", str(row["objective"]))
      self.memory["kb"].add("strategy" , "current", str(row["strategy"]))
      self.memory["kb"].add("stimuli_class", "current", row["stimuli_class"])    
  
      if  "situation" in row:
        if type(row["situation"]) is dict:
          for key, prop in row["situation"].items(): 
              self.memory["kb"].add(key, "current", prop["code"] , prop) 

      if  "locomotion" in row:
          if len(row["locomotion"]) > 0:  
              self.memory["kb"].add("locomotion", "current", "true" , prop) 
          else:
              self.memory["kb"].add("locomotion", "current", "false" , prop) 

      if  "movement" in row:
          if len(row["movement"]) > 0:  
              self.memory["kb"].add("movement", "current", "true" , prop) 
          else:
              self.memory["kb"].add("movement", "current", "false" , prop) 
 
      if  "umet" in row: 
          for  goal in row["met"]: 
              self.memory["kb"].add(goal, "current", "umet" , prop) 
 
      if  "met" in row: 
          for  goal in row["met"]: 
              self.memory["kb"].add(goal, "current", "met" , prop) 
 
      if  "indif" in row: 
          for  goal in row["met"]: 
              self.memory["kb"].add(goal, "current", "indif" , prop) 
      
      
 

 