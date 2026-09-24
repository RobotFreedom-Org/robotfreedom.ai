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

from nltk import pos_tag, word_tokenize 
 
warnings.filterwarnings("ignore") 
import csv     
 
 
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

from nltk.corpus import stopwords

Ideas = [ ["Idea"          , "Concept" ], 
              ["Question"      , "Self"],   
              ["Question"      , "Speaker" ],
              ["External_Idea" , "Concept"],
              ["Speaker_Idea"  ,  "Concept"   ]] 
     
Ideas_query = [ ["Idea"   , "Concept" ], 
                ["External_Idea", "Concept"] ]    

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM  

class RAGOllama(object):

    def __init__(self,  st_memory, lt_memory, topics, full_name , verbose=False):
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
        self.llm_tries = 0

        self.prompts_end  = []
        self.prompts_end.append( ("human", "{topic}"))
        self.prompts_end.append( ("ai", "")) 
 
 
        self.model        = OllamaLLM(model="scripted_response", 
                                                    temperature=0.8,  
                                                    num_predict=19)  
        
        self.base_template = [ {'role': "system", 
                        'content': "You are a {mood} robot {tone}.  {persona} {situation} Your name is " + full_name +"." },
                        ]    
        
        self.full_template =  [("system", "You are a robot who responds succinctly using as few words as possible." ),
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
         
        self.prompt  = ChatPromptTemplate(self.full_template )
        self.chain   = self.prompt  | self.model 
         
        
    def reset_prompt(self,robot, params, topics, tones=[]): 
         
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

    def close(self):
         """
         """
         pass 
 

    def respond(self, user_response, details, history,
                low_memory_mode,b_roll_switch,
                parse_response,  
                tone,user_topics ,get_keywords,
                assure_question,directives,
                on_tooic ):
          """
          Docstring for response
          
          :param prompt: Description
          :param ana: Description
          :param history: Description
          :param user_facts: Description
          """  
          reason_cds   = {}
          self.prompts = []
          self.resp_fit_threshold = .7
          self.llm_tries = 6
          self.assure_question = True 
          self.min_resp_len = 2
          self.min_overlap = .55
          self.min_key_wrd_scr = .04

          persona      = directives["persona"]   
          mood         = directives["mood"]       
          tone         = directives["tone"]       
          user_topics  = directives["user_topics"]
          objective    = directives["objective"]   
          objective_dsc    = directives["objective_dsc"] 
     
          
          if len(user_topics) == 0: 
                
              tokens    = word_tokenize(user_response)  
              tags      = pos_tag(  tokens)
              tags_lkup = {k:v for k, v in tags} 
              details["tags"] = tags 
              _p = get_keywords(user_response, tags)   
              if len(_p) > 0:
                  self.p_topics = _p   
              else:
                  self.p_topics = ["cats"]  
          else:
              self.p_topics = user_topics
 
          user_response  = user_response.strip()

          if user_response[-1] not in [".", "!" ,"?"]: 
              user_response = user_response + "."

          if user_response[-1] != "?" and  assure_question:
              user_response = user_response + " What are your thoughts?"  

          all   = [] 
          _tone = f"who responds in a {tone} manner"   
          for i in range(self.llm_tries): 
                  
                  if i == 2:
                       persona = ""

                  if i == 3:
                       objective_dsc = ""

                  if i == 4:
                       _tone  = "" 
  
                  if i  > 4:#i == self.llm_tries - 1:
                      t_user_response = "Please provide a response on the following topics:  " + ",".join( [t for t,s in self.p_topics]) +"."
                      response = self.chain.invoke({"topic":t_user_response})
                      
                  else:
                      response = self.chain.invoke({"topic":user_response ,
                                                      "mood":mood,
                                                      "tone":_tone,
                                                      "persona": persona,
                                                      "situation":objective_dsc }) 
                      
                  ai_response , scr = parse_response(response, [])   
                  i_len_rsp = len(ai_response)
                  adj       = 1/float(i_len_rsp)
                 
                  i_overlap = 0.0
                  for wrd in ai_response.lower().split(' '):
                      if  user_response.lower().find(wrd) > -1:
                          i_overlap += 1.0  
  
                  adj2   = 1.0# float(i_len_rsp)/300.0
                  over_lap_scr = i_overlap / float(len(ai_response)) #  overlap_scr(ai_response, user_response )
                  adj2   = 1.0
                  if  over_lap_scr* adj2 >  self.min_overlap   :
                      ai_response = "I am not sure I know what to say about that."  
                      all.append([ai_response, response, -1, over_lap_scr])
                      continue

                  if i_len_rsp <  self.min_resp_len : 
                       ai_response = "I am not sure I am following what you said."  
                       all.append([ai_response, response, -1, over_lap_scr])
                       continue  
                  
                  on_topic_scr = on_tooic(ai_response, self.p_topics  )
                  all.append([ai_response, response, on_topic_scr, over_lap_scr])
                     
                  if on_topic_scr  >  self.resp_fit_threshold:
                       break   
                  
          all = sorted(all, key = lambda x : x[2] , reverse =True )   
          
          ai_response = all[0][0]  
          response    = all[0][1]   
               
          self.prompts.append(('human', response)) ##TDH Feb 13 2026 - IT was missing
          self.prompts.append(('ai'   , ai_response)) 
          self.prompt = ChatPromptTemplate(self.prompts + self.prompts_end )
          self.chain = self.prompt | self.model 
          
          tokens    = word_tokenize(ai_response)  
          tags      = pos_tag(  tokens)  
          _keywrds = get_keywords(ai_response, tags)    
          if len(_keywrds) > 0: 
              self.r_topics = _keywrds
          return ai_response,  reason_cds