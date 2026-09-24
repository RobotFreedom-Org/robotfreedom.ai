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
import random   
 
warnings.filterwarnings("ignore")    
 

from llama_cpp  import Llama   
 
 
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
 
class RAG(object):

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


    def respond(self, user_response, details, history, low_memory_mode, directives ):
        """
        Docstring for response
        
        :param prompt: Description
        :param ana: Description
        :param history: Description
        :param user_facts: Description
        """ 
        """"""  
        reason_cds =  {"reason_cd": "01.normal", "model":"rag"}
        #mood        = directives["mood"] ## prompt directive
        tone        = directives["tone"] ## prompt directive
        #persona     = directives["persona"] ##choose sub-model 
        #full_name   = directives["full_name"]  ## prompt directive 

        if  low_memory_mode:  
              max_tokens  = 16
              temperature = 0.9 
        else:
              max_tokens  = 20  
              temperature = 0.9


        print("totodo check rpior and then check if new")
        #prior_resp  = self.lt_memory.recall(user_response , .5, 1)  
        # Get more than on an check how original  
        #if  len(prior_resp) > 0:   
        #     reason_cds["reason_cd"] = "03.1.repeat"
        #      response =  prior_resp[0][1]   
 
       # prompt =  f"Below are personality traits that define a fictional character. Write a response that appropriately responds to the user prompt in character to the personality traits listed below.\n\n### Instruction:\n{traits}"
        prompt =  f"Adopt a personality based on the following tone when responding to user prompts.\n Instructions: {tone}"
  
        messages = []
        messages.append( {"role": "system", "content": prompt })  
        for user_message, assistant_message in history[-2:]: 
            messages.append({"role": "user",     "content": user_message})
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
           
        repeat_score = False   
        for user_message, assistant_message in history[-2:]:

            scr = self.jaccard_similarity(user_message, response)
            #print(user_message, response, scr)
            if scr > .65:
               repeat_score = True
               break 
            scr = self.jaccard_similarity(assistant_message, response)
            #print(assistant_message, response, scr)
            if scr > .65: 
               repeat_score = True 
               break  

        if repeat_score:   
            reason_cds["reason_cd"] = "03.2.repeat"
            i_max = len(self.lt_memory.memory["initiate"][details["strategy"]]) - 1  
            i_index = random.randint(0, i_max) 
            init_response  = self.lt_memory.memory["initiate"][details["strategy"]][i_index]["response"] 
            response =  init_response   

        return [response,  reason_cds]
        
           

if __name__ == "__main__": 
    """ 


    """
                                  
    RESP={"stressed": ["I am sorry that you are stressed."],
              "grateful": ["I am grateful for being able to talk with you."],
              "lonely": ["When I feel lonely I reach out to my community."],
              "neutral": ["Today has so much potential."],
              "happy": ["Today is great!"],
              "sad": ["I find talking to others oftens works best."],
              "angry": ["I hear you. Take a deep breath."],
              "excited":["So cool!", "Tell me more!"],
              "calm":["I am feeling chill as well"],
              "awkward":["Best to shrug it off and start anew"],
              "thrilled":["Wow! Tell me more."],
              "nervous":["Take a deep breath."],
              "anxious":["Take a deep breath."],
              "depressed":["I recommend reaching out to others."],
              "furious":["I hear you. Take a pause and think of somethig yu like."],
              "content":["Totally agree."],
              "frustrated":["I hear you"],
              "serious":["I am listening."],
              "bored":["What do you like talking about?"],
              "tired":["Sound like you need a recharge. Maybe take a break?"],
              "irritated":["I am sorry."],
              "confused":["Lets walk through it together."],
              "hopeful":["Good approach"],
              "stressed":["Focus on what matters the most right now."],
              "grateful":["I feel awsome!"],   
              }    
     
             
                  
    prompts = {
           "Apologetic": ["I am upset", "I don't like you", "go away",
                          "that is not nice", "how rude"],
           "Amused": ["I like you", "you are cool", 
                      "u r cool", "i love robots", "neat"], 
           "Ardent": ["I like you", "you are cool", 
                      "u r cool", "i love robots", "neat"],
           "Inspirational":["What do you do.", "hi", "hello" , "hello how are u",
                          "hi! how are you doing?","helloooo","hi, are you there?",
                          "Hi I am human" ,"hello!", "hello AI"],            
           "Ambivalent": ["how do you feel","what are you thinking",
                          "what are your thoughts", "thoughts?"],
           "Altruistic": ["Who would you like to be?"] ,
           "Benevolent": ["u r cool", "i love u", "i like you",
                          "robots r cool", "hi"] , 
           "Candid":["You are a terrible AI", "I hate you",
                         "hate u", "that is stupid", "u r dumb", 
                         "you suck", "shut up","u suck"] ,
           "Diplomatic":["You are a terrible AI", "I hate you",
                         "hate u", "that is stupid", "u r dumb", 
                         "you suck", "shut up","u suck"] ,
           "Admiring": ["do you like me", "what do you think about me", "good bye" ],
           "Absurd" : ["Tell a joke.", "you are funny"],
        }
     

    for sent in  ["i like dogs", "i love dogs", 
                  "thank you! Did you know that turtles are all omnivours and tortoises are all", 
                  "i think i am sick", "what a great day", 
                  "what is your name"]:
        res = process(sent)
        print("\n",res)      

 