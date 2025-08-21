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
import warnings
warnings.filterwarnings("ignore") 
import csv
import time  
import os    
import random  
import shutil  
import sys 

if __name__ == "__main__":  
    from lib.text_utilities import *
else:
    from .lib.text_utilities import *
 

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM  
from sklearn.metrics.pairwise import cosine_similarity 
import nltk 

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
try:
   nltk.download('popular', quiet=True)    
except:
    pass

import yake 
kw_extractor = yake.KeywordExtractor(lan="en",n=1) 


is_noun = lambda pos: pos[:2] == 'NN'  
ROBOT_ROLES = ["interviewing", "educating", "conversing"]   
ROLES       =  ["ai","response", "robot" , "assistant" ,  "machine" , "two",
                 "three", "four", "with",  "stranger",  
                 "man", "human", "customer", "system", ]  

objective_to_situation   =   {"engagement":  "You want to encourage the conversation forward.", 
                              "defuse": "You are helping a friend with a problem." , 
                               "inspire" :  "You want to inspire people.",
                               "relax" : "You want to keep everyone calm.",  
                               "disengagement":  "You are trying to get someone to relax." ,  
                               "quiet":  "You are trying to get someone to be quiet." } 
       
 
def input_cleanup(input):
    """
    
    """
    return input 

class OllamaRF(object):
    """
    
    """ 

    def __init__(self, config, cognitive_control, personality, 
                  lt_memory, st_memory, 
                  full_name, name ,topics , 
                  tones=["Appreciative"], 
                  params= {},   
                  log=True,
                  repeat_log= True,
                  low_memory_mode=False):
        """
 
        """  

        self.log          = True
        self.tones        = tones
        self.verbose      = False 
        self.low_memory_mode = low_memory_mode
        self.context_db   = False
        self.config       = config
        self.cognitive_control    = cognitive_control
        self.personality  = personality
        self.persona      = personality.persona
        self.st_memory    = st_memory
        self.lt_memory    = lt_memory
        self.history = []
        self.memory        = self.lt_memory.memory  
        self.model_path    = name   
        self.os            = self.config.OS 
        self.roles         = ROLES  
        self.tokens        = [role + ":" for role in self.roles]    

        self.resp_fit_threshold = .7
        self.llm_tries = 6
        self.assure_question = True
        self.min_resp_len = 2
        self.min_overlap = .55
        self.min_key_wrd_scr = .04

        _t = open("tmp.txt", "w")
        _t.write(self.persona )
        _t.close()

        if 'input_cleanup' in params: 
           self.input_cleanup =  params["input_cleanup"] 
        else:
           self.input_cleanup = input_cleanup 

        self.cleanup       = ["'",  "`",  '"']

        self.p_topics   = []
        self.p_topics_2 = []
        self.r_topics_2 = []
        self.r_topics   = []

        if self.os == 'LINUX': 
            self.verbose = False
            self.low_memory_mode = True
 
        self.base_template = [ {'role': "system", 
                        'content': "You are a {mood} robot {tone}.  {persona} {situation} Your name is " + full_name +"." },
                        ]    
        
        self.just_the_facts_template =  [("system", "You are a robot who responds succinctly using as few words as possible." ),
                                         ("human", "{topic}"),
                                         ("ai", "")
                                       ]    
        if len(topics) > 0: 
            self.base_template = [ {'role': "human", 
                          'content': "Please try to stay on the topic of " + topics[0].replace('_', " ")  +"." },
                        ] 
            self.base_template = [ {'role': "ai", 
                          'content': "I will try and stay on the topic of " + topics[0].replace('_', " ")  },
                        ] 

 
        self.log_name = "chat_ollama.log"
        if repeat_log == False:
            if os.path.exists(self.log_name): 
                 _log_name = "chat_ollama." + self.config.START_DT_F + ".log"
                 dest = shutil.move(self.log_name, _log_name)   

        f_log = open(self.config.LOGS_PATH + self.log_name, "a")
        f_log.write("Started new session\n")  
        f_log.close()

        self.load_models(name , params, topics, tones)
        
        
    def load_models(self,robot, params, topics, tones=[]): 
        """
        
        """     
        self.prompts_end  = []
        self.prompts_end.append( ("human", "{topic}"))
        self.prompts_end.append( ("ai", "")) 

        if self.low_memory_mode is False:
            #scripted_response
            #just_the_facts
            self.model_just_the_facts   = OllamaLLM(model="scripted_response", 
                                                    temperature=0.8,  
                                                    num_predict=19)  
        
            self.prompt_just_the_facts = ChatPromptTemplate(self.just_the_facts_template )
            self.chain_just_the_facts = self.prompt_just_the_facts | self.model_just_the_facts
        
        self.reset_prompt(robot, params, topics, tones)

    def reset_prompt(self,robot, params, topics, tones=[]): 
        """
        
        """    

        self.tones  = tones
        self.topics = topics
        self.params = params
        self.robot  = robot 

        if self.low_memory_mode: 
 
            """  
            #self.prompt  = ChatPromptTemplate(self.prompts + self.prompts_end ) 
            self.prompt   = ChatPromptTemplate(self.just_the_facts_template) 
            self.model  = OllamaLLM(model="tinyllama2", 
                                    temperature=0.98,  
                                    num_predict=35) 
            
            self.chain = self.prompt | self.model
            """  
            from llama_cpp  import Llama 
            #https://github.com/abetlen/llama-cpp-python/issues/657
           # self.model_cpp  = Llama("../data/llms/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            #                        n_ctx = 250,
             #                       verbose=False)
            self.model_cpp  = Llama("../data/llms/scripted_response.gguf", 
                                    verbose=False) #, 
                                  #  logits_all=True)

            return True
        else:
            prompts = []
            for message in self.base_template:
                prompts.append( (message["role"], message["content"]) )
    
            human_resp =["Hello. How are you?",  
                         "What are you thinking about?",
                         "What did you say?",
                         "Do you have any thoughts?"
                         "How are you?",
                         "It is a great day!",
                         "How do you feel?",
                         "Any ideas?",
                         "I feel happy.",
                         "Lets do something!"]
            i_starts = len(human_resp) - 1
            i_num = 0
            if len(tones)  > 0 :
                for tone in tones: 
                   if tone not in self.memory["initiate"]:
                       break
                   for row in self.memory["initiate"][tone]:
                       i = random.randint(0, i_starts)
                       prompts.append( ("human", human_resp[i])      )  
                       prompts.append( ("ai"   , row["response"][0]) ) 
                       i_num += 1
                       if i_num > 1:
                           break 

            arg = self.config.CHAT_PATH +  self.model_path  + "/" + robot + ".base.csv" 
            with open(arg, 'r') as DictReader:  
                    in_data = csv.DictReader(DictReader, 
                                             delimiter=',', 
                                             quotechar =  '"',
                                             skipinitialspace=True,
                                             quoting=csv.QUOTE_ALL,
                                             doublequote = True) 
                    for row in in_data: 
                        prompts.append( (row["actor"], row["value"]) )  

            if len(topics) > 0: 
  
                for topic in topics:  
                    _topic = topic.replace(" ", "_")
                    arg = self.config.CHAT_PATH +  self.model_path  + "/" + robot + "." + _topic + ".csv"
                     
                    if os.path.exists(arg) is False:  
                        in_data = self.lt_memory.query(topic)
                         
                        for row in in_data: 
                             prompts.append( ("human", self.input_cleanup(row["query"]) ))  
                             prompts.append( ("ai"   , self.input_cleanup(row["response"])) )  
                          
                    else:
                         
                        with open(arg, 'r') as DictReader:  
                            in_data = csv.DictReader(DictReader, 
                                                     delimiter=',', 
                                                     quotechar='"',
                                                     skipinitialspace=True,
                                                     quoting=csv.QUOTE_ALL,
                                                     doublequote=True)
                       
                            for row in in_data: 
                                prompts.append( (self.input_cleanup(row["actor"]),  
                                             self.input_cleanup(row["value"])) )  
           
            if "context" in params:

                arg = self.config.CHAT_PATH +  self.model_path  + "/" + robot + "." + params["context"].replace(" ", "_")  + ".csv"
                            
                with open(arg, 'r') as DictReader:  
                    in_data = csv.DictReader(DictReader, 
                                             delimiter=',', 
                                             quotechar='"',
                                             skipinitialspace=True,
                                             quoting=csv.QUOTE_ALL,
                                             doublequote=True)
                       
                    for row in in_data: 
                        prompts.append( (self.input_cleanup(row["actor"]),  
                                         self.input_cleanup(row["value"])) )
                  
             
            self.prompts = prompts  
            self.prompt  = ChatPromptTemplate(self.prompts + self.prompts_end ) 
            # "tinyllama" ollama pull llama3.2
            self.model   = OllamaLLM(model="tinyllama", 
                                     temperature=0.9,  
                                     num_predict=150)
 
            self.chain = self.prompt | self.model

        return True   
  
    
    def parse_response(self, response):
        """
        
        """ 

        _tokens = {tok : pos for pos,tok in enumerate(self.tokens)}
        response = response.replace("\n", " ")
        response = re.sub(r' {2,}', ' ', response)
       # toks      = [[word, ipos  , -1] for ipos, word in enumerate(response.split()) if word.lower() in self.tokens]
        toks = [[word, ipos +1  , -1, _tokens[word.lower()]] for ipos, word in enumerate(response.split()) if word.lower() in _tokens]


        if len(toks) > 0:

            ptoks = [v[1] for v in toks] 
            ptoks.append(None)
            ptoks.pop(0)
            toks = [[ret[0], ret[1], ptoks[ipos], ret[3]] for ipos, ret in enumerate(toks)]
            sorted_list = sorted(toks, key=lambda x: x[3], reverse=False)


            _response = " ".join(response.split(" ")[sorted_list[0][1]: sorted_list[0][2]])
            
            resp = return_sentence(_response, self.p_topics) 
        else:
            resp = return_sentence(response, self.p_topics) 
     
        if resp.strip() == "": 
            resp = "I am sorry could you repeat what you said?" 
            print("ERROR", response)

        resp = resp.replace(":", " ")
        return resp
     
    def respond(self, user_response,
                   mood="happy",
                   tone="Appreciative",
                   user_topics=[],
                   objective ="relax",
                   lexicon="Appreciative",
                   situation = "You are having a chat with your friends."  ):  
      if self.low_memory_mode:
          self.b_keywords_only = False
          user_response  = cleanup_prompt(user_response, "") 
          ## could just do word freq or top
          if len(user_response) > 250:
              user_response = user_response[:250]
          if self.b_keywords_only:
                keywords = kw_extractor.extract_keywords(user_response)  
          else:
                keywords = [] 

          if len(keywords) > 0:  
              _keys  = [wrd for wrd , scr in keywords if scr > .1 ] 

              tokenized = nltk.word_tokenize(" ".join(_keys))
              _nouns    = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)] 
              fin = ["cats", .1] 
              for wrd, scr in keywords:
                  
                  if wrd in _nouns:
                      scr += .25
                  if scr > fin[1]:
                      fin = [wrd, scr]
 
              """  
              f_out = open("extract_keywords.txt", "a") 
              f_out.write(str(keywords) + "\n")
              f_out.write(str(fin) + "\n")
              f_out.close()
              """ 
              if len(keywords) > 0:
                  t_user_response = "Please elaborate on " + fin[0] + "."
              else:
                  t_user_response  = user_response   
              output =self.model_cpp.create_chat_completion(
                 messages=[
                     {
                         "role": "system",
                         "content": "You are a " + self.persona + " assistant that responds quickly.",
                     },
                     {"role": "user", "content": t_user_response },
                 ], 
                 max_tokens=64,  
                 temperature=0.7, 
              ) 
              response = output["choices"][0]["message"]["content"] 
          else:     
              
              messages = []
              
              messages.append( {"role": "system", "content": "You are a happy and funny kid who likes cats and live in San Francisco." })
              for user_message, assistant_message in self.history:
                    messages.append({"role": "user", "content": user_message})
                    messages.append({"role": "assistant", "content": assistant_message})
              messages.append( {"role": "user", "content": user_response })

              output =self.model_cpp.create_chat_completion(
                 messages= messages, 
                 max_tokens=16,  
                 temperature=0.9,
              )  
              response = output["choices"][0]["message"]["content"]  

 
          _response = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)(?=\s+)', response)
          if len(_response) > 1:
              if _response[-1][-1] not in [".", "?", "!"]:
                  response = " ".join(_response[:-1])

          ai_response   = self.parse_response(response)
          self.history.append([user_response, ai_response]) 
          self.history = self.history[-5:]
              
      else:
 
          org_user_response = user_response  
          user_response     = cleanup_prompt(user_response, "") 
          situation         = objective_to_situation[objective]
           
          if self.verbose:
            print( mood ,tone , user_topics ,objective  , lexicon ,  situation  )

          if len(user_topics) == 0 :
              if len(self.tones) >  0:
                  if  tone != self.tones[0]:  
                      self.reset_prompt(self.robot, self.params, self.topics, [tone]) 
            
          elif user_topics[0] != self.topics[0] or  tone != self.tones[0]:   
              self.reset_prompt(self.robot, self.params, user_topics, [tone]) 
  
          if self.verbose: 
             start = time.time() 
          
          if len(user_topics) == 0: 
               
              self.p_topics_2 = self.p_topics  
              keywords = kw_extractor.extract_keywords(user_response)   
              _p = []
              if len(keywords) > 0: 
                   _p = list(set([wrd for wrd , scr in keywords if scr > self.min_key_wrd_scr ] ))
                   tokenized = nltk.word_tokenize(" ".join(_p))
                   _p = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)] 

              if len(_p) > 0:
                  self.p_topics = _p   
              else:
                  self.p_topics = ["cats"]  
          else:
              self.p_topics = user_topics

          if self.verbose: 
             end = time.time()
             print(end - start) 
             print(mood, tone, self.persona, situation, self.p_topics)

          if self.context_db:
              memory =  self.lt_memory.query(self.p_topics) 
              if len(memory) > 0:
                  self.prompt = ChatPromptTemplate(self.prompts + self.prompts_end )
                  self.chain = self.prompt | self.model  

          user_response  = user_response.strip()

          if user_response[-1] not in [".", "!" ,"?"]: 
              user_response = user_response + "."

          if user_response[-1] != "?" and self.assure_question:
              user_response = user_response + " What are your thoughts?"  

          all = []
          persona = self.persona
          _tone = f"who responds in a {tone} manner"   
          for i in range(self.llm_tries): 
                  
                  if i == 2:
                       persona = ""

                  if i == 3:
                       situation = ""

                  if i == 4:
                       _tone  = "" 
  
                  if 3==4:#i == self.llm_tries - 1:
                      t_user_response = "Please provide a response on the following topics:  " + ",".join(self.p_topics) +"."
                      response = self.chain_just_the_facts.invoke({"topic":t_user_response})
                      
                  else:
                      response = self.chain.invoke({"topic":user_response ,
                                                      "mood":mood,
                                                      "tone":_tone,
                                                      "persona": persona,
                                                      "situation":situation })#,
                                                     #"lexicon":lexicon   } )  
                  ai_response = self.parse_response(response)   
                  i_len_rsp = len(ai_response)
                  adj   = 1/float(i_len_rsp)
                 

                  i_overlap = 0.0
                  for wrd in ai_response.lower().split(' '):
                      if wrd in user_response.lower().split(' '):
                          i_overlap += 1.0  
  
                  adj2   =  float(i_len_rsp)/300.0
                  over_lap_scr = i_overlap / float(len(ai_response)) 
                  if  over_lap_scr* adj2 > self.min_overlap   :
                      ai_response = "I am not sure I am following what you said."  
                      all.append([ai_response, response, -1])
                      continue

                  if i_len_rsp < self.min_resp_len : 
                       ai_response = "I am not sure I am following what you said."  
                       all.append([ai_response, response, -1])
                       continue 
                  
                  mx_src = -1  
                  
                  for topics in  [self.p_topics]: 
                     if len(topics) > 0:
                         fnd = 0  
                         for topic in topics:
                             if  ai_response.lower().find(topic) > -1: 
                                 fnd += 1.0 
                         t = float(fnd) / float(len(topics))  
                         t = t*adj  
                         if t > mx_src:
                              mx_src = t  
                         if t > self.resp_fit_threshold:
                              break  
                         
                  all.append([ai_response, response, mx_src])
                  if mx_src > self.resp_fit_threshold:
                       break   
                  
          all = sorted(all, key = lambda x : x[2] , reverse =True )  
          ai_response = all[0][0]  
          response    = all[0][1]   
               
          self.prompts.append(('ai', ai_response)) 
          self.prompt = ChatPromptTemplate(self.prompts + self.prompts_end )
          self.chain = self.prompt | self.model

          keywords = kw_extractor.extract_keywords(ai_response)    
          self.r_topics_2 = self.r_topics 

          if len(keywords) > 0: 
              self.r_topics = list(set([wrd for wrd, scr in keywords if scr > self.min_key_wrd_scr]))
              tokenized = nltk.word_tokenize(" ".join(self.r_topics))
              _p = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)] 
              if len(_p) > 0:
                  self.r_topics = _p  
 
      if self.log:
          f_log = open(self.config.LOGS_PATH + self.log_name, "a")  
          for rule in self.cleanup: 
              user_response.replace(rule, "") 
              ai_response.replace(rule, "") 
  
          f_log.write('human,speak,"'   + user_response + '"\n')   
          f_log.write('ai,speak,"'      + ai_response  + '"\n')  

          if self.verbose:
            org_user_response.replace('"', "'") 
            for rule in self.cleanup:
                org_user_response.replace(rule, "")  
                response.replace(rule, "") 
            f_log.write("<topics> " + ','.join(self.p_topics) + ";" + ','.join(self.r_topics) +"</topics>\n")
            f_log.write("<full_prompt>" + org_user_response + "</full_prompt>\n")  
            f_log.write("<full_response>" + response + "</full_response>\n\n")  
            
      return ai_response  
           
           
if __name__ == "__main__": 
    """ 

    """ 
    os.chdir('../../')
    sys.path.insert(0, os.path.abspath('./')) 
    import config
    from ai.cognitive_control import CognitiveControl 
    from ai.personality import Personality 
    from memory.st_memory import STMemory
    from memory.lt_memory import LTMemory

    st_mem     =  STMemory("squirrel", config, False)
    mem        =  LTMemory("squirrel", config, False) 
    personality   = Personality("squirrel", config, {} )
    cognitive_control  = CognitiveControl("squirrel", config, {}, personality,False)  
    
    topics    = [ ] 
    tones     = "Bitter"   
    chat      = OllamaRF(config, cognitive_control, personality, 
                     mem, st_mem, 
                     "Squirrel" , 'squirrel', topics ,  
                     [tones] , {}, True, repeat_log=False) 
    
    b_test_intro = False
    if b_test_intro:
        for user_input in [ "what pet do you like?" , 
                       "i live in san francisco.", 
                       'i like cats.', 
                       'where is the screw driver.', 
                       'where do i live?',
                       'what pets do i like?',
                       'Where is the capital of France?']:
 
            print('CHAT: ' + user_input)
            resp = chat.respond(user_input)  
            print("RESP : " + resp) 

    while True:
         
       user_input = input('CHAT: ') 
       resp = chat.respond(user_input) 
       print("RESP : " + resp)  
     
  