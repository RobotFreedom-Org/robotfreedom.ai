# -*- coding: utf-8 -*-
  
"""
/Users/theodoreharris/Desktop/MAKER25Data /chat/chat_ollama.train.log
Description: This builds and controls a simple chatbot design to run on a RaspberryPi.
Author: HipMonsters.com 
Date Created: Jan 1, 2021
Date Modified: Oct 10, 2024 
Version: 8.0
Platform: RaspberryPi
License: MIT License   

""" 
import warnings   
warnings.filterwarnings("ignore")   
 
class CSimAdv(object):

    def __init__(self,  st_memory, lt_memory, build=False, verbose=False):
        """
        """ 

        self.verbose       = verbose 
        self.history       = []
        self.speaker_facts = {}
        self.lt_memory     = lt_memory 
        self.st_memory     = st_memory 
        build              = True
        self.current_user  = None 
        self.s_path = "../data/knowledge/" 

    def close(self):
         """
         """
         pass #self.model_cpp.close()   
 

    def reset_prompt(self, prompt): 
         """
     
         """ 
         pass 

    def respond(self, user_response, details, history, get_status):
        """
        Docstring for response
        
        :param prompt: Description
        :param ana: Description
        :param history: Description
        :param user_facts: Description
        """  

        user_intent = details["user_intent"]   
        expected_response = details["expected_response"]   
        context = details["context"]   
        prior_resp = details["prior_resp"]   
        reason_cd = {}
        if  expected_response == "self_reflection"  :
              ai_response =  self.get_status() 

        elif expected_response == "inquiry" and len(context) > 0: 
             ai_response =  context[0][1]  

        elif  len(prior_resp) > 0:   
             ai_response =  prior_resp[0][1]  

        elif  len(context) > 0: 
             ai_response =  context[0][1]  

        else:
             ai_response = "I am not sure what you said."
             
             if user_intent == "statement": 
                  ai_response = "Intresting. Can you tell me more?."

             elif user_intent == "inquiry": 
                  ai_response = "I am not sure I know how to response."

        return ai_response, reason_cd