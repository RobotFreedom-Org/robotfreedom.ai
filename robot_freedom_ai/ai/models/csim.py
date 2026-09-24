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
import random  

warnings.filterwarnings("ignore")   
 
class CSim(object):

    def __init__(self,  st_memory, lt_memory, persona="normal", build=False, verbose=False):
        """
        """ 

        self.verbose       = verbose 
        self.history       = []
        self.speaker_facts = {}
        self.lt_memory     = lt_memory 
        self.st_memory     = st_memory 
        build              = True
        self.current_user  = None 
        self.persona       = persona
        self.s_path = "../data/knowledge/" 
             

    def close(self):
         """
         """
         pass #self.model_cpp.close()   
 

    def reset_prompt(self, prompt): 
         """
     
         """ 
         pass 
 
    
    def jaccard_similarity(self, sent1, sent2):

        set1 = set(sent1.lower().split())
        set2 = set(sent2.lower().split())
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union)

    
    def respond(self, user_response, details, history, low_memory_mode, directives):
        """
        Docstring for response
        
        :param prompt: Description
        :param ana: Description
        :param history: Description
        :param user_facts: Description
        """    
        reason_cds =  {"reason_cd": "01.normal", "model":"csim"}
        prior_resp = details["prior_resp"]   
        reason_cd = {}   

        if prior_resp[0][-1] > 0: 
            reason_cds["reason_cd"] = "01.1.match" 
        else:
            reason_cds["reason_cd"] = "02.1.no_match" 
            
        i = random.randint(0, len(prior_resp)-1) 
        
        response =  prior_resp[i][1]    

        return  response, reason_cd