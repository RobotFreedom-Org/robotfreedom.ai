#!/usr/bin/python
# -*- coding: utf-8 -*-
  
"""
Description: AI knowledge graph interface.
Author: HipMonsters.com  
License: MIT License  
"""
#https://codelucky.com/python-networkx/
import os  , sys, random
import datetime
import networkx as nx
import json 
  
if __name__ == "__main__":   
     
    mapped_amplitude=  { 'speech':["robotics", "I like you!" , "I am angry! go away!" , 
                                   "I like cats!" , "I am happy!" ,"this is cool!" , 
                                     "how are you?" , "What can it do?"],
                         'light':[1],  
                         'humidity':[1], 
                         'temperature':[1], 
                         'balance':[1], 
                         'noise':[1], 
                         'touch':[1],
                         "movement":[1], 
                         "distance":[1], 
                         "quiet":[0] }
     
    mapped_amplitude2=  { 'speech':["I do not like you!" , 
                                   "I am angry! go away!",
                                   "I am happy!",
                                   "this is cool!" ,
                                   "how are you?" ,
                                   "What can it do?"] }
     
    mapped_amplitude3=  { 'speech':[  "I am happy!",
                                   "this is cool!" ,
                                   "how are you?" ,
                                   "What can it do?"] }
     
    #mapped_amplitude=  { 'speech':"I like you!" }
    mapped_amplitude4=  { 'speech':"I am angry! go away!" }
    
    stimuli_len = len(mapped_amplitude) - 1
    
    os.chdir('../')
    sys.path.insert(0, os.path.abspath('./')) 
    import config 
    from ai.personality       import Personality
    from ai.cognitive_control import CognitiveControl
    from ai.behavior          import Behavior
    from memory.lt_memory     import LTMemory
    from memory.st_memory     import STMemory 

    robot_name= "number_3" 
    personality    = Personality(robot_name,
                                 config,
                                 {} )
    cog_cntrl = CognitiveControl(robot_name, config, {}, personality, False)
 
    for es in cog_cntrl.G.edges(data=True ):
        print (es)
     
 
    lt_memory       = LTMemory(robot_name, config, False) 
    st_memory       = STMemory(robot_name, config, False) 

    with open(config.DATA_PATH + robot_name + "/settings.json") as f:
           data = ''
           for row in f:
              data += row  
           settings = json.loads(data)

    behavior = Behavior(robot_name, 
                        config, 
                        settings , 
                        personality, 
                        cog_cntrl, 
                        st_memory , 
                        lt_memory,
                        False ) 
    i_epochs         = 5000
    stimuli_time     = datetime.datetime.now()
    dt_last_movement = datetime.datetime.now()
    dt_last_spoke    = datetime.datetime.now()
 
    print("Starting Simulation")
    prior_response   = ""
    interval         = 10
    out = open("../thought_visuals/sim_behavior.csv", "w")
    out.write("epoch,Event_DateTime,stimuli_class,value,emotion,goal,strategy\n")
    for epoch in range(i_epochs):
        
       interval         = random.randint(30, 160) /300000.0
       
       stimuli_time     = stimuli_time + datetime.timedelta(interval)
      
       last_moved       = (stimuli_time - dt_last_movement).total_seconds() 
       last_talked      = (stimuli_time - dt_last_spoke).total_seconds() 
  
       stimuli_type   = "sense" 
       stimuli_class  = list(mapped_amplitude.keys())[random.randint(0, stimuli_len)] 
       signals        = mapped_amplitude[stimuli_class]
       i_sig_len      = len(signals)  -1
       signal         = signals[random.randint(0, i_sig_len)]
       amplitude      = 1
       
       print(stimuli_class)
       behavior.stimuli(stimuli_type, 
                        stimuli_class, 
                        signal,  
                        amplitude, 
                        prior_response,
                        epoch, 
                        stimuli_time , 
                        last_moved,   
                        last_talked, 
                        interval)
       
       """ 
       responses =  interactions.responses(stimuli_type, 
                                         stimuli_class, 
                                         signal,  
                                         behavior,
                                         chat,
                                         get_chat_response) 
       """
       
       
       print("%s %s %s %s %s %s" %  (str(epoch).rjust(20)   , 
                                     stimuli_class.rjust(20),  
                                     str(signal).rjust(20)  ,
                                     behavior.emotions.mood().rjust(20), 
                                     behavior.objective.rjust(20), 
                                     behavior.strategy.rjust(20)  ))
       
       sout = "%s,%s,%s,%s,%s,%s,%s\n" %  (str(epoch) , 
                                     str(stimuli_time),
                                     stimuli_class ,  
                                     str(signal)  ,
                                     behavior.emotions.mood() , 
                                     behavior.objective , 
                                     behavior.strategy )
       out.write(sout)

       """
       
       dt_last_movement = datetime.datetime.now()
       dt_last_spoke    = datetime.datetime.now()
       """