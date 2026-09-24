#!/usr/bin/python
# -*- coding: utf-8 -*-
  
"""
Description: AI interactions lookup.
Author: HipMonsters.com  
License: MIT License  
"""

import random 
import json 
import traceback     

class Interactions(object):
   ""


   ""

   def __init__(self, robot, config, nerves, cognitive_control, lt_memory, triples,  low_memory_mode):
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
      self.triples            = triples 


   def try_tool(self, prompt):

       resp  = ""
       b_cmd = False
       potential_tools = self.triples.router.search(prompt.split(" "))   
       pot_tool = potential_tools[0] 
       t_out = open("tools.log", "a")
       t_out.write(prompt + " " + str(pot_tool) + "\n") 

       if  pot_tool[-1] >= 1.8: 
           cmd = pot_tool[1]["function"]  
           if cmd in ["date", "time"]:
                _p = prompt.split(cmd) 
                _s , _o = "", "" 
                if pot_tool[-1] >= .8:  
                    if "s" in pot_tool[1]:
                         _s =  pot_tool[1]["s"]
                     
                    if "o" in pot_tool[1]:
                         _o =  pot_tool[1]["o"]
                      
                params = ["", ""]
                if len(_p) == 1: 
                     params[0] = _p[0]  
                else:
                     params[0] = _p[0] 
                     params[1] = _p[1]   

                if _s != "":
                     params[0] = _s

                if _o != "": 
                     params[1] = _o   
 
                try:     

                    t_out.write("  >ran " + str(cmd) + "\n")
                    resp =   getattr(self.triples, "%s" % cmd.lower().strip())(params[0], params[1])   
                    t_out.write("  >out " + str(resp) + "\n")

                    if type(resp) is str:
                        resp = [resp]
                        b_cmd = True 

                    elif type(resp) is float:
                        resp = [str(resp)]
                        b_cmd = True 
                        
                    elif type(resp) is list: 
                        b_cmd = True  
 
                except Exception as e:  
                     print(e)
                     print(  traceback.print_exc())
  
       return [b_cmd,  resp]

   def get_stimuli_summary(self,  behavior):
       """

       """  
       stimuli = {}
       for dt , details in behavior.st_memory.memory["stimuli"].items():
           stim =   details["stimuli_class"]

           if stim not in  stimuli:
               stimuli[stim ] = 1
           else:
               stimuli[stim ] = stimuli[stim ] + 1
 
       return stimuli 
    

   def get_thoughts(self, behavior):
       """ """

       ## move to graph
       stim_resp = {"tilt":["better be careful", "wow"],
                    "light":["who changed the lights"],
                    "sound":["something out there", "hello", "is anyone there"],
                    "tempature":["am i in the sun"],
                    "humidity":["i hoppe my metal does not rust"],
                    "touch":["hello", "how are you", "thank you"], 
                    "distance":["hello there"], 
                    "movement":["a lot is going on"], 
                    }

       itype = random.randint(0, 18)
       response = []

       if behavior.stimuli_class in stim_resp and itype < 5:
            response  = random.choice(stim_resp[behavior.stimuli_class])

       if  itype  == 0:  
            response = ["stimuli detected " +  behavior.stimuli_class] 
       elif  itype  == 1:  
            response = ["current mood " + behavior.emotions.mood()]
       elif  itype  == 2: 
            response = ["current objective " + behavior.objective]
       elif  itype  == 3: 
             response = ["current strategy " + behavior.strategy]
       elif  itype  == 4: 
            if len(behavior.met) == 0: 
                response = ["no goals are met"]
            else:
                response = ["goals met are " + " ".join(behavior.met)]

       elif  itype  == 5: 
            if len(behavior.umet) == 0: 
                response = ["no goals are umet"]
            else:
                response = ["goal unmet are " + " ".join(behavior.umet)]

       elif  itype  == 6: 
            if  behavior.scr < 0:
                response = ["stimuli impact negative "  ]
            else:
                response = ["stimuli impact positive "  ] 
       elif  itype  == 7:  
            response = ["epoch is " + str(behavior.epoch)] 

       elif  itype  >= 8:  
           stimuli = self.get_stimuli_summary(behavior)
           _len = len(stimuli) -1
           _int = random.randint(0, _len)
           stim = list(stimuli.keys())[_int]
           cnt  =  stimuli[stim]   
           response  = [   stim + " detected  " + str(cnt) + " times today"]
 
       return response 
   
   def responses(self, topic, category, prompt,  behavior, interactive, get_chat_response, b_just_move = False):
       """ 

       """ 
 

       mood      = behavior.emotions.mood()
       objective = behavior.objective
       strategy  = behavior.strategy  
       
       if strategy == "quiet":
          return {"speech" : "", "movement":[]}
       result = {}
       result["topic"]          =  topic #should be gotten from sth
       result["category"]       =  category     
       result["stimuli"]        =  behavior.stimuli_type       
       result["stimuli_class"]  =  behavior.stimuli_class
       result["amplitude"]      =  behavior.amplitude   
       result["stimuli_time"]   =  behavior.stimuli_time  
       result["scrs"]           =  behavior.scrs 
       result["scr"]            =  behavior.scr   
       result["met"]            =  behavior.met  
       result["umet"]           =  behavior.umet   
       result["indif"]          =  behavior.indif   
       result["mood"]           =  behavior.mood   
       result["objective"]      =  behavior.objective    
       result["strategy"]       =  behavior.strategy    
       result["stimuli_time"]   =  str(behavior.stimuli_time)  

      
 
       if strategy in self.cognitive_control.non_verbal_strategies or b_just_move:
           response = {}
           response["speech"] = ""
           if strategy == "quiet":
                response["movement"] = [""]
           else:
                #i_max = len(self.movement[objective][0]) - 1 #added [0]
                i_index = 0# random.randint(0,i_max)
                response["movement"] =  [self.movement[objective][i_index] ]  
       else:
             response = self.__response_verbal(topic, category, behavior.stimuli_class, prompt,  behavior, interactive, get_chat_response) 
 
       if len(response["speech"]) > 0 or  len(response["movement"]) > 0:
           result["prompt"]         = prompt
           result["response"]       = response
           with open(self.config.DATA_PATH + self.robot + "/actions.json", "a") as f:
                f.write(json.dumps(result) + "\n")

       return response    
   
   def __response_verbal(self, topics, category,stimuli_class, prompt,  behavior, interactive, get_chat_response):
       """
       
       """
       
       response   = {"speech" : "", "movement":[]}
       mood       = behavior.emotions.mood()
       objective  = behavior.objective
       strategy   = behavior.strategy     
       situation  = behavior.situation     

       if interactive: 
            b_cmd,  resp = self.try_tool( prompt)   
            if  b_cmd is False:
                resp = get_chat_response(prompt, 
                                         mood, 
                                         strategy, 
                                         topics,
                                         objective, 
                                         situation )   
                resp = [resp]   
            response["speech"]  =  resp 
       else:   
           i_index = random.randint(0,10)    

           if  i_index <=  3:
                resp  =  self.lt_memory.memory["moods"].search_tfidf.similarities([mood], 1000) 

                if   resp  is None:  
                     resp= self.get_thoughts(behavior) 
                elif  len(resp) == 0:  
                     resp= self.get_thoughts(behavior) 
                else:
                     resp = random.choice(resp)  
                     resp  = [resp[1]]     
           else:      
                resp= self.get_thoughts(behavior)
  
           response["speech"]  =  resp   
            
       i_max = len(self.movement[objective]) -1
       i_index = random.randint(0,i_max)
       response["movement"] =  [self.movement[objective][i_index]]  

 
       return  response
       
if __name__ == "__main__":

    """
    python3 launcher.py  -monitor
  
    """
    import os , sys

    print("source ~/venv_rf/bin/activate")
    os.chdir('../')
    sys.path.insert(0, os.path.abspath('./')) 
    import config
    from ai.cognitive_control import CognitiveControl 
    from ai.personality import Personality 
    from memory.st_memory import STMemory
    from memory.lt_memory import LTMemory
    from communication.nerves import Nerves  
    from responders.chat_responder import ChatResponder 
    from ai.behavior import Behavior

    from triples.triples     import Triples
    s_robot       = "number_3"
    nerves        = Nerves(s_robot) 
    triples       = Triples(agent=s_robot, 
                            config=  config,
                            communication=None,
                            nerves =nerves,
                            client=False)    
    st_mem        =  STMemory(s_robot, 
                              config,
                              triples, 
                              False) 
    lt_mem        =  LTMemory(s_robot, 
                              config, 
                              triples= triples, 
                              load_all=True) 
    
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

    cognitive_control = CognitiveControl(s_robot, 
                                         config, 
                                         settings, 
                                         personality, 
                                         triples, 
                                         False)

    interactions = Interactions(s_robot, config, nerves, cognitive_control, lt_mem, triples,  False)
        
    from ai.sensors_fusion       import SensorFusion  

    sensor_fusion = SensorFusion(st_mem  , lt_mem , triples)
    behavior      = Behavior(s_robot               , 
                          config              ,
                          settings            ,
                          personality         ,
                          cognitive_control   ,
                          st_mem          , 
                          lt_mem            ,
                          triples             ,
                          False) 
    behavior.situation =  sensor_fusion.reason() 
    polling_rate = .1
    import time
    chat_wait_length= 3000
    def get_chat_response(self, prompt, 
                              mood="happy",
                              tone="Appreciative", 
                              topics=["cat"], 
                              objective="engagement",
                              situation= {}):
            """
            
            """
            
            param = {}
            prompt = prompt.replace("'", "<aprostophy>").replace("`", "<aprostophy>")
            param["action"]     = "respond"
            param["prompt"]     = prompt.replace("'", "<aprostophy>")
            param["mood"]       = mood 
            param["tone"]       = tone 
            param["topics"]     = topics
            param["objective"]  = objective
            param["situation"]  = situation   
            nerves.set("chat" , json.dumps(param) )
     
            time.sleep( polling_rate)
            i_cnt = 0
            while True:
                detect, val =  nerves.pop("chat_responses")  
                i_cnt += 1
                if detect:
                    nerves.set("speech", "")   
                    print(val)
                    return val   
                 
                elif i_cnt >  chat_wait_length:
     
    
                    nerves.set("speech", "")   
                    return  "aeeeir"  
                
                time.sleep(polling_rate)

    while True:
       user_input = input('CHAT: ') 
       resp = interactions.responses("cat", 
                                     "speech", 
                                     user_input, 
                                     behavior, 
                                     True,
                                     get_chat_response)

       if "processed" in resp: 
                print("INTENT: " +   resp["processed"]["Intent"][0]    )
                print("LOGIC : "  + str( resp["processed"]["Logic"]  )  )
       
       print(  resp )  
