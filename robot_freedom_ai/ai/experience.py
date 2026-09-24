#!/usr/bin/python
# -*- coding: utf-8 -*-
  
"""
Description: AI experience interface.
Author: HipMonsters.com  
License: MIT License  
"""

import os
import datetime 
import json  
##import numpy as np  
import random 


if __name__ == "__main__": 

   from  models.gds import GDS
else:
   from .models.gds import GDS
  

class Experience():

   def __init__(self, robot , config, cognitive_control, personality, st_memory, lt_memory,  low_memory_mode):
       """
       
       """
       self.robot                   = robot 
       self.config                  = config 
       self.personality             = personality
       self.discount                = personality.discount
       self.novelty                 = 1 - self.discount 
       self.prior_statement         = "" 
       self.cognitive_control       = cognitive_control
       self.episodic_memory                       = cognitive_control.episodic_memory
       self.st_memory               = st_memory 
       self.lt_memory               = lt_memory 
       self.verbose =False# verbose 
     

       self.low_memory_mode   = low_memory_mode 
       self.last_reflection   = datetime.datetime.now()
       self.epoch             = 1
       
       self.reaction_threshold  = personality.reaction_threshold  
       self.movement_threshold  = personality.movement_threshold  
       self.speech_threshold    = personality.speech_threshold
 
            
       self.objectives        =  list(self.cognitive_control.objectives.keys())  
       self.factors           = self.cognitive_control.factors  
       self.goals             = self.cognitive_control.goals   
       self.mapped_stimuli    = self.cognitive_control.mapped_stimuli 
       self.mapped_strategies     =  self.cognitive_control.mapped_strategies
       self._emotional_suppressors =  self.cognitive_control.emotional_suppressors

       self.words = {}
       self.dates_done_words = set([])

       self.experience                          = {}  
 
   
       self.experience["objectives_2_moods"]   = {} 
       self.experience["senses_2_moods"]       = {} 
       self.experience["objective_2_strategy"] = {}  
       self.experience["strategy_2_mood_scr"]   = {}  
       self.experience["strategy_2_mood"]      = {}
       self.experience["objectives_2_mood"]    = {}

       self.current_strategy   = None
       self.current_strategies     = []
       self.current_nonverbal_strategy = None
       
       self.prior_mood       = None 

       self.prior_nonverbal_strategy = None
       self.prior_strategy   = None
       self.prior_strategies     = []
       
 
   def save(self ):
      """  
      
      """
      with open(self.config.DATA_PATH + self.robot + "/experience.json", "a") as f:
         f.write( json.dumps(self.experience )  + "\n")

      with open(self.config.DATA_PATH + self.robot + "/experience.words.json", "a") as f:
         f.write( json.dumps(self.words )  + "\n")   

   def strategies(self,objective): 
        
       edges = self.episodic_memory.related(objective, "objective_2_strategy", None , return_data = True) 
       cat = edges[0][0]["o"]  
       edges = self.episodic_memory.related( objective, cat, None , return_data = True)  
       potentials = [[e["o"], e["data"] ]for e , scr, _t in edges] 
       return potentials
   
  

   def strategy(self, objective, interval, last_moved, last_talked, mood, chatting ):
       """    
    
       """   

       self.prior_strategy   = self.current_strategy
       self.prior_strategies = self.current_strategies 
       self.prior_mood       = mood

       wght_adg = {}
       wght_adg[self.prior_strategy] = 1
       if self.prior_strategy is not None and mood == "happy":
           wght_adg[self.prior_strategy] = 3 
       elif  self.prior_strategy is not None and self.prior_mood == "happy" and mood != "happy":
           wght_adg[self.prior_strategy] = .5 
   
       unique_type = objective  

        
       edges = self.episodic_memory.related(objective, "objective_2_strategy", None , return_data = True) 
       cat = edges[0][0]["o"]  
       edges = self.episodic_memory.related( objective, cat, None , return_data = True)  
       potentials = [[e["o"], e["data"] ]for e , scr, _t in edges]  
  
       self.current_strategies = potentials

       probs  = [e["weight"] for v ,e in potentials] 
       #probs  =  np.random.dirichlet(probs, size=1)[0]   
       
       draw = random.choices([v for v, e in potentials], weights=probs, k=1)
       self.current_strategy   = draw[0] #_t
       #while True:
           #  TODO loop through to check emotiuon strageiy alignment 

        #   draw = random.choices([v for v, e in potentials], weights=probs, k=1)
           #draw   = np.random.choice([v for v, e in potentials], 
           #       1,
           #       p=probs) 
         #  _t = draw[0]
           #if _t != "Angry" :
           #    self.current_strategy   = _t
           #    break 

           
       _pots = list(self.cognitive_control.non_verbal_strategies_wgt.keys())

      # self.current_nonverbal_strategy =  np.random.choice(_pots,1)[0]
       self.current_nonverbal_strategy =  random.choice(_pots  )[0]

       if self.verbose: 
          print("~~~~~~~~~   start   ~~~~~~~~~~~~~~") 
          print(self.current_strategy )
          print(self.current_nonverbal_strategy) 

       if last_moved <  self.movement_threshold:  
              self.current_nonverbal_strategy  = "quiet" 

       if chatting:
           if last_talked < self.speech_threshold*.25: 
               return  self.current_nonverbal_strategy 
       else:
           if last_talked < self.speech_threshold: 
               return  self.current_nonverbal_strategy 
       
       return  self.current_strategy

   def emotional_suppressors(self, 
                             objective, 
                             strategy,
                             stimuli_class = "", 
                             amplitude = ""  ):
       """
       
       """ 

       edges = self.episodic_memory.related( objective, "emotional_suppressors", None , return_data = True) 
       return {e["o"]:e["data"]["weight"]  for  e,s,v in edges}
 
   
   def __moods_expand(self, ds):  
       """
       
       """
       row  = []
       cols = [] 
       for key , val in ds.items():
           row.append(val  )    
           cols.append(key  )  

       return row ,cols  
   
   def __motivations_expand(self,ds  ): 
        """
             
        """
        row  = []
        cols = [] 
        for key , val in ds.items():
           row.append(val  )    
           cols.append(key  )    
        return row ,cols   
   
   def __strategy_ohe(self,ds  ): 
        """
             
        """
        row  = []
        cols = [] 
        for key  in self.mapped_strategies :
           if key in ds: 
               row.append(1.0 ) 
           else:   
               row.append(0.0 )    
           cols.append(key  )    
        return row ,cols   

   def __strategy_bin(self,strategy, rev=False ): 
            """
            
            """
            ## needs to move to settings
   
            if rev:
                if strategy < (len(self.mapped_strategies) - 1):
                    return self.mapped_strategies[strategy]
                else:
                    return "NA" 

            if  strategy  in self.mapped_strategies:
                  return self.mapped_strategies.index(strategy)
            else:
                  print('strategy', strategy)
                  return -1 
            
   
   def __stimuli_ohe(self,ds  ): 
        """
            
        """
        row  = []
        cols = [] 
        for key   in self.mapped_stimuli :
           if key in ds:
               row.append (1.0 ) 
           else:   
               row.append(0.0 )    
           cols.append(key  )    
        return row ,cols   
   
   def __stimuli_bin(self,stimuli , rev=False): 
            """ 
            
            """
            ## needs to move to settings
   
            if rev:
                if stimuli < (len(self.mapped_stimuli) - 1):
                    return self.mapped_stimuli[stimuli]
                else:
                    return "NA" 
            if  stimuli  in self.mapped_stimuli:
                  return self.mapped_stimuli.index(stimuli)
            else:
                  print('stimuli', stimuli)
                  return -1  
            
   def __objective_ohe(self,ds  ): 
        """
            
        """
        row  = []
        cols = [] 
        for key  in self.objectives :
           if key in ds:
               row.append(1.0 ) 
           else:   
               row.append(0.0 )    
           cols.append(key  )    
        return row ,cols   
   
   def __objective_bin(self,objective, rev=False ): 
            """
            
            """
            ## needs to move to settings
            if rev:
                if objective < (len(self.objectives) - 1):
                    return self.objectives[objective]
                else:
                    return "NA" 
                
            if  objective  in self.objectives:
                  return self.objectives.index(objective)
            else:
                  print('objective', objective)
                  return -1  



   def __feature_gen(self, raw_feats, row):
       """
       why low cost / direct to consume / use case SAAS 

       SAAS 
       deepseek

       

       """
       feats = []
       cols  = []

       for feat in raw_feats: 
           
           if  feat == "event_interval":
                 feats.append(round((row['event_interval']  / 1000.0 ), 5))
                 cols.append(feat) 
           
           elif  feat == "objective":
                 _feats , _cols =  self.__objective_ohe(row[feat] ) 
                 feats += _feats
                 cols  += _cols

           elif  feat == "stimuli_class":
                 _feats , _cols  = self.__stimuli_ohe(row[feat] )
                 feats += _feats
                 cols  += _cols
               
           elif feat == "strategy": 
                 _feats , _cols =  self.__strategy_ohe(row[feat])  
                 feats += _feats
                 cols  += _cols

           elif  feat == "moods":  
                 _feats , _cols = self.__moods_expand(row[feat])
                 feats += _feats
                 cols  += _cols

           elif feat == "motivations":  
                 _feats , _cols = self.__motivations_expand(row[feat])
                 feats += _feats
                 cols  += _cols 

               
           else:
                 feats.append(row[feat])
                 cols.append(feat) 

       return feats, cols
   
   def run_model(self,model_name, index, target, cols, short_term_memory, multi_seg=True):
        """ 

        """ 

        Y           = {}
        X1          = {} 
        mdl_results = {}
        segments    = set([])
        feats        =  None 
       
        if multi_seg is False:
             
             for key, details in short_term_memory["stimuli"].items():  
                  
                 seg = details[index]
                 if seg not in Y:
                     Y[seg]  = []             
                     X1[seg] = []   
                     segments.add(seg) 

                 _y , _cy    = self.__feature_gen([target], details)

                 Y[seg].append(_y[0])   

                 _x, _feats = self.__feature_gen(cols , details) 

                 X1[seg].append( _x)

                 if feats is None:
                     feats = _feats
 
        else: 
          for key, details in short_term_memory["stimuli"].items(): 
          
             for seg ,val in details[target].items():
                 
                 if seg not in Y :
                     Y[seg]  = []             
                     X1[seg] = []  

                 segments.add(seg)

                 Y[seg].append(val)   
                 _x, _feats = self.__feature_gen(cols , details) 

                 X1[seg].append(_x)

                 if feats is None:
                     feats = _feats 
        LR = 0.000001

        for seg  in segments:
            prior_weights =  None
            if model_name in self.experience:
                if "weights" in self.experience[model_name]:
                  if seg in self.experience[model_name]["weights"]: 
                     prior_weights = [v for k, v in self.experience[model_name]["weights"][seg]]

            if prior_weights is None:
                prior_weights = [1.0 for v in  feats]  
  
            if len(Y[seg]) < 10:  
                gds  = GDS(X1[seg], Y[seg],  prior_weights, LR)
                gds.train()  
                weights = gds.weights()
            else:
               weights =  prior_weights


            mdl_results["weights"]  = {}
            for irow, feat in enumerate(feats):
               if seg not in mdl_results["weights"]:
                   mdl_results["weights"][seg] = []

               mdl_results["weights"][seg].append( [feat , weights[irow]])

        mdl_results["creation_date"] = str(datetime.datetime.now())
        mdl_results["feats"]    = list(feats)
        mdl_results["target"]   = target
        mdl_results["segments"] = list(segments )
        mdl_results["epoch"]    = self.epoch 
        self.experience[model_name] = mdl_results

       # X1["result"] = Y

       # t = open("all_weights.csv","a")
       # t.write(json.dumps(X1 )+ "|" + json.dumps(Y ) + "\n")


   
   def objectives_2_moods(self,short_term_memory):
       """

       """  
       index       = "objective"
       target      = "scr"
       cols        = ["moods", "event_interval"]
       self.run_model("objectives_2_moods",index, target, cols, short_term_memory , False)

   ##################### These are for update reactions         
   # objectives_2_moods       emotional_suppressors  # best mood for objective
   # senses_2_moods           emotion_factors        # try not to react 
   # objective_2_strategy     objective_2_strategy   # best strategies for objective (available strategy)
   # strategy_2_mood_scr      todo                   # best strategy by impact on mood (filter on impact)
   # strategy_mood            todo                   # best strategy by current mood (filter on current mood)
   #####################  

  
   def gen_mood_src(self, short_term_memory):
       """
       
       
       """
       scr = self.cognitive_control.mood_binning 

       for key , row  in short_term_memory["stimuli"].items(): 
           row["mood_scr"] =  scr[row["mood"]][0]
           row["mood_bin"] =  scr[row["mood"]][1]

   def senses_2_moods(self, short_term_memory):
        """ 
        sense impact on mood- bright light!

        """ 

        index       = "stimuli_class"
        target      = "scr"
        cols        = ["moods", "event_interval"]
        self.run_model("senses_2_moods", index, target, cols, short_term_memory, False  )
 
   def objectives_2_mood(self,short_term_memory):
        """
        
        best mood for objective
        """  
        index       = "objective"
        target      = "scr" 
        cols        = ["moods", "event_interval"] 
        self.run_model("objectives_2_mood",index, target, cols, short_term_memory, False )


   def objective_2_strategy(self, short_term_memory):
        """ 

        DONE
        
        """ 

        index       = "objective"
        target      = "scr"
        cols        = ["strategy", "event_interval"]
        self.run_model("objective_2_strategy", index, target, cols, short_term_memory, False  )
 
   def strategy_2_mood(self,short_term_memory):
        """

        """  
        index       = "strategy"
        target      = "scr" 
        cols        = ["moods", "event_interval"] 
        self.run_model("strategy_2_mood",index, target, cols, short_term_memory, False )
 
       
   def strategy_2_mood_scr(self,short_term_memory):
        """

        """  

        index       = "strategy"
        target      = "mood_scr" 
        cols        = [ "moods", "event_interval"] 
        self.run_model("strategy_2_mood_scr",index, target, cols, short_term_memory, False )


 
   ##################### These are rethinking objective 
   # objective moods  (if always sad...) 

   ##################### These are for update scr  
   # objectives_met         
   # objectives_umet     
   # objectives_neu  
   
   ##################### These are for global      
   # strategy moods  # may be pulled in 
   # strategy_met         
   # strategy_umet     
   # strategy_neu   


   ##################### These are for update reactions   
   def objectives_met(self,short_term_memory):
       """

       """  
       index       = "goal"
       target      = "scr"
       cols        = ["mood",  "event_interval"]
       self.run_model("emotions_scr_fit", index,target, cols, short_term_memory, False  )


 
   def word_whts(self, short_term_memory):
       """
       disengagement
       
       """ 
       if 'word_weights' in  self.words:
           word_weights  =  self.words["word_weights"] 
       else:
           word_weights = {}
       avg_weights = {'neg': 0.33, 'neu': .33, 'pos': 0.33, 'compound': 0.0}
       for key, details in short_term_memory["stimuli"].items():
          if key in self.dates_done_words:
              continue  
          self.dates_done_words.add(key)
          if 'prior_response'  not in details:
              details["prior_response"] = {}
                      
          if 'speech' in details["prior_response"]:
              prior_statement = details["prior_response"]["speech"][0] 
              scrs = details["scrs"]
              if len(scrs) == 0:
                  continue 
              
              for word in prior_statement.split():
                  if len(word) <= 3:
                       continue 
                  if word in word_weights:
                      old = word_weights[word] 
                      _vals = {}

                      if "query" in scrs: 
                        if scrs["query"] == "failed":
                           scrs = avg_weights
                      else: 
                          for k , v in scrs.items(): 
                              avg_weights[k] = .5*avg_weights[k]  + .5*v
                           
                      for k , v in scrs.items():
                          if k == "query":
                             continue   
                          
                          if k in old:
                              _vals[k] = .5*old[k]  + .5*v
                          else:
                              _vals[k] =  1

                      word_weights[word] = _vals
                  else:
                      word_weights[word] = scrs
 
       self.words["creation_date"]   = str(datetime.datetime.now())
       self.words["epoch"]           = self.epoch 
       self.words["word_weights"]      =  word_weights

   def  reflect(self, short_term_memory={}):
        """
        
        """
        if short_term_memory == {}:
            short_term_memory = self.st_memory.memory

        ########## scr adjustment phase 
        # - readjust scr on each record based on met, umet and all emotions

        ########## Objective evaluation phase 
        # - rank objectives based on met, umet and all emotions

        ########## Decision phase - who to choose
        self.word_whts( short_term_memory) 
 
        self.gen_mood_src(short_term_memory)

        self.senses_2_moods( short_term_memory) 
          
        self.strategy_2_mood(short_term_memory)
        self.strategy_2_mood_scr(short_term_memory)

        self.objectives_2_moods( short_term_memory) 
        self.objective_2_strategy( short_term_memory)   

 
        self.last_reflection =  datetime.datetime.now() 
        self.save()
        return True
 

if __name__ == "__main__": 
    """
    
    """
    import os, sys
    os.chdir('../')
    sys.path.insert(0, os.path.abspath('./')) 
    import config
    from ai.cognitive_control import CognitiveControl
    from ai.personality import Personality
    from memory.st_memory import STMemory 
    from memory.lt_memory import LTMemory

    from triples.triples     import Triples
    s_robot       = "squirrel" 
    triples       = Triples(agent=s_robot,  
                             client=False)    

    personality = Personality("squirrel", config, {} ) 
    #robot, config, settings, personality, low_memory_mode,  update_from_experience = True):
       
    cognitive_control = CognitiveControl("squirrel", config, {}, personality,False,False)

    st_memory = STMemory("squirrel", config, triples, False)
    lt_memory = LTMemory("squirrel", config, triples=triples,load_all=False)
  
    exp =  Experience("squirrel" , config, cognitive_control,
                       personality,  st_memory, lt_memory,False)

    exp.reflect() #True)

    #for key, val in exp.experience.items():
    #    print (key, val)

    cognitive_control.update_weights()