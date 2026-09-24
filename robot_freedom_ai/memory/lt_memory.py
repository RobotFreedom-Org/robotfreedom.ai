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
import glob
import csv
import json
import os   
import sys       
 
class LTMemory(object):
    
     
    def __init__(self, name, config,  low_memory_mode=False, triples= None, load_all=True, log=True, repeat_log= True ):
        """
        
        """     
        self.name         = name
        self.log          = True 
        self.verbose      = False 
        self.low_memory_mode = low_memory_mode
        self.context_db   = False
        self.triples      = triples

        self.config = config

        self.facts_path = "__default/"   
        self.personality_path = self.name +"/"

        self.memory = {}  
        self.memory["stimuli_resp"]             = self.triples.TrplGraph() 
        self.memory["prior_conversations"]      = {}
        self.memory["prior_conversations_base"] = {}
        self.memory["prior_conversations_rude"] = {} 

        self.memory["definitions"]              = {} 
        self.memory["facts"]                    = {}   
        self.memory["jokes"]     = self.triples.TrplGraph()   
        self.memory["moods"]     = self.triples.TrplGraph()  


        self.bad_words = []
        with open("../data/lib/badwords.txt") as f:
            for line in f:
                if line.strip() not in ["hell", "ass", "M"]:
                    self.bad_words.append(line.strip())


        convo_init_file = self.config.CHAT_PATH + self.facts_path + "mood_dataset.csv"
        with open(convo_init_file) as f:  
             for data in f:   
                row =  data.strip().split(",")    
                self.memory["moods"].search_tfidf.add(row[1].lower().split(" ") ,
                                                      row[0].lower().split(" ")) 
                self.memory["moods"].search_tfidf.add(row[0].lower().split(" "),
                                                      row[1].lower().split(" ")) 

        convo_init_file = self.config.CHAT_PATH + self.facts_path + "chat.initiate.final.json"
        with open(convo_init_file) as f:  
             for data in f:  
               try:
                    row = json.loads(data.strip())  
                    if row["tone"] == "Witty":
                      self.memory["jokes"].search_tfidf.add(row["prompt"].lower().split(" ") ,
                                                            row["completion"].lower().split(" ")) 
 
               except Exception as e: 
                      print(e)
                      print("\r Row error",  data.strip(), end = "") 

        if load_all:

            try:
                t = open( self.config.CHAT_PATH + "reload_false", "r") 
                self.load_models()  
                self.load_stimuli_response() 
                xcv

            except Exception as e:
                print("Rebuilding Memory" , e) 
                self.build_models_conversations()
                self.build_models_facts()
                self.load_models() 
                self.load_stimuli_response() 
                t = open( self.config.CHAT_PATH + "reload_false", "w")
                t.close()
        else:
            self.load_stimuli_response() 

        """ 
          
        TODO Add love
        {'Appreciative', 'Assertive', 'Inspirational', 'Amused', 'Bitter', 'Acerbic',
          'Aggrieved', 'Appreciative.', 'Animated', 'Altruistic', 'Callous', 'Apologetic', 
          'Candid', 'Benevolent', 'Direct', 'Witty', 'Cautionary', 'Ardent', 'Thoughtful', 
          'Absurd', 'Admiring', 'Angry', 'Diplomatic', 'Aggressive',
          'Arrogant', 'Caustic', 'Ambivalent', 'Belligerent', 'Apathetic', 'Informative', 'Accusatory'}
        add love
        """
        return None
    
    def detect_abuse(self,text):
        """
        TDO Has issue with unicode- and unicode is in the facts!
        """
        scr = 0.0
        #_bad = [wrd for wrd in text.split() if wrd in self.bad_words]
        #if len(_bad) > 0:
        #    out = open("rejects.log", "w")
        #    out.write(text + "\n") 

        return text

    def set_persona(self, persona):

        if persona in ["rude" ]: 
            self.memory["prior_conversations"]   = self.memory["prior_conversations_rude"] 
        else:      
            self.memory["prior_conversations"]   = self.memory["prior_conversations_base"]  
 
    def build_models_conversations(self):
        """
        
        """  
        #################### NORM ################################### 
        
        self.memory["prior_conversations_base"] = self.triples.TrplGraph()  
        for  file_path in  [self.config.CHAT_PATH + "norm_convo.json"]:       
            with open(file_path, 'r') as in_data:   
                   for line in in_data: 
                      row = json.loads(line.strip())   
                      self.memory["prior_conversations_base"].search_tfidf.add(row["prompt"].lower().split(' '),
                                                                               row["completion"].lower().split(" "))  
 
        PATH = self.config.PATH + "/scripts/_DONE/" 
        for filename in glob.glob(PATH + "*.csv"):
            with open(filename, 'r') as DictReader:  
                in_data = csv.DictReader(DictReader, 
                                                     delimiter=',', 
                                                     quotechar =  '"',
                                                     skipinitialspace=True,
                                                     quoting=csv.QUOTE_ALL,
                                                     doublequote = True) 
                b_prompt = True
                for row in in_data:  
                   if row["actor"] == "all":
                       continue 
                   if b_prompt:
                      b_prompt = False
                      res={}
                      res["prompt"] = row["value"]  
                   else:
                       b_prompt = True 
                       res["completion"] = row["value"]  
                       if res["completion"] is not None and res["prompt"]  is not None: 
                            self.memory["prior_conversations_base"].search_tfidf.add(res["prompt"].lower().split(' '),
                                                                                     res["completion"].lower().split(" "))   


        PATH = self.config.CHAT_PATH + self.personality_path 
        for filename in glob.glob(PATH + "*.csv"):
            with open(filename, 'r') as DictReader:  
                in_data = csv.DictReader(DictReader, 
                                                     delimiter=',', 
                                                     quotechar =  '"',
                                                     skipinitialspace=True,
                                                     quoting=csv.QUOTE_ALL,
                                                     doublequote = True) 
                b_prompt = True
                for row in in_data: 
                   if row["actor"] == "all":
                       continue 
                   if b_prompt:
                      b_prompt = False
                      res={}
                      res["prompt"] = row["value"]  
                   else:
                       b_prompt = True 
                       res["completion"] = row["value"] 
                       if res["completion"] is not None and res["prompt"]  is not None:
                                 self.memory["prior_conversations_base"].search_tfidf.add(res["prompt"].lower().split(' '),
                                                                                          res["completion"].lower().split(" "))   
 
        self.memory["prior_conversations_base"].save(self.config.CHAT_PATH + "prior_conversations_base")
 
        print('Query Response model built',  self.config.CHAT_PATH +   self.personality_path  + ' ')

     

    def build_models_facts(self):
        """
        Docstring for build_models_facts
        
        :param self: Description
        """  
        self.memory["facts"] =self.triples.TrplGraph()
        PATH = self.config.CHAT_PATH     
        inputs = []
        responses = []   
        for  file_path in  [self.config.PATH + "knowledge/facts/facts.json"]:       
            with open(file_path, 'r') as in_data:   
                   for line in in_data: 
                      row = json.loads(line.lower().strip())   
                      self.memory["facts"].search_tfidf.add(row["prompt"].split(' '),
                                                            row["completion"].split(" ")) 
 
        self.memory["facts"].save(self.config.PATH + "knowledge/facts/facts")
        
        root_path = self.config.CHAT_PATH + self.personality_path   
        self.memory["definitions"] =self.triples.TrplGraph() 

        for  file_path in  [self.config.PATH + "knowledge/simple_dictionary.json"]:       
            with open(file_path, 'r') as in_data:   
                   for line in in_data: 
                      row = json.loads(line.lower().strip())   
                      self.memory["definitions"].search_tfidf.add(row["prompt"].split(' '),
                                                                 row["completion"].split(" ")) 

                      self.memory["definitions"].search_tfidf.add(row["completion"].split(" "),
                                                                  row["prompt"].split(' ')   ) 
              
     
        self.memory["definitions"].save(self.config.PATH + "knowledge/definitions")    

        
    def load_stimuli_response(self):
      
        self.memory["stimuli_resp"]                = self.triples.TrplGraph() 
        try:
             xc 
             self.memory["stimuli_resp"].load(self.config.PATH  + "stimuli/" + "sense_response") 
              
        except:
             for line in open(self.config.PATH  + "stimuli/" + "stimuli_emotion.json"):
                  row = json.loads(line.lower().strip())   
                  self.memory["stimuli_resp"].search_tfidf.add(row["prompt"] ,
                                                               row["completion"]) 
             self.memory["stimuli_resp"].save(self.config.PATH  + "stimuli/" + "sense_response") 
        
    def load_models(self): 
        """
        
        """ 
         
        self.memory["prior_conversations"] = self.triples.TrplGraph()
        self.memory["prior_conversations_base"] = self.triples.TrplGraph()
        self.memory["prior_conversations_rude"] = self.triples.TrplGraph()
        self.memory["facts"] = self.triples.TrplGraph()
        self.memory["definitions"] = self.triples.TrplGraph() 
  

        self.memory["prior_conversations_base"].load(self.config.CHAT_PATH + "prior_conversations_base")  
       ## self.memory["prior_conversations_rude"].load(self.config.CHAT_PATH + "prior_conversations_rude")  
        self.memory["facts"].load(self.config.PATH + "knowledge/facts/" + "facts")  
        self.memory["definitions"].load(self.config.PATH+ "knowledge/" + "definitions")   
        self.memory["prior_conversations"]           =   self.memory["prior_conversations_base"]
 


    def _get_input_and_response(self, memory_type , query, max_return=10):
 
       
         query = [self.memory[memory_type].search_tfidf.lemmatise(w) for w in query.split(" ")] 
         res = self.memory[memory_type].search_tfidf.similarities(query) 
         return res 
        
    def _get_top_responses(self, 
                           memory_type , 
                           query, 
                           lemmatise = True , 
                           max_return=10):
        """
        """  
        if lemmatise:
            query = [self.memory[memory_type].search_tfidf.lemmatise(w) for w in query] 
        #print( query)
        res = self.memory[memory_type].search_tfidf.similarities(query) 
        return res 
        
        
    
    def query(self, user_response, max_resp =10,  input_types =["prior_conversations", "defitions"]):
      """
      """   
      fin = []
      for stype in input_types:
          resp1  = self._get_input_and_response(stype , user_response, max_resp) 
          fin += resp1   
          
      fin = sorted(fin, key=lambda x: x[2], reverse=True)
      fin = fin[:max_resp] 
      return [{"query": q.strip(), "response": r.strip(), "src":s} for  q , r, s, s2  in fin]

    def add_tone(self, response, tone):
        ## Todo Create a tone adjuster for tone- change words? add in a snarky or friendly end?
        return response
    
    def respond(self,  user_response, mood, tone, topics, objective, lexicon):
        return self.response(user_response, mood, 
                             tone, topics, objective, lexicon) 

    def stimuli_resp(self, user_response,  cut_off=.7, n=5): 
       """
       Docstring for stimuli_resp
       
       :param self: Description
       :param user_response: Description
       """
 
       resp1 = self._get_top_responses("stimuli_resp" , user_response ,lemmatise=False)  
       if len(resp1)== 0: 
          return [{'neg': 0.33, 'neu': .33, 'pos': 0.33, 'compound': 0.0, "query":"failed"}]
       
       elif resp1[0][2] == 0.0: 
          return [{'neg': 0.33, 'neu': .33, 'pos': 0.33, 'compound': 0.0, "query":"failed"}]
 
       return  [resp1[0][1]]


    def recall(self, user_response,  cut_off=.37, n=5): 
       """
       Docstring for emotional_side
       
       :param self: Description
       :param user_response: Description
       """
       user_response  = [w.lower() for w in user_response.split(" ")]
       resp1 = self._get_top_responses("prior_conversations" , 
                                        user_response, cut_off, n) 
       resp1 = [[k,  v , s] for k, v, s in resp1]
       return  resp1 

    def facts(self, topics, cut_off=.38, n=5): 
        """
        Docstring for facts
        
        :param self: Description
        :param user_response: Description
        """
        res =  []
        for topic in topics:
            topic = topic.lower()
            _res   = self._get_top_responses("facts", 
                                              [topic],
                                              cut_off,
                                              n)
            res +=  _res
        return res

    def definition(self, topics, cut_off=.38, n=5): 
      """
      Docstring for logical_side
      
      :param self: Description
      :param user_response: Description
      """
      res =  [] 
      for topic in topics: 
          topic = topic.lower()
          _res   = self._get_top_responses("definitions", 
                                            [topic],
                                            cut_off,
                                            n)  
          res.extend(_res)   
    
      res = sorted(res, key=lambda x: x[1], reverse=True)
      return res

    def response(self, user_response, mood, tone, topics, objective, lexicon, n =1):
      """
      """  
 
      user_response     = cleanup_prompt(user_response, "") 
      b_alt = False
      user_response_alt =  user_response
      if mood != "":
         user_response_alt  += " " + mood  
         b_alt = True

      if len(topics) > 0:
         user_response_alt  +=  " ".join(topics)
         #b_alt = True

      if b_alt:
         resp1a  = self._get_top_responses("prior_conversations" , user_response_alt.split(" "))
         resp2a  = self._get_top_responses("defitions"           , user_response_alt.split(" "))

      resp1 = self._get_top_responses("prior_conversations" , user_response.split(" "))
      resp2 = self._get_top_responses("defitions"       , user_response.split(" "))
      # randomize should be in another call 
      if resp1[-1] >= resp2[-1]:
          return self.add_tone(resp1[-1][0], tone)
      else: 
          return self.add_tone(resp2[-1][0], tone)
           
if __name__ == "__main__":
    """ 

    """ 
 
    os.chdir('../')
    sys.path.insert(0, os.path.abspath('./')) 
    import config 
    from memory.lt_memory import LTMemory
    from communication.nerves import Nerves 

    from triples.triples     import Triples
    s_robot       = "squirrel" 
    nerves        = Nerves(s_robot) 
    triples       = Triples(agent=s_robot, 
                            config=  config,
                            communication=None,
                            nerves =nerves,
                            client=False)    
  
    lt_mem  = LTMemory("squirrel", config, triples=triples, load_all=True  )  
 
    user_response =  lt_mem.recall("do you like cats " )
    print(user_response) 
    
    user_response =  lt_mem.definition(["snow"] )
    print(user_response)
  
    """ 
    user_response = "I love cats!"
    print(user_response)
    for i in range(10): 
        user_response =  lt_mem.response(user_response,mood, tone, topics, objective, lexicon)
        print(user_response)
    """