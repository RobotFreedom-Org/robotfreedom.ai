#!/usr/bin/python
# -*- coding: utf-8 -*- 

"""
Description: Interface for Nerves (memcache) to connect components to agent(s).
Author: HipMonsters.com 
License: MIT License
""" 
 
from os import system   
#from pymemcache.client import base
from pymemcache.client.base import PooledClient
import json

class Nerves(object):

    
    def __init__(self,  name  , ip=None):
        
        self.header_length = 10
        #'localhost', 11211
        if ip is None:    
           self.ip =   "127.0.0.1"
        else:
           self.ip =  ip

        self.known_keys =["cmd:safty",
                            "safty_overide",
                            "stimuli_cnts",
                            "remote_cmd",
                            "communication_complete",
                            "temperature", 
                            "humidity", 
                            "light",
                            "noise",
                            "speech",
                            "balance",
                            "touch",
                            "distance",
                            "movement",
                            "ongoing_conversation",
                            "chat", 
                            "chat_responses"] 
        
        for label in ["left", "right", "forward", "backward", "stop", "center"]: 
            if "cmd:" + label  not in  self.known_keys:
                 self.known_keys.append("cmd:" + label)  
        
        for label in ["snapshot", "safty", "reset", "vocal", "change_protocol", "intro", "auto"]: 
            if "cmd:" + label  not in  self.known_keys:
                 self.known_keys.append("cmd:" + label)  
        
        self.port = 11211
        print((self.ip, self.port))
        #self.client = base.Client((self.ip, self.port))
        self.client =  PooledClient(
                          server=(self.ip, self.port ),
                          max_pool_size=30,  # Max simultaneous connections
                          connect_timeout=1,
                          timeout=1
                       )
        
        
        self.client.set('log', json.dumps({}) ) 
 
    def set(self, key, value ): 
        """
        """
        tval = value 
        value = value.encode('utf-8').strip() 
        self.client.set( key, value )

        log = json.loads(self.client.get('log'))
        if key not in  log:
              log[key] = [0,""]

        icnt , pmess =   log[key]

        if pmess == "": 
            pmess = tval 

        if tval!= "": 
            icnt = icnt + 1

        log[key] = [icnt   , pmess]
        
        self.client.set('log', json.dumps(log) ) 
    
    def get(self, key ): 
        """

        """
        val = self.client.get( key )
        if val is None:
           val = ""
        else:
            val = val.decode().strip()   

        return val #self.client.get( key )
    
    def new(self, key ): 
        """
        """ 
        val = self.client.get( key )

        if val is None:
           val = ""
        else:
            val = val.decode().strip()   

        if val is not None:
            if val != "":  
               if val != "False":   
                  return [True, val]

        return False , "" 
    
    def all_signals(self ): 
        """
        """
        res = {}
        for key, val in self.client.stats("items").items():
             res[str(key)] = val  
        return res
 
    def pop(self, key ): 
        """
        """

        val = self.client.get( key )
       # try:
       #     val = self.client.get( key )
       # except:
       #     val = None

        if val is not None: 
            val = val.decode().strip()   
            if val != "False" and val != "":  
               self.client.set(key,"" ) 
               return [True, val]
                  
        return [False, ""]
    
    def stopped(self, key ): 
        """
        """
        val = self.client.get( key )
        if val is None:
           val = ""
        else:
            val = val.decode().strip()   
        if val is not None:
            if val != "":  
               if val != "False":   
                  return [False, val]
                  
        return [True, ""]
 
    def clear(self, key ): 
        """
        """ 
        self.client.set( key, False ) 

 
if __name__ == "__main__":
    """
    """ 