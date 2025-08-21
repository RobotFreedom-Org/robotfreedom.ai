# -*- coding: utf-8 -*-
"""
Description: Sensor daemon for temperature and humidity.
Author: HipMonsters.com 
License: MIT License
https://github.com/jesus1a/Vibe
sudo rpi-update 

"""
import json 

try: 
   from ._sense  import SenseBase
except:
   from _sense  import SenseBase

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode")  
parser.add_argument("-r", "--robot") 
parser.add_argument("-a", "--args")    




class  Balance(SenseBase):

    def __init__(self, robot, nerves, config, settings, pins ={"pin_1":27}):
        """
        
        """
        super().__init__(robot, nerves, config, settings, "balance") 
        
        self.pins = pins
        self.args["max"] = 20
        if self.os == "LINUX":
               import RPi.GPIO as GPIO
               import time as time  
               #setting up GPIO
               self.channel = pins["pin_1"]  
               self.GPIO = GPIO
               self.GPIO.setmode(GPIO.BCM) 
               self.GPIO.setup(self.channel, GPIO.IN) 
               self.start_tilt_level   = self.GPIO.input(self.channel)     
               self.current_tilt_level = self.GPIO.input(self.channel)

        self.sense = "balance"  
        self.counter = 0  

    def vibrationFound(self, channel):

        if self.GPIO.input(channel):  
             self.nerves.set(self.sense, "tilt")  
            
    def poll(self):
        """
        """ 
           
        if self.os == "LINUX":
                             
            current_tilt_level = self.GPIO.input(self.channel)
            if abs(current_tilt_level - self.current_tilt_level) != 0:       
               self.current_tilt_level =    current_tilt_level      
               return [True , str(current_tilt_level)]
            
        elif self.os == "OSX":
            
           if self.counter  >= self.args["max"]: 
               self.counter = 0
               return [True, "timeout"]

        
        return [False, ""]
     

if __name__ == "__main__":
    """ 
     python3 balance.py -r number_2 -m test
    
    """
    import os, sys
    os.chdir('../')
    sys.path.insert(0, os.path.abspath('./')) 
    import config
    from communication.nerves         import Nerves  

    args    = parser.parse_args()  
    mode    = args.mode 
    robot   = args.robot   
   # args    = json.loads(args.args  ) 

    with open( config.DATA_PATH  + robot + "/settings.json") as f:
        data = ''
        for row in f:
           data += row  

    settings = json.loads(data)

    nerves     = Nerves(robot) 

    args =  parser.parse_args() 

    mode    = args.mode 
    robot   = args.robot    
 
    balance  = Balance(robot, nerves, config, settings )
    if mode == "serve":
        balance.serve_forever()

    elif mode =="test":
        balance.debug  = True
        balance.serve_forever()
