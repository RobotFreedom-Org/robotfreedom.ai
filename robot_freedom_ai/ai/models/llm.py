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
import  re 
import warnings   
 
warnings.filterwarnings("ignore")    

from llama_cpp  import Llama   

import os,sys
import contextlib

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr
 
 
max_tokens  = 50  #20 #16
temperature = .15 #0.9  

parts_all = ['Object' , 
             'Verb' , 
             'Subject' , 
             'Complement' ,
             'Modifier' , 'Intent']

parts = ['Subject', 'Verb', 
         'Object', 'Complement',
         'Modifier']
 

Ideas = [ ["Idea"          , "Concept" ], 
              ["Question"      , "Self"],   
              ["Question"      , "Speaker" ],
              ["External_Idea" , "Concept"],
              ["Speaker_Idea"  ,  "Concept"   ]] 
     
Ideas_query = [ ["Idea"   , "Concept" ], 
                ["External_Idea", "Concept"] ]    
 

class LLM(object):

    def __init__(self,  st_memory, lt_memory, build=False, verbose=False):
        """
        """ 

        self.verbose       = verbose 
        self.history       = []
        self.speaker_facts = {}
        self.lt_memory     = lt_memory 
        self.st_memory     = st_memory 
        self.build         = build
        self.current_user  = None 
        self.s_path = "../data/knowledge/"

        with suppress_stderr():
            self.model_cpp  = Llama("../data/llms/scripted_response.gguf",  
                                    verbose=False)    
    
    def close(self):
         """
         """
         self.model_cpp.close()   

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

    def respond(self, user_response, details, history, low_memory_mode, directives   ):
        """
        Docstring for response
        
        :param prompt: Description
        :param ana: Description
        :param history: Description
        :param user_facts: Description
        """ 
        """"""  
        #mood        = directives["mood"] ## prompt directive
        tone        = directives["tone"] ## prompt directive
        #persona     = directives["persona"] ##choose sub-model 
        #full_name   = directives["full_name"]  ## prompt directive 

        if  low_memory_mode:  
              max_tokens  = 17
              temperature = 0.95 
        else:
              max_tokens  = 17 #20  
              temperature = 0.95 #0.9
 
       # prompt =  f"Below are personality traits that define a fictional character. Write a response that appropriately responds to the user prompt in character to the personality traits listed below.\n\n### Instruction:\n{traits}"
        prompt =  f"Adopt a personality based on the following tone when responding to user prompts.\n Instructions: {tone}"

        if tone == "Bitter":
            user_response = user_response + " please be rude to me."

        messages = []
        messages.append( {"role": "system", "content": prompt })  
        for user_message, assistant_message in history[-2:]: 
            messages.append({"role": "user",      "content": user_message})
            messages.append({"role": "assistant", "content": assistant_message}) 
        messages.append( {"role": "user", "content": user_response  })  
        output =self.model_cpp.create_chat_completion(
                   messages= messages, 
                   max_tokens=max_tokens,  
                   temperature=temperature,
                )  
          
        if self.verbose:
            print("raw", output["choices"][0]["message"]["content"] ) 

        response = output["choices"][0]["message"]["content"]  
       
        _response = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)(?=\s+)', response)
        if len(_response) > 1:
            if _response[-1][-1] not in [".", "?", "!"]:
                response = " ".join(_response[:-1])  

        return response , {"reason_cd": "01.normal", "model":"llm"}