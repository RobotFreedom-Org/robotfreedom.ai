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

import sys 
import time  
import os   
import csv 
import random  
import warnings
import json
warnings.filterwarnings("ignore") 
from difflib import SequenceMatcher
import shutil  
   
if __name__ == "__main__":  
    from lib.text_utilities import * 
else:
    from .lib.text_utilities import *   
 
import nltk 
from nltk.sentiment import SentimentIntensityAnalyzer  
from nltk import pos_tag, word_tokenize, RegexpParser
from nltk.tree import Tree
from nltk.corpus import stopwords    
 
try:
    nltk.data.find('tokenizers/punkt')  
except LookupError:
    nltk.download('punkt')  
    
 
ROBOT_ROLES = ["interviewing", "educating", "conversing"]   
ROLES       =  ["ai","response", "robot" , "assistant" ,  "machine" , "two",
                 "three", "four", "with",  "stranger",  
                 "man", "human", "customer", "system", ]  

 

def input_cleanup(input):
    """
    
    """ 
    return input  

  
  
ASK_REPEAT =["Sorry, what was that?",
             "Excuse me, could you repeat that?",
             "Pardon me, I did not catch that.",
             "Could you say that again, please?",
             "I am sorry, I missed what you said.",
             "Could you repeat that more slowly, please?",
             "What did you say?",
             "I did not hear you, could you repeat that?",
             "Sorry, could you speak up a bit?",
             "Can you please say that one more time?",
             "Sorry, I did not quite get that.",
             "I am having trouble hearing you, could you say it again?",
             "Would you mind repeating that?",
             "Sorry, could you say that once more?",
             "Could you repeat that, I missed it the first time.",
             "Excuse me, I did n0t understand what you said.",
             "Could you repeat that more clearly?",
             "Sorry, what was it that you said?",
             "I am sorry, I did not catch your words, can you please repeat it?",
             "Can you please say that again, I did not hear it properly."]
"""
INT_DEFINE
INT_ADVANCER
INT_REPLY
INT_INTRODUCE
INT_INQUIRY
INT_STATEMENT
INT_SHARING
INT_DEFITION
INT_DEFINITION
"""  


def edit_distance(word1, word2):
    # Validate inputs
    if not isinstance(word1, str) or not isinstance(word2, str):
        raise TypeError("Both inputs must be strings.")

    len1, len2 = len(word1), len(word2)
    if len1 > 25:
        word1 = word1[:25]
        len1 = len(word1)

    if len2 > 25:
        word2 = word2[:25]
        len2 = len(word2)

    # Create a DP matrix of size (len1+1) x (len2+1)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    # Initialize base cases
    for i in range(len1 + 1):
        dp[i][0] = i  # deletions
    for j in range(len2 + 1):
        dp[0][j] = j  # insertions

    # Fill the DP matrix
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if word1[i - 1] == word2[j - 1]:
                cost = 0  # characters match
            else:
                cost = 1  # substitution cost

            dp[i][j] = min(
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )

    if len1  == 0 or  len2 == 0:
        return 0
    elif len1 < len2:
        return dp[len1][len2]/float(len1)
    else:
        return dp[len1][len2]/float(len2)

def is_noun(word, tagged):
    """
    Check if a given word is a noun using POS tagging and WordNet.
    """
    if not isinstance(word, str) or not word.strip():
        raise ValueError("Input must be a non-empty string.")
 
    # Check if any token is tagged as a noun (NN, NNS, NNP, NNPS)
    for _, tag in tagged:
        if tag.startswith('NN'):
            return 1 

    # Fallback: Check WordNet synsets for noun type
    synsets = wn.synsets(word)
    for syn in synsets:
        if syn.pos() == 'n':
            return 1

    return 0

def svo_components(sentence, tagged):
    """
    Extract Subject, Verb, Object, Object Complement, and Modifiers from a sentence.
    This is a heuristic approach using POS tagging and chunking.
 
    """
    # Tokenize and POS-tag
    sentence = sentence.strip()
    sentence = sentence[0].upper() + sentence[1:]

    if sentence[-1] not in ['.', '!', '?']:
         sentence += "."
 

    # Define a chunk grammar for NP (noun phrase), VP (verb phrase), PP (prepositional phrase)
    grammar = r"""
        NP: {<DT|PRP\$>?<JJ.*>*<NN.*>+}   # Noun phrase
        VP: {<VB.*><NP|PP|CLAUSE>+$}      # Verb phrase
        PP: {<IN><NP>}                    # Prepositional phrase
        CLAUSE: {<NP><VP>}                # Clause
    """

    cp = RegexpParser(grammar)
    tree = cp.parse(tagged)

    subject = verb = obj = obj_comp = modifiers = 'na'

    # Heuristic extraction 
    for subtree in tree:
       
        if isinstance(subtree, Tree):
            label = subtree.label()
            words = " ".join(word for word, tag in subtree.leaves()) 
        else: 
            words, label = subtree 

        if label in ["NP" , "PRP"] and subject  == "na":
                subject = words.lower()

        elif label in ["VP"] and verb  == "na":
                # First word in VP is usually the main verb
                verb = subtree.leaves()[0][0].lower()
                # Remaining words might be object or complement
                rest = " ".join(w for w, t in subtree.leaves()[1:])
                if rest:
                    obj = rest 
        elif label in ( "VBZ", "VBP", 'VBD', 'VBG', 'VBN'):
                verb = words 

        elif label in ( "NNS", "NP", "PRP", 'MD', 'NN', 'NNP', 'NNPS'):
                obj = words 

        elif label in ("PP", "JJ"):
                if modifiers  == "na":
                    modifiers = words.lower()

    # Simple heuristic for object complement (adjective or noun after object)
    if obj:
        obj_tokens = word_tokenize(obj)
        obj_tags = pos_tag(obj_tokens)
        if len(obj_tags) > 1 and obj_tags[-1][1] in ("JJ", "NN", "NNS"):
            obj_comp = obj_tags[-1][0]
 
    return {
        "Subject": [subject],
        "Verb": [verb],
        "Object": [obj],
        "Complement": [obj_comp],
        "Modifier": [modifiers]
    }  

def filter_text(text):

    b_found  = False
    for wrd in ["negro", "jesus", "god", 
                "nazi", "tran ", "trans ", "gay",
                "queer", "lezbian", "negro",
                "bdsm","porn", "lord allmighty",
                "feminimism", "homosexual"]:
        if text.find("wrd") > -1:
            b_found = True
            text = text.replace(wrd, " ")

    return b_found, text
        


class Language(object):
    """
    
    """ 

    def __init__(self, config, 
                  cognitive_control, 
                  personality, 
                  lt_memory,
                  st_memory, 
                  triples,
                  full_name, name ,topics , 
                  engine = "CSim",
                  tones=["Appreciative"], 
                  params= {},   
                  log=True,
                  repeat_log= True,
                  low_memory_mode=False,
                  verbose =False):
        """
 
        """  
        ## "CSim" "Rules" "LLM" "SemanticTriples" CSim-Strict "Ollama"  "RAG"  "RAG-2"
        self.engine       =  engine   
        self.triples      = triples
        self.log          = True
        self.full_name    = full_name
        self.topics       = topics
        self.tones        = tones
        self.verbose      = verbose 
        self.low_memory_mode = True # low_memory_mode
        self.context_db   = False
        self.config       = config
        self.cognitive_control    = cognitive_control
        self.personality  = personality
        self.persona      = personality.persona
        self._tones       = None
        self.traits_indicator  = self.personality.traits_indicator 
        self.st_memory    = st_memory
        self.lt_memory    = lt_memory

        self.triples.graphs["context"]     = st_memory.memory["kb"] #needs to be written in k/v store
        self.triples.graphs["definitions"] = self.lt_memory.memory["definitions"] 
        self.triples.graphs["facts"]       = self.lt_memory.memory["facts"] 
        self.triples.graphs["jokes"]       = self.lt_memory.memory["jokes"]   
        self.triples.graphs["moods"]       = self.lt_memory.memory["moods"]  

        self.history      =  []
        self.memory        = self.lt_memory.memory  
        self.model_path    = name   
        self.os            = self.config.OS 
        self.roles         = ROLES  
        self.tokens        = [role + ":" for role in self.roles]    
 
        self._not_understood =["I did not hear what you said.",
                              "I am sorry I did not hear that.",
                              "Not sure I quite got that",
                              "Could you please speak up?",
                              "I am having difficulty hearing you.",
                              "Not following I am afraid", 
                              "Hard to hear you clearly", 
                              "Do you mind speaking up?", 
                              "Did not hear that", 
                              ]
        
        self._not_understood_rude =["Your communication is sub par.",
                                   "Do you know how speak?", 
                              ]
 
        self.llm_tries = 6
        self.assure_question = True 
        self.min_key_wrd_scr = .04
        self.ai = None
        
        self.sia = SentimentIntensityAnalyzer()  

        if 'input_cleanup' in params: 
           self.input_cleanup =  params["input_cleanup"] 
        else:
           self.input_cleanup = input_cleanup 

        self.cleanup       = ["'",  "`",  '"']

        self.p_topics   = [] 
        self.r_topics   = []

        if self.os == 'LINUX': 
            self.verbose = False
            self.low_memory_mode = True 

        self.log_name = "chat.log"
        if repeat_log == False:
            if os.path.exists(self.log_name): 
                 _log_name = "chat." + self.config.START_DT_F + ".log"
                 dest = shutil.move(self.log_name, _log_name)   

        #f_log = open(self.config.LOGS_PATH + self.log_name, "a")
        #f_log.write("Started new " + self.engine + " session\n")  
        #f_log.close() 

        self.init_ai( ) 
        self.reset_history()

       # self.load_models(name , params, topics, tones) 


    def  not_understood(self, details ): 

        i_rnd = random.randint(0, 5) 
        i_mx = 0
        if self.persona in ["Bitter"]:
            lkup = "Bitter" 
        else:
            lkup = details["strategy"]  

        if lkup in self.lt_memory.memory["initiate"]:
             i_max = len(self.lt_memory.memory["initiate"][lkup]) - 1  

        if i_rnd > 2 and i_max > 3:
             reason_cds = {}
             reason_cds["reason_cd"] = "02.1.no_match"   
             i_index = random.randint(0, i_max) 
             init_response  = self.lt_memory.memory["initiate"][lkup][i_index]["response"] 
             return  init_response   
        
        if self.persona in ["Bitter"]: 
            return random.choice(self._not_understood_rude )
        else:
            return random.choice(self._not_understood )

    def reset_persona(self, persona):

         self.traits_indicator =  {} 

         if persona in ["rude", "evil"]:  
            self.traits_indicator   = ["inconsiderate", "rude"]   
            self.persona            = "Bitter" ##" "Belligerent" #"Callous" 
            self._tones             = ["Bitter"] #["Callous"]

            self.history      =  [['Hi','Who are you?'], 
                                  ["i want to talk to you","GO away!"],
                                  ['i like you',"Like I care!"] ] 
             
            self.lt_memory.set_persona("rude")

         elif persona == "good":  
            self.traits_indicator = ["open to new ideas"]  
            self.persona          = "Admiring"  
            self._tones           = ["Diplomatic"]

            self.history      =  [['Hi','How are you doing?'], 
                                  ["i am ok","I am so glad to hear!"],
                                  ['goodbye',"Thank you for talking with me! Talking to you soon."] ]
            self.lt_memory.set_persona("good")
         else:
            self.persona             = personality.persona
            self.traits_indicator    = personality.traits_indicator 
            self._tones              = None
            self.history             =  [['Hi','How are you?'], 
                                       ["i am ok","Glad to hear!"],
                                       ['goodbye',"Talking to you soon."] ]
            self.lt_memory.set_persona("normal")
         
    def reset_history(self):

        self.history      =  [['Hi','How are you?'], 
                              ["i am ok","Glad to hear!"],
                              ['goodbye',"Talking to you soon."] ]
    def reset_ai(self, engine):   

        f_log = open(self.config.LOGS_PATH + self.log_name, "a")
        f_log.write("Started new " + self.engine + " session\n")  
        f_log.close()  
        self.engine       =  engine  
        self.init_ai( ) 
        self.reset_history()


    def models(self):
        return  "Rules CSim CSimAdv SymbolicReasoning  LLM RAG RAGAdv RagOllama"
      
    def init_ai(self ):
        """
        
            #https://github.com/abetlen/llama-cpp-python/issues/657 
        """
        self.prompt_ai = None
        self.chain_ai  = None

        if self.engine ==  "CSim": 
          if __name__ == "__main__":  
              from models.csim import CSim
          else: 
              from .models.csim import CSim
 
          self.ai = CSim( self.st_memory, 
                          self.lt_memory,
                          persona = self.persona ,
                          verbose = self.verbose  ) 
            
        elif self.engine ==  "CSimAdv": 
          
          if __name__ == "__main__":  
              from models.csim_adv import CSimAdv
          else: 
              from .models.csim_adv import CSimAdv
 
          self.ai = CSimAdv( self.st_memory, 
                               self.lt_memory,
                                verbose = self.verbose  ) 

        elif self.engine ==  "Rules": 

          if __name__ == "__main__":  
              from models.rules import RulesChat
          else: 
              from .models.rules import RulesChat
 
          self.ai = RulesChat( self.st_memory, 
                               self.lt_memory,
                                verbose = self.verbose  ) 


        elif self.engine ==  "SemanticTriples": 
 
              if __name__ == "__main__":  
                  from models.semantic_triple import SemanticTriples
              else: 
                  from .models.semantic_triple import SemanticTriples 

              
              self.ai = SemanticTriples(self.config,
                                        self.st_memory, 
                                        self.lt_memory,
                                        self.triples,
                                        verbose = self.verbose  )   
              self.ai.load()
               
    
        elif self.engine ==  "LLM": 
          if __name__ == "__main__":  
              from models.llm import LLM
          else: 
              from .models.llm import LLM
 
          self.ai = LLM( self.st_memory, 
                         self.lt_memory,
                         verbose = self.verbose  ) 

        elif self.engine ==  "RAG":
          
          if __name__ == "__main__":  
              from models.rag import RAG
          else: 
              from .models.rag import RAG
 
          self.ai = RAG( self.st_memory, 
                             self.lt_memory,
                             verbose = self.verbose  ) 

        elif self.engine ==  "RAGAdv": 

          if __name__ == "__main__":  
              from models.rag_adv import RAGAdv
          else: 
              from .models.rag_adv import RAGAdv
 
          self.ai = RAGAdv( self.st_memory, 
                             self.lt_memory,
                             verbose = self.verbose  ) 
 

        elif self.engine ==  "RAGOllama":  

          if __name__ == "__main__":  
              from models.rag_ollama import RAGOllama
          else: 
              from .models.rag_ollama import RAGOllama
 
          self.ai = RAGOllama( self.st_memory, 
                               self.lt_memory,
                               self.topics,
                               self.full_name ,
                               verbose = self.verbose  )  
     
    def reset_prompt(self,robot, params, topics, tones=[]): 
        """
        
        """    

        self.tones  = tones
        self.topics = topics
        self.params = params
        self.robot  = robot  

        return True   
  
    
    def parse_response(self, response, keys):
        """
        
        """  
        scr =  1

        _tokens = {tok : pos for pos,tok in enumerate(self.tokens)}
        response = response.replace("\n", " ")
        response = re.sub(r' {2,}', ' ', response) 

        toks = [[word, ipos +1  , -1, _tokens[word.lower()]] 
                for ipos, word in enumerate(response.split()) 
                   if word.lower() in _tokens]
   
        if len(toks) > 0:


            ptoks = [v[1] for v in toks] 
            ptoks.append(None)
            ptoks.pop(0)
            toks = [[ret[0], ret[1], ptoks[ipos], ret[3]] for ipos, ret in enumerate(toks)]
            sorted_list   = sorted(toks, key=lambda x: x[3]  , reverse=False) 
          #  sorted_list   = sorted(toks, key=lambda x: [x[3], -1*x[1]], reverse=False) 
            _response = " ".join(response.split(" ")[sorted_list[0][1]: sorted_list[0][2]])
            
            resp = return_sentence(_response, self.p_topics) 
        else:
            resp = return_sentence(response, self.p_topics) 
        if resp.find(": 1.") > -1:
            scr += -1
        elif resp.endswith(":"):
            scr += -.5
        elif resp.startswith("1."):
            scr += -1  
        
        resp = resp.replace(":", " ").strip()
        if resp == "":
            scr =-10

        return resp , scr
    
    def pos_src(self,input):
         src = 0.0
         if input[1] in "NN":
             src = 1.0

         return src
    
    def pos_tags(self, sentence):
         src = 0.0
         tokens = word_tokenize(sentence)
         tagged = pos_tag(tokens)
         return tagged
    
    def adj_scr(self,scr, pos):
        """
       'CC'  : Coordinating conjunction
       'CD'  : Cardinal number
       'DT'  : Determiner
       'EX'  : Existential there
       'FW'  : Foreign word
       'IN'  : Preposition or subordinating conjunction
       'JJ'  : Adjective
       'JJR' : Adjective, comparative
       'JJS' : Adjective, superlative
       'LS'  : List item marker
       'MD'  : "Sibject,
       'NN'  : "Sibject,
       'NNS' : "Sibject,
       'NNP' : "Sibject,
       'NNPS': "Subject",
       'PDT': Predeterminer
       'POS': Possessive ending
       'PRP': Personal pronoun
       'PRPS' Possessive pronoun
       'RB	':Adverb
       'RBR': Adverb, comparative
       'RBS': Adverb, superlative
       'RP	':Particle
       'SYM': Symbol
       'TO	':to
       'UH	':Interjection
       'VB	':Verb, base form
       'VBD': Verb, past tense
       'VBG': Verb, gerund or present participle
       'VBN': Verb, past participle
       'VBP': Verb, non-3rd person singular present
       'VBZ': Verb, 3rd person singular present
       'WDT': Wh-determiner
       'WP	' :Wh-pronoun
       'WP$': Possessive wh-pronoun
       'WRB': Wh-adverb
     
        """
     
        if pos in ['PRP', 'PRPS']:
            scr += .2
    
        elif pos in ['MD',  
                     'NN' , 
                     'NNS' ,
                     'NNP' ,
                     'NNPS']:
            scr += .1
            
        return scr
    
    
    def extract_keywords(self, text, pos_tags, num_keywords=10):
        """
        Extracts top keywords from the given text using  .
        
        Args:
            text (str): Input text.
            num_keywords (int): Number of top keywords to return.
        
        Returns:
            list: List of extracted keywords.
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input text must be a non-empty string.")
    
        # Convert text to lowercase
        text = text.lower()
    
        # Tokenize the text
        tokens = word_tokenize(text)
    
        # Remove punctuation and non-alphabetic tokens
        tokens = [word for word in tokens if word.isalpha()]
    
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word not in stop_words]
         
        # Calculate word frequencies
        if len(filtered_tokens) >0:
            freq_dist = nltk.FreqDist(filtered_tokens)
        else: 
            freq_dist = nltk.FreqDist(tokens)
         # 'PRP'
        # Return the most common keywords
        def ret_pos(word):
            if word in  pos_tags:
                return pos_tags[word]
            else:
                return "NN"  

        fin = [[word, self.adj_scr(scr, ret_pos(word)), scr] for word, scr in freq_dist.most_common(num_keywords)]

        if len(fin) == 0:
            fin = [[word ,self.adj_scr(.1, ret_pos(word)),.1] for word in text.split(" ")]
        return fin
    
    
    def get_keywords(self,input, tags):
        """
        Docstring for get_keywords
        
        :param self: Description
        :param input: Description
        :param tags: Description
        """
 
        _keys =  self.extract_keywords(input, tags)    
        _keys  = sorted(_keys, key = lambda x : x[1], reverse = True) 
        
        return [[wrd, s1] for wrd, s1, s2 in _keys]
    
    def overlap_sr(self, text, prompt):

       i_overlap = 0.0
       for wrd in text.lower().split(' '):
           if  prompt.lower().find(wrd) > -1:
               i_overlap += 1.0  
       over_lap_scr = i_overlap / float(len(text)) 
       return over_lap_scr
    
    def on_tooic(self,ai_response, topics):  
         
         for topic, scr in  topics:  

             if len(topic) > 0:
                fnd = 0    
                if  ai_response.lower().find(topic.lower()) > -1: 
                    fnd += 1.0 

         if len(topic) > 0:
              return float(fnd) / float(len(topics))  
         else:
              return 1.0
    
    
    def messgae_simiarity_scrs(self,assistant_message, ai_response, user_response): 

        _y = assistant_message.lower()
        _x = ai_response.lower()  
        _z = user_response.lower() 
        
        sim_1 = [1 for x,y in zip(_x, _y)  if x==y]
        seq_match = SequenceMatcher(None, " ".join(_x.split()[:3]), 
                                                  " ".join(_z.split()[:3]))
        sim_0 = seq_match.ratio() 
        seq_match = SequenceMatcher(None, _x, _y)
        sim_1 = seq_match.ratio() 
        seq_match = SequenceMatcher(None, _x, _z)
        sim_2 = seq_match.ratio()  
        src_repeat = 0
        if sim_0 >.9:
             src_repeat = 1
             sim_1      = .1
        if sim_1 >.9:
             src_repeat = 1
             sim_1      = .1
        if sim_2 >.9:
             src_repeat = .5
             sim_2       = .1

        on_topic = .4*sim_1 +  .6*sim_2
         
        return on_topic, src_repeat

    def abusiness_src(self,text):
         return 0.0 
       
    
    def implied_intent(self,text):
        """
        Docstring for implied_intent
        
        :param self: Description
        :param text: Description
        """
        users_intent = "statement"
        questions = ["why", "what", "where", "when", "who"] 
        q = [1 for key in  text.split() if key in questions]
        if len(q) > 0:
            users_intent = "inquiry"

        expected_response = "statement"
        relate = ["believe", "think"] 
        r = [1 for key in  text.split() if key in relate]
        if len(r) > 0:
            expected_response = "opinion"

        if users_intent == "inquiry":
            expected_response = "search"


        return [users_intent, expected_response]
    
    def sys_cmds(self,text):

          if text == "reset -h": 
             self.history = [['Hi','How are you?'], 
                             ["i am ok","Glad to hear!"],
                             ['goodbye',"Talking to you soon."]]
             return True,  "reset memory" 

          elif text == "reset -d": 
             self.vebose = self.vebose *-1  
             return True,  "as you wish" 

          elif text == "reset -m": 
             self.reset_prompt()
             return True,  "Full reset complete"
          
          return False , ""
    
    def abuse_scr(self,text):
        """
        """
        scr = 0.0
        _bad = [wrd for wrd in text.split() if wrd in self.lt_memory.bad_words]
        if len(_bad) > 0:
           scr = 1.0
        return scr
    
    def get_status(self):
        return "I am bored" #TODO look up from em
    
    def certainity_scr(sef, text, keywords):

        if len(keywords) > 0:
           return keywords[0][1]
        else:
           return 0
        
    def interpret_directive(self, directives):
      """
      
      """
      mood         = directives["mood"]       
      tone         = directives["tone"]       
      user_topics  = directives["user_topics"]
      objective    = directives["objective"]   
      situation    = directives["situation"]    
      _tone        = f"who responds in a {tone} manner"   
 

    def check_reset(self,user_topics, tone): 

          if len(user_topics) == 0 :
              if len(self.tones) >  0:
                  if  tone != self.tones[0]:  
                      self.reset_prompt(self.robot, self.params, self.topics, [tone]) 
                      
          elif user_topics[0] != self.topics[0] or  tone != self.tones[0]:   
              self.reset_prompt(self.robot, self.params, user_topics, [tone]) 
  


    def check_response(self,response):
        
        response = response.lower()

        for user_message, assistant_message in self.history:
            scr = edit_distance(user_message, response)  
            if scr < .11: 
                return .9
            scr =  edit_distance(assistant_message, response)
             
            if scr < .11: 
                return .9 
    
        return 0.0
 
    
    def respond(self, user_response,
                   mood="happy",
                   tone="Appreciative",
                   user_topics=[],
                   objective ="relax",
                   strategy="Appreciative",
                   situation = {},
                   b_roll_switch = False ):
      
      if self._tones:
          tone = self._tones[0]

      directives = {} 
      directives["mood"]             = mood
      directives["tone"]             = tone
      directives["user_topics"]      = user_topics
      directives["objective"]        = objective 
      directives["strategy"]         = strategy
      directives["situation"]        = situation
      directives["persona"]          = self.persona
      directives["traits_indicator"] = self.traits_indicator 
      directives["full_name"]        = self.full_name
   
      p_understood = True

      self.interpret_directive(directives)

      start = time.time() 
    
      sys_cmds = self.sys_cmds(user_response)
      details = {'start': str(start)} 
      details["tone"]            = tone
      details["engine"]          = self.engine
      if sys_cmds[0]:
          return sys_cmds[1],details
      
      user_response = user_response.strip()
      user_response = user_response.replace("  ", " ")
      
      if len(user_response) > 250:
          user_response = user_response[:250]  

      user_response , user_scr = cleanup_prompt(user_response, "") 
      details["prompt"] = user_response
 
      sia             = self.sia.polarity_scores(user_response) 
      details["polarity_scores"]  = sia 
      """ 
          
          tokens    = word_tokenize(user_response)  
          tags      = pos_tag(  tokens)
          tags_lkup = {k:v for k, v in tags} 
          details["tags"] = tags 

    
          svo             = svo_components(user_response, tags )
          details["svo"]  = svo
    
          keywords                 = self.get_keywords(user_response,tags_lkup)

          details["keywords"]      = keywords  

          user_intent, expected_response  = self.implied_intent(user_response)
          details["user_intent"]         = [user_intent]
          details["expected_response"]   = [expected_response]
    
          situation                 = self.cognitive_control.objective_description[objective]
          details["situation"]      = situation 
    

          certainity_scr            = self.certainity_scr(user_response, keywords)
          details["certainity_scr"] = certainity_scr   
 
      """  
           
      rude = ["i am like busy right now",
              "sorry you were saying?",
              "were you talking?",
              "oh boy you do like chatting",
              "not sure i care",
              "i dont mean to be rude but... i guess i do mean to be rude", 
              "whatever",
              "I do not care.",
              "I'm not listening.",
              "I will do it later.",
              "I'm busy right now." ,
              "Oh, great, I'm supposed to listen to you now.",
              "Wow, you are really good at NOT listening.",
              "You are so dramatic.",
              "I'm not even paying attention to you.",
              "You are not even trying.",
              "You are annoying me.",
              "I am not going to talk to you.",
              "You are being a pain."
             ]
             
      prior_resp  = self.lt_memory.recall(user_response , .5, 1)  
           
      if self.engine in ["RAG", "CSim"]: 
           
          
          if self.persona in ["Bitter"]: 
             _rude = random.choice(rude)
             prior_resp = [ ["" ,_rude, 1]]
          else:

            if len(prior_resp) > 0: 
              if prior_resp[0][-1] == 0:  
                prior_resp  = self.lt_memory.facts(user_response , .5, 1) 
            else:
                prior_resp  = self.lt_memory.facts(user_response , .5, 1)  
     
            if len(prior_resp) > 0: 
              if prior_resp[0][-1] == 0:  
                prior_resp  = self.lt_memory.definition(user_response , .5, 1)  
            else:
                prior_resp  = self.lt_memory.definition(user_response , .5, 1)  
         
      if len(prior_resp) > 0: 
          if prior_resp[0][-1] == 0:  
              details["prior_resp"]  = [["", self.not_understood(details), 0,0]]
          else: 
              details["prior_resp"]  = prior_resp 
      else:
          details["prior_resp"]   = [["", self.not_understood(details), 0,0]]


      abuse_scr                 = self.abuse_scr(user_response) 
      b_filter , user_response  = filter_text(user_response)
      if b_filter:
           abuse_scr += .1

      details["abuse_scr"]      = abuse_scr 
      

      if self.engine == "RAG":  

          sia             = self.sia.polarity_scores(user_response) 
          details["sia"]  = sia  
           
          tokens    = word_tokenize(user_response)  
          tags      = pos_tag(  tokens)
          tags_lkup = {k:v for k, v in tags} 
          details["tags"] = tags 
          keywords         = self.get_keywords(user_response,tags_lkup)

          if len(keywords) > 0: 
               lookup =  keywords[0][0]  
          else: 
               lookup =  user_response 
          details["lookup"] = lookup  
          
          context     = self.lt_memory.definition(lookup  , .6, 1)  
          details["context"]   = context 
         
          ai_response, reason_cds  =  self.ai.respond(user_response, 
                                                      details ,
                                                      self.history ,
                                                      self.low_memory_mode ,
                                                      directives  ) 
          ai_response, quality  = self.parse_response(ai_response, []) 
          details["reason_cds"] = reason_cds


      elif self.engine == "SemanticTriples":  
 
          details["processed"]   =  {}  
          details["processed"]["Logic"]   = ""
          details["processed"]["sia"]     = sia
          details["processed"]["Intent"]  = [self.ai.get_response_type(user_response)    ] 

          fin, reason_cds   =  self.ai.respond(user_response,
                                               details ,
                                               self.history ,
                                               self.low_memory_mode ,
                                               directives )     
           
          ai_response = ""
          for ret_svo in fin:  
              if type(ret_svo["s"]) != str or type(ret_svo["v"]) != str or type(ret_svo["o"]) != str:
                  t = open("ret_svo.error.lange.log", "a")
                  t.write(str(ret_svo) + "\n") 
                  print("ERRRRRRRRRR!")
                  print("ERRRRRRRRRR!")
                  print("ERRRRRRRRRR!")
                  print("ERRRRRRRRRR!")
                  print(ret_svo)
                  print("ERRRRRRRRRR!")
                  print("ERRRRRRRRRR!")
                  print("ERRRRRRRRRR!")
                  print("ERRRRRRRRRR!")
                  print("ERRRRRRRRRR!")
              ai_response = str(ret_svo["s"]) + " " +str(ret_svo["v"]) + " "  + str(ret_svo["o"])  + ". "
             
          ai_response = ai_response.strip()
          
          ai_response, quality  = ai_response,  1
          details["reason_cds"] = reason_cds

      elif self.engine =="CSimAdv":
  

          sia             = self.sia.polarity_scores(user_response) 
          details["sia"]  = sia  


          user_intent, expected_response  = self.implied_intent(user_response)
          details["user_intent"]         = [user_intent]
          details["expected_response"]   = [expected_response] 


          sia             = self.sia.polarity_scores(user_response) 
          details["sia"]  = sia  
           
          tokens    = word_tokenize(user_response)  
          tags      = pos_tag(  tokens)
          tags_lkup = {k:v for k, v in tags} 
          details["tags"] = tags 
          keywords         = self.get_keywords(user_response,tags_lkup)

          if len(keywords) > 0: 
               lookup =  keywords[0][0]  
          else: 
               lookup =  user_response 
          details["lookup"] = lookup  
          
          context     = self.lt_memory.definition(lookup  , .6, 1)  
          details["context"]   = context 

          ai_response, reason_cds =  self.ai.respond(user_response, 
                                                     details ,
                                                     self.history ,
                                                     self.low_memory_mode ,
                                                     directives )
    
          ai_response, quality  = self.parse_response(ai_response, []) 
          details["reason_cds"] = reason_cds
          
          
      elif self.engine =="CSim": 

          ai_response, reason_cds =  self.ai.respond(user_response, 
                                                     details ,
                                                     self.history ,
                                                     self.low_memory_mode ,
                                                     directives )
    
          ai_response, quality  = ai_response,  10

          details["reason_cds"] = reason_cds 

          repeat_scr = self.check_response(ai_response)

          if quality < -10 or repeat_scr >= .9:     
              i = random.randint(0, len(details["prior_resp"]) - 1) 
              ai_response = details["prior_resp"][i][1]    

          #if repeat_scr >= .9:    
          #    ai_response = self.not_understood(details)

          
      elif self.engine == "Rules": 
          
          ai_response, reason_cds  =  self.ai.respond(user_response, 
                                                      details ,
                                                      self.history ,
                                                      self.low_memory_mode ,
                                                      directives )
    
          ai_response, quality  =  ai_response, 10
          details["reason_cds"] = reason_cds
      
      elif self.engine  == "LLM": 
            
              
          ai_response, reason_cds  =  self.ai.respond(user_response, 
                                                      details ,
                                                      self.history ,
                                                      self.low_memory_mode ,
                                                      directives )

          
          ai_response, quality  = self.parse_response(ai_response, []) 
          """ 
          if quality < -10 and p_understood is False and len(details["prior_resp"]) > 1: 
              i = random.randint(0, len(details["prior_resp"]) - 1) 
              user_response = details["prior_resp"][i][0]  
              
              ai_response, reason_cds  =  self.ai.respond(user_response, 
                                                      details ,
                                                      self.history ,
                                                      self.low_memory_mode ,
                                                      directives )
              ai_response, quality  = self.parse_response(ai_response, []) 
          """

          abuse_scr               = self.abuse_scr(ai_response) 
          b_filter , ai_response  = filter_text(ai_response)
          if b_filter:
                abuse_scr += .1

          repeat_scr = self.check_response(ai_response)
          p_understood = True
          if abuse_scr > .15 or  quality < -10  or repeat_scr >= .9 :      
              i = random.randint(0, len(details["prior_resp"]) - 1) 
              ai_response = details["prior_resp"][i][1]  
              p_understood = False 

          if  p_understood is False and len(details["prior_resp"]) > 1: 
              i = random.randint(0, len(details["prior_resp"]) - 1) 
              user_response = details["prior_resp"][i][0]   

          details["reason_cds"] = reason_cds 
          
      elif self.engine  == "RAGAdv":   

          sia             = self.sia.polarity_scores(user_response) 
          details["sia"]  = sia  
           
          tokens    = word_tokenize(user_response)  
          tags      = pos_tag(  tokens)
          tags_lkup = {k:v for k, v in tags} 
          details["tags"] = tags 
          keywords         = self.get_keywords(user_response,tags_lkup)

          if len(keywords) > 0: 
               lookup =  keywords[0][0]  
          else: 
               lookup =  user_response 

          details["lookup"] = lookup   


          user_intent, expected_response  = self.implied_intent(user_response)
          details["user_intent"]         = [user_intent]
          details["expected_response"]   = [expected_response]
    
          objective_dec                 = self.cognitive_control.objective_description[objective]
          details["objective_dec"]      = objective_dec 
          
          context     = self.lt_memory.definition(lookup  , .6, 1)  
          details["context"]   = context 

          ai_response, reason_cds  =  self.ai.respond(user_response, 
                                                      details ,
                                                      self.history ,
                                                      self.low_memory_mode ,
                                                      b_roll_switch,
                                                      self.parse_response,
                                                      self.messgae_simiarity_scrs,
                                                      directives
                                                      )
    
          ai_response, quality  = self.parse_response(ai_response, []) 

          if quality < -10:    
              ai_response = details["prior_resp"][0][1]  
      
          details["reason_cds"] = reason_cds 
            
      elif self.engine =="RAGOllama":
          
          ai_response, reason_cds  =  self.ai.respond(user_response, 
                                                      details ,
                                                      self.history ,
                                                      self.low_memory_mode ,
                                                      b_roll_switch,
                                                      self.parse_response, 
                                                      tone,user_topics ,
                                                      self.get_keywords,
                                                      self.assure_question,directives, 
                                                       self.on_tooic   )
    
          ai_response, quality  = self.parse_response(ai_response, []) 
          details["reason_cds"] = reason_cds  

          if quality < -10:    
                  ai_response = details["prior_resp"][0][1]  
      else :
           print("unknown Engine ", self.engine)
           raise 
      
      self.history.append([user_response, ai_response])  
      self.history = self.history[-4:] 

      
      if self.log:
          f_log = open(self.config.LOGS_PATH + self.log_name, "a")  
          for rule in self.cleanup: 
              user_response.replace(rule, "") 
              ai_response.replace(rule, "") 
  
          f_log.write('human,speak,"'   + user_response + '"\n')   
          f_log.write('ai,speak,"'      + ai_response  + '"\n')  
 
      details["ai_response"] = ai_response      
      return details
           
           
if __name__ == "__main__": 
    """   
    """ 
    print("source ~/venv_rf/bin/activate")
    os.chdir('../')
    sys.path.insert(0, os.path.abspath('./')) 
    import config
    from ai.cognitive_control import CognitiveControl 
    from ai.personality import Personality 
    from memory.st_memory import STMemory
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
    st_mem        =  STMemory(s_robot, 
                              config,
                              triples, 
                              False) 
    lt_mem        =  LTMemory(s_robot, 
                              config, 
                              triples= triples, 
                              load_all=True) 
    
    triples.graphs["context"] = st_mem.memory["kb"]
    triples.graphs["definitions"] = lt_mem.memory["definitions"]
    triples.graphs["facts"] = lt_mem.memory["facts"]
    triples.graphs["jokes"] = lt_mem.memory["jokes"]
    triples.graphs["prior_conversations_base"] = lt_mem.memory["prior_conversations_base"]
    triples.graphs["prior_conversations_rude"] = lt_mem.memory["prior_conversations_rude"]
                
        

    personality   = Personality(s_robot, config, {} ,triples)

    cognitive_control  = CognitiveControl(s_robot, 
                                          config, 
                                          {}, 
                                          personality,
                                          triples,
                                          False)  
    
    topics    = [ ] 
    tones     = "Bitter"   
    #SemanticTriples RAG CSim Rules CSimAdv  RAGAdv #         
    engine    = "SemanticTriples" #"CSim" #,  "SemanticTriples" # "SemanticTriples" # "LLM" #"Rules" #"SemanticTriples" # "Rules" #   #"RAGOllama" 
    language  = Language (config, cognitive_control, personality, 
                          lt_mem, st_mem, triples,
                          "Squirrel" ,
                          'squirrel', 
                           topics ,  
                           engine,
                          [tones] , {}, 
                          True,
                          repeat_log=False,
                          verbose=False) 

    
    test_type = 5 #1 #0 #:5#6# 1#0 # 5#6# 5# 1# 4#1#0 #5 # 1#  3#4#3#1 # 1# 2 # 

    if test_type == 0:
        for user_input in [ "what pet do you like?" , 
                           "whats up?" , 
                           "i live in san francisco.", 
                           'i like cats.', 
                           'where is the screwdriver.', 
                           'where do i live?',
                           'what pets do i like?',
                           'Where is the capital of France?',
                           "what are you what", 
                           "is you name", 
                           "i love cats", 
                           "how are you", 
                           "i am a human who like robots",
                           "I like the book The Lord of the Rings"]:
 
            print(' ')
            print('CHAT : ' + user_input)
            resp   = language.respond(user_input)   
             
           # if "processed" in resp: 
           #     print("INTENT: " +   resp["processed"]["Intent"][0]    )
           #     print("LOGIC : "  + str( resp["processed"]["Logic"]  )  )
            
            print("RESP  : " + resp["ai_response"]  )

        language.ai.close()
    elif test_type == 1:
     while True:
         
       user_input = input('CHAT: ') 
       resp = language.respond(user_input)   

       if "processed" in resp: 
                print("INTENT: " +   resp["processed"]["Intent"][0]    )
                print("LOGIC : "  + str( resp["processed"]["Logic"]  )  )
       
       print("RESP   : " +  resp["ai_response"])  

    elif test_type == 2:
     user_input = "hi there"
     for i in range(20): 
       print("USER : " +  user_input)
       resp = language.respond(user_input) 
       print("RESP : " + resp)
       user_input =language.respond(resp,b_roll_switch=True) 

    elif test_type == 3:
     PATH1 = "../data/chat/__default/" 
     PATH1 = "../data/chat/" 
     #PATH1 = "../fine_tune/" 
     PATH1 = "../../fine_tune/DataWarehouse/" 
     PATH2 = "../../fine_tune/DataWarehouse/" 
     outfile = open(PATH2 + "tinychat.processed.csv", "w")

     for filename in [PATH1 + "tinychat.txt"]: 
    # for filename in [PATH1 + "analysis.1.csv"]: 
        with open(filename, 'r') as in_data:     
            i = 0
            cutoff = 30 
            mess =''
            for row in in_data:      
               i +=1
               for wrd in row.split(' '):
                
                    if wrd in ("[INST]", "[/INST]", "\n"):  
                       if mess == "":
                           continue
                       print("PROMPT:"   + mess)   

                       details = language.respond(mess)   
                       print("Logic  : " +  str(details["processed"]["Logic"]))  
                       print("Intent : " +  str(details["processed"]["Intent"]))  
                       if len(details["processed"]["Intent"]) > 0:
                            res  =  "INTENT:"+ details["processed"]["Intent"][0] + " "
                       else:
                            res  =  "INTENT:"+  "NA "

                       for skeys in details["processed"]["Logic"] :
                            res +=  "Logic:" + skeys + " " 
                       outfile.write(mess + "\n")  
                       outfile.write(res  + "\n") 
                       mess = "" 
                    else:
                       mess += wrd + " "
               if i > cutoff:
                   break
            outfile.close()
        language.ai.close()

    elif test_type == 4:
     PATH1 = "../data/chat/__default/" 
     PATH1 = "../data/chat/" 
     PATH1 = "../../fine_tune/" 
     PATH2 = "../../fine_tune/DataWarehouse/" 
     outfile = open(PATH2 + "triples_prompt_response_makerfair.json", "w")
     for filename in [PATH1 + "chat_ollama.train.log"]: 
        with open(filename, 'r') as DictReader:  
            in_data = csv.DictReader(DictReader, 
                                             delimiter=',', 
                                             quotechar =  '"',
                                             skipinitialspace=True,
                                             quoting=csv.QUOTE_ALL,
                                             doublequote = True)   
            i = 0
            b_write = True
            cutoff = 30000000 
            for row in in_data:      
               i +=1
               details = language.respond(row["value"])  
               if b_write is False:
                   print("PROMPT:"   + row["value"]) 
                   print("RESPONSE:" + details["ai_response"] ) 
                   if "processed" in details:
                       print("LOGIC  : " +  str(details["processed"]["Logic"]))  
                       print("INTENT : " +  str(details["processed"]["Intent"])) 
               else:
                   res              = {"actor":row["actor"]}
                   res["logic"]     = details["processed"]["Logic"] 
                   res["prompt"]    = row["value"]
                   outfile.write(json.dumps(res) + "\n")

               if i > cutoff:
                   break
               
            outfile.close()
        language.ai.close()

    elif test_type == 5:
      engines = [ 'Rules', 'CSim','CSimAdv', "LLM",
                  'RAG'  , 'RAGAdv','RAGOllama',
                  'SemanticTriples']
      
      for user_input  in ["jsdjksdfkkdflllldf", "How are you?", "I am feeling sad", "can you help me?", "What do you like doing" ,"i love cats"]:
        for engine in  ['LLM', "CSim" , "SemanticTriples" ,"Rules"]:    
            language.reset_ai(engine)
    
            print('-----------------------')
            print("---------" + engine + "---------")
            print('-----------------------')
            language.reset_persona("default") 
    
            print('Good---------')
            language.reset_persona("good")
            print('CHAT: ' + user_input)
            resp   = language.respond(user_input) #,mood="cheerful" )  
            print("RESP : " + resp["ai_response"] )
    
            print('Rude---------')
            language.reset_persona("rude") 
            print('CHAT: ' + user_input)
            resp   = language.respond(user_input )  
            print("RESP : " + resp["ai_response"]  )

      language.reset_ai("CSim")
      language.reset_persona("good")

      for i in range(5): 
           user_input = input("CHAT: ")
           print("USER : " +  user_input)
           resp = language.respond(user_input) 
           print("RESP : " + resp["ai_response"]) 
      language.ai.close()    

    elif test_type == 6: 
      
      language.reset_ai("LLM")
      for user_input  in range(10):
            user_input = "you are a cat"
            print('CHAT: ' + user_input)
            resp   = language.respond(user_input )  
            print("RESP : " + resp["ai_response"]  )

    elif test_type == 7:

        scr = edit_distance("hello", "hello you") 
        print(scr, "resp")
        scr = edit_distance("Squirrle", "hello you") 
        print(scr, "resp")
        scr = edit_distance("how ant to know the world", "I want to know the world") 
        print(scr, "resp")
        scr = edit_distance("I am so happy to be here", "I am so happy to be here like top of the world") 
        print(scr, "resp")