import datetime


class SensorFusion():


    def __init__(self,st_memory , lt_memory, triples):

        
        self.st_memory = st_memory
        self.lt_memory = lt_memory
        self.triples   = triples


        self.rules = {}  
        self.rules["threat"]      = [{"balance":1}, {"noise":1}]
        self.rules["weather"]     = [{"light":1}, 
                                     {"temperature":{"lt":[75,-1] , "gt":[85,-1 ]  } },
                                     {"humidity": {"lt":[40,-1] , "gt":[75,-1 ]  } },
                                     ]
        self.rules["lifeforms"]   = [{"movement":1}, {"distance":1}]
        self.rules["humans"]       = [{"speech":2},{"touch":2}]
        self.rules["moving"]      = [{"balance":1}, {"movement":1}, {"distance":1} ]
        self.rules["activity"]    = [{"balance":1}, {"noise":1}, {"speech":1}, {"movement":1}] 
        self.rules["ambiance"]    = [ {"tone":{"lt":[0,-1] , "gt":[1,1 ]  } },]
        self.rules["user_present"]= [{"user_detected":1}, ]


        self.codes = {}
        self.codes["lifeforms"]   = [["alone",     [0,0]], ["present",[1,2]   ], ["multible",[3,None]]]
        self.codes["humans"]      = [["alone",     [0,0]], ["present", [1,2]  ], ["multible",[3,None]] ]
        self.codes["threat"]      = [["low",       [0,0]], ["elevated", [1,2] ], ["high",[None,3]]]
        self.codes["weather"]     = [["poor",   [None,0]], ["fair", [0,2]     ], ["good",[3,None]]]
        self.codes["moving"]      = [["stationary",[0,2]], ["moving",[3,None]]]
        self.codes["activity"]    = [["low",       [0,0]], ["elevated", [1,2] ], ["high",[3,None]] ]
        self.codes["ambiance"]    = [["poor",   [None,0]], ["fair", [1,2]     ], ["positive",[3,None]]]
        self.codes["user_present"]= [["false",  [None,0]], ["true",[1,None]]]


        """

{'individuals': {'cnt': 0, 'creators': 0, 'desciption': 'alone'}, 
'threat': {'cnd': 1, 'code': 'high'}, 
'weather': {'cnd': 0, 'code': 'poor'}, '
'lifeforms': {'cnd': 3, 'code': 'multible'}, 
'human': {'cnd': 5, 'code': 'multible'}, 
'moving': {'cnd': 3, 'code': 'moving'}, 
'activity': {'cnd': 4, 'code': 'na'}, 
'ambiance': {'cnd': 19, 'code': 'positive'}, 
'user_present': {'cnd': 2, 'code': 'na'}}
        """

        self.estimates = {}  
 
        self.estimates["lifeforms"]   = {"cnt": 0,    "code":"alone"} 
        self.estimates["humans"]       = {"cnt": 0,    "code":"alone"}
        self.estimates["threat"]      = {"level":0,   "code":"low" }
        self.estimates["weather"]     = {"overall":2, "code":"fair"}
        self.estimates["moving"]      = {"overall":2, "code":"fair"}
        self.estimates["activity"]    = {"overall":2, "code":"fair"}
        self.estimates["ambiance"]    = {"overall":2, "code":"fair"}
        self.estimates["user_present"]= {"overall":0, "code":"negative"}   

        self.sensor_history = {}
         

        self.reset()
        

    def reset(self):
        #define number of people , possible creator, dog
        self.sensor_history["touch"]    = {"cnt":0, "amplitude":0}
        self.sensor_history["distance"] = {"cnt":0, "amplitude":0}
        self.sensor_history["movement"] = {"cnt":0, "amplitude":0}

        #self.sensor_history["infrared"]   = {}
        #self.sensor_history["camera"]     = {}
        #self.sensor_history["proximity"]  = {}
        #self.sensor_history["keycard"]    = {}
        #self.sensor_history["wearable"]   = {}
        #self.sensor_history["safty_override"]   = {}
        #self.sensor_history["voice_recognition"] = {}
        #self.sensor_history["person_recognition"] = {}
        #self.sensor_history["shape_recognition"] = {}
 
        self.sensor_history["user_detected"] = {"cnt":0, "amplitude":0}

        self.sensor_history["speech"] = {"cnt":0, "amplitude":0} 
        self.sensor_history["noise"] = {"cnt":0, "amplitude":0}
        self.sensor_history["balance"]    = {"cnt":0, "amplitude":0} 
        self.sensor_history["temperature"] = {"cnt":0, "amplitude":0}
        self.sensor_history["humidity"]    = {"cnt":0, "amplitude":0}
        self.sensor_history["light"]       = {"cnt":0, "amplitude":0} 
        self.sensor_history["tone"]        = {"cnt":0, "amplitude":0}

 
    def update(self, stimuli_class,amplitude,stimuli_time,scr, scrs,user_detected):
         
         self.reset() 
         
         for str_stimuli_time in  self.st_memory.memory["stimuli_sequence"][-10:]:

              
              data = self.st_memory.memory["stimuli"][str_stimuli_time] 
              sense = data["stimuli_class"] #amplitude epoch  interval
              hist=  self.sensor_history[sense]
              hist["cnt"] = hist["cnt"] + 1
              amp = 0
              try:
                  amp = float(data["amplitude"])
                  amp = amp/hist["cnt"]
              except:
                  pass
              hist["amplitude"] = amp
              self.sensor_history[sense] = hist


              hist=  self.sensor_history["tone"]
              hist["cnt"] = hist["cnt"] + 1
              amp = data["scr"]
              if hist["cnt"]  > 0:
                  amp = amp / float(hist["cnt"] )
              hist["amplitude"] = amp

              self.sensor_history["tone"] = hist

         hist=  self.sensor_history["user_detected"]
         hist["cnt"] = hist["cnt"] + 1 
         hist["amplitude"] = hist["cnt"] 

         self.sensor_history["user_detected"] = hist
              
         if  stimuli_class in  self.sensor_history:
              hist =  self.sensor_history[stimuli_class]
         else:
              hist =  {"cnt":0, "amplitude": 0}
         hist["cnt"] = hist["cnt"] + 1
         amp = 0
         try:
             amp = float(amplitude)
             amp = amp/hist["cnt"]
         except:
             pass
         hist["amplitude"] = amp
         self.sensor_history[stimuli_class] = hist

         self.estimates["last_stimuli"] = {"tot":hist["cnt"], "amp": hist["amplitude"] , "code": stimuli_class}

         

    def reason(self):


        for situation,  rule in self.rules.items():
         cnt = 0
         amp = 0  
         tot = 0
         for cmds in rule:  
           for sense ,  details in cmds.items(): 
             cnt =  self.sensor_history[sense]["cnt"]
             amp =  self.sensor_history[sense]["amplitude"]
             if type(details) is dict:  
                 v = 1
                 if amp > details["gt"][0]:
                     v =  details["gt"][1]
                 if amp < details["lt"][0]:
                     v =  details["lt"][1]
                 tot +=  v
             else:
                 tot += details*cnt

           code_rules = self.codes[situation]
           cd = "na"
           #  self.codes["user_present"]= {"false":[None,0], "true": [1,2], "true":[3,None]}  
           for desc, rule in code_rules: 
               if rule[0] is None:
                 if  tot <= rule[1]:
                     cd = desc
                     break
                   
               elif rule[1] is None:
                 if tot >= rule[0] :
                     cd = desc 
                     break
               else:
                 if tot >= rule[0] and tot <= rule[1]:
                     cd = desc
                     break
                    
           #self.codes["lifeforms"]   = {"alone":[0,0], "present": [1,2], "multible":[3,None]} 
           self.estimates[situation] = {"tot":tot, "amp": amp , "code": cd}

 

        return self.estimates
