#!/usr/bin/python
# -*- coding: utf-8 -*- 
""" 
Author: HipMonsters.com  
License: MIT License  
"""   
import time 
import json 
import statistics    

from  .utils.utils import dispatcher 
"""
     analysis max scr;
        {"stimuli": "sense", "stimuli_class": "speech", "amplitude": 1, 
        "signal": "so it's i'm up here", 
        "prior_response": {"speech": ["you what name"], "movement": [["random", "random", "random"]], 
        "locomotion": []}, "scr": 0.1, "scrs": {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0}, 
        "motivations": {"processing": 0, "empathy": 0.04652115793525531,
          "sharing": 0.03188112586788982, "curiosity": 0.04711759950000001},
            "mood": "happy", "moods": {"happy": 2.5634829999999997, 
            "sad": 1.416758, "fear": 0.7197039999999999, "disgust": 0.5811669999999999, 
            "anger": 0.884512, "bored": 0.53575, "surprised": 1.694026}, 
            "objective": "engagement", "strategy": "Assertive",
              "emotional_suppressors": {"happy": 1.0, "sad": 1.0, "fear": 1.0, "disgust": 1.0, 
              "anger": 1.0, "bored": 1.0, "surprise": 0.0, "time_delta": 0.0, "stimuli_class": 0.0}, 
              "stimuli_time": "2026-08-07 12:00:19.057095", "event_interval": 0.684534, "epoch": 6195} 
"""
    
class SensorTriples(object):
 
    def __init__(self):
        """
        functions for analyizing and seeing sensor logs
        """ 
        pass 
    
    @dispatcher
    def readings(self: object, in_subjects:str= "", in_objects: str ="" )-> str:
        """
        provides data sample of sensor readings
        """ 
        if len(  self.memory["log"]) == 0: 
           with open(self.config.PATH + "settings/" + self.agent + "/stimuli.json", "r", encoding='utf-8') as f:
             for line in  f:
                 try:
                     row = json.loads(line.strip()) 
                     if  row["stimuli_class"] not in self.memory["log"]:
                         self.memory["log"][row["stimuli_class"]] = [] 
                     self.memory["log"][row["stimuli_class"]].append(row)

                 except:
                     pass 
            
        if in_subjects == "":
            res = []
            for sen in self.memory["log"].keys():

                row = self.memory["log"][sen][-1] 
                _res   =  row["stimuli_class"] + " amplitude  " + str(row["amplitude"]) + " polarity  " + str(row["scr"]) +  " signal  " + str(row["signal"])
             
                res.append(_res)
        else:
            row =  self.memory["log"][in_subjects][-1]
            _res   =   row["stimuli_class"] + " amplitude  " + str(row["amplitude"]) + " polarity  " + str(row["scr"]) +  " signal  " + str(row["signal"])
            res = [_res]

        return res
    

    @dispatcher
    def analysis(self: object, in_subjects:str= "", in_objects: str ="" )-> str:
        """
        Does standard analstsis on sensor readings 
        """
        if len(  self.memory["log"]) == 0: 
           with open(self.config.PATH + "settings/" + self.agent + "/stimuli.json", "r", encoding='utf-8') as f:
             for line in  f:
                 try:
                     row = json.loads(line.strip()) 
                     if  row["stimuli_class"] not in self.memory["log"]:
                         self.memory["log"][row["stimuli_class"]] = [] 
                     self.memory["log"][row["stimuli_class"]].append(row)

                 except:
                      print(line) 
         
        apresp = in_subjects.split("|")
        if in_subjects =="cnt": 
            return  len(self.memory["log"][in_objects])
        
        elif apresp[0]  =="max":  
            if len(apresp) == 2:
                return  max([ v [apresp[1]] for v in self.memory["log"][in_objects]])  
            if len(apresp) > 3:
                return  max([ v[apresp[1]][apresp[2]] for v in self.memory["log"][in_objects]])   
            else: 
                return  max([ v ["amplitude"] for v in self.memory["log"][in_objects]])  
        
        elif apresp[0]  =="min":  
            if len(apresp) == 2:
                return  min([ v [apresp[1]] for v in self.memory["log"][in_objects]])  
            if len(apresp) > 3:
                return  min([ v[apresp[1]][apresp[2]] for v in self.memory["log"][in_objects]])   
            else: 
                return  min([ v ["amplitude"] for v in self.memory["log"][in_objects]])   
        
        elif apresp[0]  == "mean":   

            if len(apresp) == 2:
                return  statistics.mean([ v [apresp[1]] for v in self.memory["log"][in_objects]])  
            if len(apresp) > 3:
                return  statistics.mean([ v[apresp[1]][apresp[2]] for v in self.memory["log"][in_objects]])   
            else: 
                return  statistics.mean([ v ["amplitude"] for v in self.memory["log"][in_objects]])     
     
        elif apresp[0]  == "summarize": 
   
            if in_objects == "":
                res = []
                for sen in self.memory["log"].keys():
            
                    rows = self.memory["log"][sen]
                    #mx_amp = max([row["amplitude"] for row in rows])
                    #mn_amp = max([row["amplitude"] for row in rows])
                    #avg_amp = statistics.mean([row["amplitude"] for row in rows])
                    mx_scr  = round(max([row["scr"] for row in rows]),3)
                    mn_scr  = round(min([row["scr"] for row in rows]), 3)
                    avg_scr = round(statistics.mean([row["scr"] for row in rows]), 3)
                    _res   =  rows[0]["stimuli_class"]  + " polarity: mean " + str(avg_scr)  + " max " + str(mx_scr)  + " min " + str(mn_scr) 
                    res.append(_res)
            else:
                rows =  self.memory["log"][in_objects]  
                mx_scr = max([row["scr"] for row in rows])
                mn_scr = max([row["scr"] for row in rows])
                avg_scr = statistics.mean([row["scr"] for row in rows])
                _res   =   rows[0]["stimuli_class"] + " polarity: mean " + str(avg_scr)  + " max " + str(mx_scr)  + " min " + str(mn_scr) 
    
            return  res  
   
        elif apresp[0]  == "correlate" : 

            a_in_objects = in_objects.split("|")
            rows1 =  [row["scr"] for row in  self.memory["log"][a_in_objects[0]]    ]
            rows2 =  [row["scr"] for row in  self.memory["log"][a_in_objects[1]]  ]
         
            if len(rows1) > len(rows2):
               rows1 = rows1[:len(rows2)]
            else:
               rows2 = rows2[:len(rows1)] 
            avg_scr = statistics.correlation(rows1, rows2)
            return avg_scr
        else:
            return  self.memory["log"][in_objects][-1]
     
    
    @dispatcher  
    def monitor(self: object, in_subjects:str= "", in_objects: str ="" )-> str:
        """runs a loop to see real-time reading from agent"""
        vals = "" 
        for i in range(10):
            for topic in ["chat", "chat_responses", "speech", "sound"]  :
                mess = self._nerves.get(topic) 
                if mess != "":
                    vals += topic + " " + mess + "\n"
                time.sleep(.1)
        return vals 
   

if __name__ == '__main__': 
     """
     
     """  
     pass
 