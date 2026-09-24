     
import json
import random  
import traceback
from collections.abc import Mapping
  
BTriplesParser = True

try:
    from .triples_parser.inference_bayes_triples import TriplesParser 
except:
    BTriplesParser = False 
      
"""
              The five purposes for communication are to 
              inform, imagine, influence, meet social expectations 
              and express feelings
              motives
              TO INFORM 
              TO EDUCATE 
              TO MOTIVATE 
              TO RELATE 
              TO PROMOTE
              TO ENTERTAIN

              user mood, name, fun
              fill i a kg on user
              goals 
                  learn
                       user name
                       how user feels
                       what user enjoys doing
                       what user reads
                  express
                       name
                       thoughts on cats


            more joke to semanetic tirples 
            also add subconscious. i wounder...
            keeps moods here and add to sematic triples
            use cht init to guess spoke stragetgies


 """

def cos_distance(v1, corpus): 

    results = [[i,0] for i, v in enumerate(corpus)]

    for i, v2 in enumerate(corpus): 
        common = v1[1].intersection(v2[1])  
        # by definition of cosine distance we have 
        if v2[2] == 0:
            scr = 0.0
       #elif   v2[0] != v1[0]:  
       #     scr = 0.0 
        else:
            scr = sum(v1[0][ch]*v2[0][ch] for ch in common)/v1[2]/v2[2]  

        results[i] = scr
    return results 

def edit_distance(word1, word2):
    # Validate inputs
    if not isinstance(word1, str) or not isinstance(word2, str):
        raise TypeError("Both inputs must be strings.")

    len1, len2 = len(word1), len(word2)

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

    return dp[len1][len2]

def compare_to_corpus(word, corpus):  
     results = [ ]  

     for i, val in enumerate(corpus): 
         scr = edit_distance(word, val) 

         if scr == 0  :
             scr = 1.0 
         elif len(word) == 0 or len(val) == 0:
             scr = 0.0 
         elif len(val) < len(word):
             scr =  (len(val) - scr)  / float(len(val)) 
         elif len(val) >= len(word):
             scr =  (len(word) - scr)/ float(len(word))
     
         results.append([val ,scr] )

     scores = sorted(results, key=lambda x:x[1], reverse=True)   
     return scores
 
def deep_merge(dict1, dict2):
    """
    Recursively merges dict2 into dict1.
    - Nested dicts are merged deeply.
    - Lists are concatenated without duplicates.
    - Scalars in dict2 override dict1.
    """
    if not isinstance(dict1, Mapping) or not isinstance(dict2, Mapping):
        raise TypeError("Both arguments must be dictionaries or dict-like objects.")

    merged = dict1.copy()  # Start with a shallow copy of dict1

    for key, value in dict2.items():
        if key in merged:
            # If both values are dicts, merge recursively
            if isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = deep_merge(merged[key], value)
            # If both are lists, merge without duplicates
            elif isinstance(merged[key], list) and isinstance(value, list):
                merged[key] = merged[key] + [item for item in value if item not in merged[key]]
            # Otherwise, override with dict2's value
            else:
                merged[key] = value
        else:
            merged[key] = value

    return merged
 
  


class SemanticTriples(object):
    
    def __init__(self, config, lt_mem, st_meme, triples, verbose=False):
  

        self.config = config
        self.verbose =  False #True
        self.last_resp_question = None
        self.user_name = "unknown"
        self.mode = "chat"

        self.st_mem = {}
        self.st_mem["kb_graph"] = {} 
        self.st_mem["kb_graph"]["name"] = {}
        self.st_mem["kb_graph"]["name"]["edges"] = {}

        self.triples  = triples

        self.history = [[{"v":"like", "o":"cat", "s":"you"}, {"v":"love", "o":"cat", "s":"me"}]]
        self.triples_parser = TriplesParser(self.config) 


        self.knowledge_base = triples.TrplGraph() 
        self.response_graph = triples.TrplGraph()
        self.revist_graph   = triples.TrplGraph()

    def try_tool(self, prompt):

            resp  = ""

            b_cmd = False
            potential_tools = self.triples.router.search(prompt.split(" "))   
            pot_tool = potential_tools[0] 
            t_out = open("tools.log", "a")
            t_out.write(prompt + " " + str(pot_tool) + "\n") 

            if  pot_tool[-1] >= 1.8: 
              cmd = pot_tool[1]["function"]   
              if cmd in ["date", "time"]:
                _p = prompt.split(cmd) 
                _s , _o = "", "" 
                if pot_tool[-1] >= .8:  
                    if "s" in pot_tool[1]:
                         _s =  pot_tool[1]["s"]
                     
                    if "o" in pot_tool[1]:
                         _o =  pot_tool[1]["o"]
                      
                params = ["", ""]
                if len(_p) == 1: 
                     params[0] = _p[0]  
                else:
                     params[0] = _p[0] 
                     params[1] = _p[1]   

                if _s != "":
                     params[0] = _s

                if _o != "": 
                     params[1] = _o   
 
                try:     

                    t_out.write("  >ran " + str(cmd) + "\n")
                    resp =   getattr(self.triples, "%s" % cmd.lower().strip())(params[0], params[1])   
                    t_out.write("  >out " + str(resp) + "\n") 

                    if type(resp) is str:
                        resp = [resp]
                        b_cmd = True 

                    elif type(resp) is float:
                        resp = [str(resp)]
                        b_cmd = True 
                        
                    elif type(resp) is list: 
                        b_cmd = True 
                    
 
                except Exception as e:  
                     print(e)
                     print(  traceback.print_exc())
  
            return [b_cmd,  resp]

    def create_plan(self, svo_in, svo_init ,intent): 
        """
        add in check for repeats....
        
        """
        plan =  []
 

        if intent == "inquiry":
           action = {"action":"query", "db":"personal", "value":svo_init}
           plan.append(action)
        
        elif svo_in["v"] in self.triples.functions:
                   action = {"action":"tool", 
                             "function":  svo_in["v"],  
                             "value":svo_in}
                   plan.append(action)
        
                   action = {"action":"formulate", "input":"prior"} 
                   plan.append(action)
           
        elif svo_init["o"] in self.triples.functions:
           action = {"action":"tool", 
                     "function":  svo_init["o"],  
                     "value":svo_init}
           plan.append(action)

           action = {"action":"formulate", "input":"prior"} 
           plan.append(action)

           
        elif svo_init["s"] in self.triples.functions:
           action = {"action":"tool", 
                     "function":  svo_init["s"],  
                     "value":svo_init}
           plan.append(action)

           action = {"action":"formulate", "input":"prior"} 
           plan.append(action)


        else:
           action = {"function":"query", "db":"all", "value":svo_init}
           plan.append(action)

        return plan


    def close(self):
        pass

    def load(self):

        self.triples_parser.load() 

        self.short_term_mem = {} 
        self.short_term_mem["file"]       = "short_term_mem.json"
        self.short_term_mem["merge"]      = False 
        self.short_term_mem["graph"]      = {}   
        self.flips = {}
        self.flips["my"]   = "me"
        self.flips["i"]    = "me"
        self.flips["mine"] = "me" 
        self.flips["yours"]   = "you" 
          
        
        #self.response_graph.load("responses_to_questions")
        #self.revist_graph.load("revist_graph")

        id = self.knowledge_base.get_id() 
        self.knowledge_base.add("you", "how", "feel", {"type":"q", "link_id": id})
        self.knowledge_base.add("me", "feel", "good", {"type":"a", "link_id": id})  

        id = self.knowledge_base.get_id()
        self.knowledge_base.add("you", "what", "name" ,   {"type":"q", "link_id": id}) 
        self.knowledge_base.add("me", "name", "number 3", {"type":"a", "link_id": id})  

        id = self.knowledge_base.get_id()
        self.knowledge_base.add("i", "am", "sad",   {"type":"q", "link_id": id})  
        ##Todo being back after maker fair
       ## self.knowledge_base.add("open", "media", "image ./assets/cinder.jpg", {"type":"a", "link_id": id}) 
        self.knowledge_base.add("soon", "feel", "better", {"type":"a", "link_id": id}) 

        pth = self.config.PATH + "chat/"
        self.knowledge_base.load_trlps(pth + "/personal/", "personal") 

        pth = self.config.PATH + "knowledge/"  

        for line in open(pth+ "common_sense/common_sense.txt"):
            row = line.strip().split("|")
            id = self.knowledge_base.get_id()  
            self.knowledge_base.add(row[0], row[1], row[2], {"type":"a", "link_id": id})  
            self.knowledge_base.add(row[0], row[1], row[2], {"type":"a", "link_id": id})  

        self.knowledge_base.load_trlps(pth + "/THOR_U/", "common_sense")  

        self.triples_parser.knowledge_base    = self.knowledge_base 

     #   self.knowledge_base.load_trlps(pth + "/convo", "convo") 
     #   self.knowledge_base.load_trlps(pth + "/facts", "facts")   


    def check_user(self, user_name):
       
       new = False
       if user_name !=  self.user_name:
           new = True
           self.user_name = user_name 

           if user_name not in self.st_mem["kb_graph"]:
               self.st_mem["kb_graph"][user_name] = {}
               self.st_mem["kb_graph"][user_name]["edges"] = {}
               self.st_mem["kb_graph"][user_name]["edges"]["name"]    = {"type":"s_v"}
               self.st_mem["kb_graph"][user_name]["edges"][user_name] = {"type":"s_o"}
               self.st_mem["kb_graph"]["name"]["edges"][user_name]    = {"type":"v_o"}

       return [self.user_name, new]
           
    def add_user_data(self, user_name, final):
        """
        
        """  
        self.response_graph.add("user", "name", user_name)

    def get_response_type(self, prompt):
        w = prompt
        if w.startswith("i ") or w.startswith("my "): 
            return "sharing"
        
        for w in ["what", "which", "do you", "are you", "want"]:
            if prompt.find(w) > -1:
                return "inquiry"

        for w in ["why", "where", "when"  ]:
            if prompt.find(w) > -1:
                return "question" 
        return "statement"
            
    def revist(self,   history): 

         if len(self.history) == 0:
             return [{}, {}]
         svo  = random.choice(self.history)[0] 

         res1 = self.knowledge_base.similar(svo["s"], 
                                            svo["v"],
                                            svo["o"], {"type":"a"}) 

         if len(res1) == 0:
             return [{}, {}]
             
         fin1 = random.choice(res1)   

         res2 = self.knowledge_base.similar(fin1[0]["s"], 
                                            fin1[0]["v"],
                                            fin1[0]["o"], {"type":"a"}) 

         if len(res2) == 0:
             return [{}, {}]
         fin2 = random.choice(res2)  

         id = self.revist_graph.get_id() 
         self.revist_graph.add(fin1[0]["s"], fin1[0]["v"], fin1[0]["o"] ,  {"type":"q", "link_id": id})
         self.revist_graph.add(fin2[0]["s"], fin2[0]["v"], fin2[0]["o"] ,  {"type":"a", "link_id": id})
  
         self.revist_graph.save("revist_graph")  
         self.history.append([fin1[0], fin2[0]] )

         return  [fin1[0], fin2[0]]

    def inquire(self, svo, details, directives): 
        """ 
        """ 
        reason_cds = {"engine":"inquiry", "scr" :1} 
        s_term = None
        if svo["o"] != "": 
            reason_cds = {"type":"access", "scr" :1} 
            s_term  = svo["o"] 
        elif svo["v"] != "": 
            reason_cds = {"type":"access", "scr" :1} 
            s_term  = svo["v"] 
        elif svo["s"] != "": 
            reason_cds = {"type":"access", "scr" :1}    
            s_term  = svo["s"] 

        if s_term != None:  

            db = "word"

            if directives["strategy"] in ["Witty", "Animated", "Absurd", "Amused"]: 
 
                db = "jokes"
                _question = "not know"

            elif directives["strategy"] in [ 'Aggressive', 'Acerbic',   'Caustic' ,   'Callous' ,  
                                            'Bitter' ,   'Belligerent',  'Accusatory' ,    'Angry' ]: 
 
                
                db = "prior_conversations_rude"
                _question = "why did you say" 

            elif directives["strategy"] in ["Inspirational", "Benevolent", "Altruistic"]: 
 
                 db = "moods"
                 _question = "please  explain" 

            elif directives["strategy"] in ["Direct", "Candid", "Ardent" ,   'Thoughtful',  'Arrogant' ]: 

                db = "facts"  
                _question = "what you mean"
  

            elif directives["strategy"] in ['Assertive' ,  "Diplomatic" , "Informative"]: 
                db = "word"  
                _question = "define"
 
 
            elif directives["strategy"] in [ 'Appreciative']:
                db = "prior_conversations_base"    
                _question = "can you explain" 

            elif directives["strategy"] in [ 'Apathetic' ,  "Ambivalent" ]:
                db = "prior_conversations_rude"    
                _question = "why say" 

            elif directives["strategy"] in [ "Apologetic" , 'Cautionary' ]:  
                db = "prior_conversations_base"    
                _question = "sorry what is" 

            elif directives["strategy"] in [ "Admiring" ]:
                db = "prior_conversations_base"    
                _question = "interesting can you define" 
        
            elif directives["strategy"] in [ 'Aggrieved'  ] :
                db = "prior_conversations_base"    
                _question = "not understand" 
            else:
                _question = "not understand" 
                t = open("star_not_forund.log", "w")
                t.write(str(directives["strategy"]) + "\n")


            code = []
            code.append({"v":"define", "s":db , "o": s_term + "->research_tmp"} )
            code.append({"v":"element", "s":"research_tmp","o": "0 -> research_v"})
            code.append({"v":"element", "s":"research_tmp" ,"o": "1 -> research_scr"})
            code.append({"v":"set", "s":"v1" , "o": ".3"})
            code.append({"v":"flow", "s":"if" , "o": "start"})
            code.append({"v":"less", "s":"research_scr" , "o": "v1"})
            code.append({"v":"echo", "s": '"' + _question + " " + s_term + '"', "o":"" })
            code.append({"v":"flow", "s":"if" ,"o": "end"} )
            code.append({"v":"flow", "s":"if" , "o": "start"}  )
            code.append({"v":"more", "s":"research_scr" , "o": "v1"})
            code.append({"v":"echo", "s":"research_v", "o":""})
            code.append({"v":"flow", "s":"if" , "o": "end"}  )  

            return [code  ,reason_cds ]
        
        elif len(directives["situation"]) > 0:

            reason_cds = {"engine":"no info", "scr" :1} 

            fin =  self.get_thoughts(self, details, directives)
            return [[fin] ,reason_cds ] 

        else:

            reason_cds = {"engine":"no info", "scr" :1} 
            fin =  {"s":"you", "v":"repeat", "o": "statement"}
            return [[fin] ,reason_cds ] 
    
 
    def get_thoughts(self, details, directives):
       """ """

       ## move to graph
       stim_resp = {"tilt":[{"s":"me", "v":"be", "o":"careful"}, 
                            {"s":"wow","v":"", "o":""} ],
                    "light":[{"s":"who", "v":"changed", "o":"lights"}],
                    "sound":[{"s":"something out there", "v":"", "o":""},
                              {"s":"hello",  "v":"", "o":""},
                               {"s":"is anyone there",  "v":"", "o":""},],
                    "tempature":[{"s":"am i in the sun", "v":"", "o":""},],
                    "humidity":[{"s":"me", "v":"", "o":""},],
                    "touch":[{"s":"hello", "v":"", "o":""}, 
                             {"s":"", "v":"how are", "o":"you"}, 
                             {"s":"me", "v":"thank", "o":"you"}], 
                    "distance":[{"s":"hello there", "v":"", "o":""}], 
                    "movement":[{"s":"me" , "v":"detect", "o":"movement"}], 
                    }

       itype = random.randint(0, 18)
       response = []

       if directives["situation"]["last_stimuli"]["code"] in stim_resp and itype < 5:
            response  = random.choice(stim_resp[ directives["situation"]["last_stimuli"]["code"] ])

       if  itype  < 3:   
             response = {"s":"stimuli" ,"v":"detected" , "o":details["situation"]["last_stimuli"]["code"]  }
       elif  itype  < 6:   
                response = {"s":"mood" ,"v":"current" , "o":directives["mood"]   }
       elif  itype  < 12: 
            if  details["polarity_scores"]["neg"] >   details["polarity_scores"]["pos"]:
                response = {"s":"stimuli" ,"v":"impact" , "o":"negative"   }
            else:
                response = {"s":"stimuli" ,"v":"impact" , "o":"positive"   }
                
       return response 

    def ret_triples(self, query):
           triple_in   =  {"s":"", "o":"", "v":""} 
           _triple_in = self.triples_parser.triple_inference([query])     
           if type(_triple_in) is str: 
               return triple_in
            
           for key, value in _triple_in.items(): 
               _out = []
               for w in value.strip().split():
                    
                    w = self.response_graph.lemmatize(w) 

                    if w in self.flips:
                        w = self.flips[w]
                    _out.append(w)    
               _t= " ".join(_out)
               triple_in[key] = _t.strip() 
           return triple_in

    def analyize(self,  query, sia):
       
 
        triple_in =  self.ret_triples(query)  
        if len(triple_in) == 0 or type(triple_in) == str:
           triple_in = {"s":"", "v":"", "o":""}  
         
        graph_query = {"s":"", "v":"", "o":""}  

        final     = {k:v.strip()  for k, v in triple_in.items()} 
        triple_in = {k:v.strip()  for k, v in triple_in.items()}  

        b_ok = False
        if  final["o"] != "" and  final["v"] != "" and  final["s"] != "":
           b_ok = True  

        _potentials       =  {"s":{"":.0}, "v":{"":.0}, "o":{"":.0}}   

        for edge_type, q in triple_in.items():
             
               if q in self.flips:
                   q = self.flips[q] 
    
               q = self.knowledge_base.lemmatize(q) 
               scores = compare_to_corpus(q, list(self.knowledge_base.r_v.keys()))   
              
               for word, v in scores[:3]:  
                   v_id = self.knowledge_base.r_v[word]
                   pot_edge_type  = self.knowledge_base.v[v_id]["base_type"][0] 
                   if v > .80 : #and pot_edge_type == edge_type:    
                     if word not in _potentials[edge_type]:
                           _potentials[pot_edge_type][word] = v  
                     else:
                         if v > _potentials[edge_type][word]:
                            _potentials[pot_edge_type][word] =  v
 
        potentials = []
        for s, s1 in _potentials["s"].items():
            for v , v1 in _potentials["v"].items():
                for o , o1 in _potentials["o"].items():
                    scr = s1 + v1 + o1
                    potentials.append([{"s":s, "v":v, "o":o},scr ])

        if len(potentials) > 0:
            potentials = sorted(potentials , key=lambda x:x[1], reverse=True)  
            graph_query = {k:v for k,v in potentials[0][0].items()}

        return [potentials, graph_query , triple_in, b_ok] 

    def respond(self, user_response, details , history , low_memory_mode ,  directives):
           """
           
           
           """

           if user_response.find("initiate mode learning") > -1:
               self.mode = "learning"
               return ["initiated learning mode", {}]
               
           elif user_response.find("initiate mode chat") > -1:
               self.mode = "chat"
               return ["initiated chat mode", {}]
           
           if self.mode == "learning":
               
               potentials    = self.analyize(user_response, 
                                             details["processed"]["sia"]  )    
               print(potentials)
               ## self.knowledge_base.add(s,v,o)
               ## self.knowledge_base.save()
               return ["learned  ", {}]
               
           if len(details) == 0: 
               details = {} 
               details["processed"]  ={}
               details["processed"]["sia"] = 1
               details["processed"]["Intent"] ="inquiry" 
            
           situation = directives["situation"] 
           potentials    = self.analyize(user_response, 
                                          details["processed"]["sia"]  )    
           
 
           b_tool , resp= self.try_tool(user_response)

           if b_tool:
               reason_cds = {"engine":"tools", "scr" :1}  
               if type(resp) is dict:
                   resp = [str(resp)]
               elif type(resp) is float:
                   resp = [str(resp)]
               elif type(resp) is str:
                   resp = [str(resp)]
               elif resp  is None:
                     resp = [ "na"]
               svo = {"s": " ".join(resp), "v":"", "o":""}
               fin = [{"s": " ".join(resp), "v":"", "o":""}]
           else:
               
               resp  , reason_cds = self.closest_match(potentials, details , history , low_memory_mode ,  directives) 
  
               if resp[0]["s"] == "" and resp[0]["s"] == "" and resp[0]["s"] == "":
                    
                   links, cd = self.inquire(potentials[2], details, directives )
                   self.last_resp_question = links[-1] 

               elif resp[1] <= 2: 
                    links, cd = self.inquire(potentials[2],details, directives ) 
 
               else: 
                   links = self.knowledge_base.linked(resp[0]["s"], resp[0]["v"],resp[0]["o"],)

               if len(links) == 0: 
 
                   
                   plan = self.create_plan(potentials[0][0][0], resp[0], details["processed"]["Intent"]) ## for multistrp 
                   links = [resp[0]] 

          
               fin = [] 
           
               for svo in links: 
             
                  if svo["v"] in self.triples.function_lkup: 
                      try: 
                          t_out =  getattr(self.triples, "%s" %  svo["v"].lower().strip())( svo["s"],  svo["o"])  
                      except:
                          t_out = None 

                      if t_out is None:
                           pass 
                      
                      elif type(t_out) == dict: 
                          fin.append(t_out)

                      elif type(resp) == list:  
                            for _resp in t_out:
                                fin.append({"s":_resp ,"v":"", "o":""})
                      elif t_out != "": 
                          fin.append({"s":t_out ,"v":"", "o":""}) 
                  else:
                      fin.append(svo) 
 
               if len(fin) == 0:  
                   fin.append(resp[0]) 
 
           reason_cds = {"engine":"triples", "scr" : 1}  

           if  type(potentials[0]) is dict:
               pass
           else: 
               potentials = [{"s":"arg" ,"v":"", "o":""}]


           if  type(fin[0]) is dict:
               pass
           else: 
               fin = [{"s":"arg" ,"v":"", "o":""}]

           self.history.append([ potentials[0], fin[0] ] )
           if len(self.history) > 100:
               self.history = self.history[-100:]
           

           return [fin , reason_cds]
  
    def closest_match(self, potentials, details , history , low_memory_mode ,  directives): 

        self.verbose = False
        if self.verbose: 
            _t = open("sematic_triples.log", "a")
            _t.write(str(potentials) + "\n") 

        reason_cds = {"engine":"triples", "scr" : 1}  
 
        svo = {"s":"", "o":"", "v":""}
        if  self.last_resp_question is not None: 

            svo = potentials[2]
           # id = self.response_graph.get_id() 
           # self.response_graph.add(self.last_resp_question["s"],
           #                         self.last_resp_question["v"],
           #                         self.last_resp_question["o"] ,  {"type":"q", "link_id": id}) 
           # self.response_graph.add(svo["s"],svo["v"],svo["o"]   ,  {"type":"a", "link_id": id})
 
            self.last_resp_question = None
           # self.response_graph.save("responses_to_questions")
       
        for svo, scr in potentials[0]: 
             res = self.knowledge_base.similar(svo["s"], 
                                               svo["v"],
                                               svo["o"], {"type":"a"}) 
             
             if len(res) > 0: 
                _fin= random.choice(res)  
                fin = [_fin[0] ,_fin[1]] 
                if fin[1] > 0:
                   break 
        else: 
           fin = [ {"v":"", "s":"", "o":""}, -1]

        if self.verbose:  
              _t.write(str(fin) + " 1 \n")   
              _t.write(str(svo) + " 2 E \n") 
              _t.write(str(fin) + " 2 F \n") 
              _t.write(str(self.last_resp_question) + " 2 C \n") 
  
        return  [fin, reason_cds]
         
    def responense(self, svo):
       
        final = []
        potentials   = {}
        _potentials  = {} #sorted(_potentials.items(), key=lambda x:x[1][0], reverse=True)  
        self.verbose = False
 
        #{'s_q_v_q', 's_q_o_q', 's_v', 'v_q_v', 'v_q_o_q', 'v_v_q', 's_s_q', 's_o'}
        edges_wgt_adj =  {"s_q_o":2,
                          "s_q_s":2,
                          "s_q_v":1.9,

                          "s_v":1.8,
                          "s_v":1.8,
                          "s_v":1.7,

                          "s_v_q":.5,
                          "s_v_q":.5,
                          "s_v_q":.4,

                          "s_q_o_q":.2,
                          "s_q_s_q":.2,
                          "s_q_v_q":.19,


                          }  
 

        for stype in  ["o","v","s"]:

            value = svo[stype]
            if value == "":
                continue    
            
            if self.verbose:
                  print("query", value, stype)  
            
            if stype == "s": 
                intersections_a =   svo["o"]
                intersections_b =   svo["v"]
            elif stype == "o":
                intersections_a =   svo["v"]
                intersections_b =   svo["s"]
            elif stype == "v":
                intersections_a =   svo["o"] 
                intersections_b =   svo["s"] 


            def third_type(a,b):
                if a in ["s", "o"] and b in ["s", "o"]:
                    return "v"
                elif a in ["s", "v"] and b in ["s", "v"]:
                    return "o"
                elif a in ["v", "o"] and b in ["v", "o"]:
                    return "s" 
            for grph  in ["qa" , "emotional"]:
              if value in self.models[grph]["graph"]["edges"]:

                edges = {k:prop for k, prop in self.models[grph]["graph"]["edges"][value].items()  } 
               
                for to_node, prop in edges.items():   
                    
                    to_type  = prop["type"]
                    to_type = to_type.replace("_q", "") 
                    to_type = to_type.split("_")[-1]  

                    if stype ==  to_type:
                          continue 
                    
                    base_scr = 1
                    if to_node == intersections_a or to_node ==  intersections_b:
                        base_scr = 2 
                    
                    res = {"s":"", "o":"", "v":""}
                    res[stype] = value  
                    res[to_type] = to_node  
                         
                    if prop["type"] in edges_wgt_adj:
                        base_scr += edges_wgt_adj[prop["type"]] 

                    missing_type = third_type(stype, to_type)

                    if missing_type in  ["o","s"]:
                         query_types = [ "s", "o"]
                    elif missing_type == "v":
                          query_types = [ "v"]  

                    _res  = {}
                    for k, v in res.items():
                        _res[k] = v  
                     
                    final.append([_res, base_scr])
                          
                    for query_type in query_types:  
                         
                         child_edges = {k:prop for k, prop in self.models[grph]["graph"]["edges"][to_node].items() if prop ["type"].endswith(query_type )}   

                         for child_edge , child_edge_prop in child_edges.items(): 
                                      
                                     scr = base_scr  
                                     mis_type  = child_edge_prop["type"].replace("_q", "").split("_")[-1]

                                     if res[mis_type] != "":
                                         continue 
                                     
                                         
                                     if child_edge == intersections_a or child_edge ==  intersections_b:
                                         scr += 1

                                     _res  = {}
                                     for k, v in res.items():
                                         _res[k] = v  
                                     _res[mis_type] = child_edge 
                                     final.append([_res, scr])
  
       
        if len(final) > 0:  
            final = sorted(final , key=lambda x:x[1], reverse=True)   

        if len(final) > 0:    
           return final[:6]
        else:        
           return [[{"s":"me", "v":"not undertand", "o":"you"},-1.0, -1]]

if __name__ == "__main__": 
    """   

    https://www.kaggle.com/datasets/duketemon/wordnet-synonyms?select=synonyms.csv

    """  
    import os, sys
    os.chdir('../../')
    sys.path.insert(0, os.path.abspath('./')) 
 
    from memory.st_memory import STMemory
    from memory.lt_memory import LTMemory 
    import config   
    from triples.triples     import Triples

    from communication.client    import Client
    from communication.nerves    import Nerves    

    settings = {}
    nerves = Nerves("User")
    
    from ai.models.triples_parser.inference_bayes_triples import TriplesParser 
     
    communication_ip   = list(config.NET_CONFIG["hubs"].keys())[0]   
    communication      = None
    if 1==3 and communication_ip is not None:
          try:
             communication = Client( "user", communication_ip)
             communication.connect()
          except: 
             communication  = None
     
    s_robot       =  "squirrel"
    

    triples  = Triples(agent="user", 
                       config= config,
                       communication= communication,
                       nerves= nerves,
                       client= False )    

    st_mem        =  STMemory(s_robot, 
                              config, 
                              triples,
                              False) 
    lt_mem        =  LTMemory(s_robot, 
                              config, 
                              triples=triples,
                              load_all=True)     
     
    semantic_triples = SemanticTriples(config,
                                       lt_mem, 
                                       st_mem, 
                                       triples 
                                       )
    
    
    triples.graphs["context"] = st_mem.memory["kb"]
    triples.graphs["definitions"] = lt_mem.memory["definitions"]
    triples.graphs["facts"] = lt_mem.memory["facts"]
    triples.graphs["jokes"] = lt_mem.memory["jokes"]
    triples.graphs["prior_conversations_base"] = lt_mem.memory["prior_conversations_base"]
    triples.graphs["prior_conversations_rude"] = lt_mem.memory["prior_conversations_rude"]
                
        
    semantic_triples.load()
    test_tyoe = 1
    directives =  {"situation":{}, "strategy":"Witty"}
    if test_tyoe == 1:
       while True:
           user_input = input('CHAT: ') 
           response_type = semantic_triples.get_response_type(user_input)    
           resp , reason_cds =  semantic_triples.respond(user_input, {}, [] , False , directives)   
           ai_response = "" 
           for ret_svo in resp:
                  ai_response += ret_svo["s"] +" " + ret_svo["v"] + " "  + ret_svo["o"]  + ". "
           print(ai_response)

    elif test_tyoe == 2:
        i  = 0
        for line in open("../data/chat/norm_convo.json"): 
           i +=1
           if i > 10000000:
               break
           row = json.loads(line.strip()) 
           user_input = row["prompt"]
           print(" >" + user_input)
           response_type = semantic_triples.get_response_type(user_input)   

           resp , reason_cds =  semantic_triples.respond(user_input, {}, [] , False ,  {})     
          
           ai_response = ""
           for ret_svo in resp:
                ai_response += ret_svo["s"] +" " + ret_svo["v"] + " "  + ret_svo["o"]  + ". "

           print(ai_response)
 
        