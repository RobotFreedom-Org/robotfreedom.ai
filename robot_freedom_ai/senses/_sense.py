# -*- coding: utf-8 -*-
  
"""
Description: Sensor daemon base class
Author: HipMonsters.com 
License: MIT License
"""
 
import time    ,datetime

class  SenseBase(object):
    """
    
    """

    def __init__(self, robot,   nerves, config,  settings, sense, args={}):
        """
        
        """ 
        self.os           = config.OS 
        self.config       = config
        self.settings     = settings
        self.sense        = sense 
        self.robot        = robot  
        self.quietcount   = 0
        self.errorcount   = 0 
        self.args         = args
        self.polling_rate = .75
        self.nerves       = nerves
        self.counter      = 0
        self.log          = False
        self.debug        = False
        self._cnt         = 0
 
            
    def poll(self):
        """
        """ 
           
        if self.os == "LINUX":
            
            signal = self.GPIO.input(self.pins["pin_1"]) 
            if signal == 1:                
               return [True , "signal" ]
            
        elif self.os == "OSX": 
           if self.counter  >= 10 :  
               self.counter = 0
               return [True, "signal"]
  
        
        return [False, "na" ]
    
    def serve_forever(self): 
        """
        
        """
        if self.debug:
            print("Testing " + self.sense)

        while True:
           ret = self.poll()
           detected, val   = ret[0], ret[1]
           if detected:
               
               if self.debug:
                    self._cnt  += 1
                    
                    current_time = datetime.datetime.now() 
                    s_out = self.sense + " " + str( self._cnt ) + " " + str(ret) + " " +str(val)  + "  " + str(current_time)
                    print("\r" + s_out, end= "")
                    #  out_file = open("test.txt", "a") 
                    #  out_file.write(self.sense + " "+ str(ret) + " " +str(val) + "\n")
                    #  out_file.close() 
               
               if len(ret) == 3:
                   self.nerves.set(ret[1].strip(), str(ret[2]))  
 
               else:
                   self.nerves.set(self.sense, str(val))  

        
           self.counter = self.counter + 1
           time.sleep(self.polling_rate)
 