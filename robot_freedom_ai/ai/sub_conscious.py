#!/usr/bin/python
# -*- coding: utf-8 -*-
  
"""
Description: AI interactions lookup.
Author: HipMonsters.com  
License: MIT License  
"""
  

class SubConcious(object):
   """
    sub conscious creates a new edge then runs 
    d randon function based on it 

   """

   def __init__(self, robot, config, nerves,  lt_memory,  cognitive_control, trpl_graph , triples, low_memory_mode):
      """
      
      """
      self.robot              = robot
      self.config             = config
      self.nerves             = nerves
      self.low_memory_mode    = low_memory_mode 
      self.cognitive_control  = cognitive_control   
      self.mapped_strategies  = self.cognitive_control.mapped_strategies
      self.vocalization       = self.cognitive_control.vocalization
      self.movement           = self.cognitive_control.movement  
      self.lt_memory          = lt_memory    
      self.chat               = self.lt_memory.memory   
      self.trpl_graph          = trpl_graph 
      self.triples            = triples 
  
   
   def pounderings(self, mood, sense, stimuli,  behavior):
       """ 

       """  
       #aslo add in rtiples to graph , svo_in, svo_out,
       #res = list(self.trpl_graph.infer_edges() )
       fin = []
       #for _to, _frm in res:
       #    if _to in [mood, sense]  or _frm in [mood, sense]:  
       #        self.trpl_graph.add(sense, 'makes', mood) 
       #        break
           
       #if sense == "speech":
       #    for wrd in stimuli.split(" "):
       #        self.trpl_graph.add(wrd, 'feel', mood) 
               
       #self.trpl_graph.save("sub_concious")
       
       return fin  

   
       