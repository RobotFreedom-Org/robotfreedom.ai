#!/usr/bin/python
# -*- coding: utf-8 -*- 

"""
Description: This builds and controls a simple chatbot design to run on a RaspberryPi.
Author: HipMonsters.com 
Date Created: Jan 1, 2021
Date Modified: Oct 10, 2024
Version: 8.0
Platform: RaspberryPi
License: MIT License  
"""
import os
import sys 
import time 
import json    
import argparse
import traceback 

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode")  
parser.add_argument("-r", "--robot") 
parser.add_argument("-d", "--devices", default="")  
parser.add_argument("-p", "--param", default="")  


if __name__ == "__main__":  
   h = "f"
  # from  language import  Language
else:
   from  .language import  Language

class Response(object): 

    def __init__(self, robot, nerves, config, settings, cognitive_control = None, personality =None,
                      lt_memory = None, st_memory=None,  triples =None , params =None, polling_rate = .1, verbose=False):
        """
        
        """ 
        self.robot     = robot 
        self.nerves    = nerves 
        self.module    = "chat"  
        self.config    = config
        self.settings  = settings  
        self.os        = self.config.OS
        self.st_memory = st_memory
        self.lt_memory = lt_memory
        self.polling_rate = polling_rate
        self.verbose   = verbose 
        self.low_memory_mode = False

        if self.config.CONFIG["low_memory_mode"] == 1: 
            self.low_memory_mode = True
              
        if params is not None:  
          if "low_memory_mode" in params:
            if params["low_memory_mode"] == 1: 
              self.low_memory_mode = True


        if triples is None: 
              from triples.triples     import Triples
              triples  = Triples(agent=robot, 
                                config= config,
                                communication=None,
                                nerves=nerves,
                                client=True)  
              
        if st_memory is None:
              from memory.st_memory import STMemory  
              st_memory       = STMemory(robot, config,triples, self.low_memory_mode)  
              
        if lt_memory is None:
              from memory.lt_memory import LTMemory  
              lt_memory       = LTMemory(robot, 
                                         config, 
                                         triples=triples, 
                                         load_all=True)  

              triples.kb = lt_memory.memory["definitions"]

        if personality is None: 
              from .personality import Personality  
              personality       = Personality(robot,  config, settings, triples)  
              
        if cognitive_control is None: 
              from .cognitive_control import CognitiveControl  
              cognitive_control = CognitiveControl(robot,  config, settings, personality, triples, self.low_memory_mode)


        self.cognitive_control  = cognitive_control
        self.personality        = personality
        self.lt_memory          = lt_memory
        self.st_memory          = st_memory 
        self.chat_params        = self.settings["chat"]   
        self.low_memory_mode    = False  
        self.triples              = triples  

        self.language = Language(config, 
                                 self.cognitive_control, 
                                 self.personality, 
                                 self.lt_memory, 
                                 self.st_memory,
                                 triples,
                                 robot.replace("_", " "), 
                                 robot,  
                                 ["cats"],  
                                 self.chat_params["type"],
                                 log=True, 
                                 low_memory_mode = self.low_memory_mode)
        self.type = self.chat_params["type"]
  
        return None     
        
    def serve_forever(self): 
        """ 

        """

        while True: 

           new, cmds = self.nerves.pop("directive:ai_settings") 
           if new:

               
               cmds = json.loads(cmds) 

               if "cmds" in cmds:
                   self.language.sys_cmds(cmds["cmds"])

               if "setting" in cmds:
                   if cmds["setting"].lower() == "rude": 
                       self.language.reset_persona("rude") 
                   else:
                       self.language.reset_persona("good") 

               if "type" in cmds:
                   if cmds["type"].lower() == "llm":   
                        self.language.reset_ai("LLM")

                   elif cmds["type"].lower() == "rules":   
                        self.language.reset_ai("Rules")

                   elif cmds["type"].lower() == "semantictriples" or cmds["type"].lower() == "triples"  :   
                        self.language.reset_ai("SemanticTriples")

                   else: 
                        self.language.reset_ai("CSim")
                        

           new, cmds = self.nerves.pop(self.module) 
           if new: 
               dcmds = json.loads(cmds.strip())  
 
               if dcmds["action"] == "respond":
                  if dcmds["topics"] == "sense":
                      dcmds["topics"] = []

                  if dcmds["tone"] == "quiet":
                      dcmds["tone"]     = "Benevolent" 

                  #self.verbose = True
                  if self.verbose:  
                       print(dcmds ) 
                       t = open("t.log", "a")
                       t.write(json.dumps(dcmds) + "\n") 
                       t.close()
                   
                  try:
                      
                      response =  self.language.respond(dcmds["prompt"].replace("<aprostophy>", "'"),
                                                        dcmds["mood"], 
                                                        dcmds["tone"], 
                                                        dcmds["topics"],
                                                        dcmds["objective"],
                                                        dcmds["situation"] )
                  except Exception as e:
                       
                       t = open("response.error.log", "a")
                       t.write(json.dumps(dcmds) + "\n") 
                       t.write(str(e) + "\n") 
                       t.write(str(traceback.format_exc()) + "\n") 
                       
                       response = {}
                       response["ai_response"]  = "i encounted an error"
                       response["details"]  = {}


                  if len(response["ai_response"]) > 150:
                      response["ai_response"] = response["ai_response"][:150]
                      
                  self.nerves.set(self.module + "_responses", 
                                  response["ai_response"] ) 
                  
                  self.nerves.set(self.module + "_responses_details", 
                                  json.dumps(response) ) 
                  

               elif dcmds["action"] == "clear_mem": 
                  self.language.reset_history()
                  
               self.nerves.set(self.module, "")  
           else:
             pass   
            #  if self.language.engine == "SemanticTriples" and random.randint(1,100) >= 98:  
            #     self.language.ai.revist([])
 
           time.sleep(self.polling_rate)
           
if __name__ == "__main__":
    """

    """
    args    =  parser.parse_args()  
    mode    = args.mode 
    robot   = args.robot   
    param   = args.param
    if param =="":
        param = {}
    else:
        param = json.loads(param)

    os.chdir('../')
    sys.path.insert(0, os.path.abspath('./')) 
    import config 
    from communication.nerves import Nerves 

    from triples.triples     import Tools
    from memory.lt_memory import LTMemory
    from memory.st_memory import STMemory
    from ai.cognitive_control import CognitiveControl 
    from ai.personality import Personality 
    from ai.language import Language  

    nerves  = Nerves(robot) 

    triples   = Tools(robot, 
                          config,
                          None,
                          nerves,
                          False)  

    personality   = Personality(robot, config, {} )

    cognitive_control       = CognitiveControl(robot,  
                                               config, 
                                               {}, 
                                               personality,
                                               False) 
    lt_memory       = LTMemory(robot, config, triples, False) 
    st_memory       = STMemory(robot, config, triples=triples, load_all=False) 


    with open(config.DATA_PATH + robot + "/settings.json") as f:
           data = ''
           for row in f:
              data += row  
           settings = json.loads(data)

    chat = Response(robot, nerves, config, 
                    settings, cognitive_control,personality, 
                    lt_memory, st_memory, 
                    triples, param) 

    if mode == "serve": 
        chat.serve_forever()

    elif mode == "test":  
       print(chat.language.respond("how are you?"))


    elif mode == "fit":  
       chat.build_models(args.param)