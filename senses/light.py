# -*- coding: utf-8 -*-
"""
Description: Sensor daemon for temperature and humidity.
Author: HipMonsters.com 
License: MIT License
https://www.electronicshub.org/raspberry-pi-dht11-humidity-temperature-sensor-interface/
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


class  Light(SenseBase):

    def __init__(self, robot, nerves, config, settings, pins ={"pin_1":22}):
        """
        
        """
        super().__init__(robot, nerves, config, settings, "light") 
        
        self.start_light_level = 0  
        self.current_light_level = 0   
        self.pins = pins
        if self.os == "LINUX":
               import RPi.GPIO as GPIO
               self.channel = pins["pin_1"]        
               self.GPIO = GPIO
               self.GPIO.setmode(GPIO.BCM)
               self.GPIO.setup(self.channel, GPIO.IN) 
               self.start_light_level   = self.GPIO.input(self.channel)     
               self.current_light_level = self.GPIO.input(self.channel)       
               
        self.sense  = "light" 
        self.counter = 0 
        self.args["max"] = 20
    def poll(self):
        """
        """ 
           
        if self.os == "LINUX":
            
            light_level = self.GPIO.input(self.channel)    
            print("light", light_level)

            if abs(light_level - self.current_light_level) == 1:       
               self.current_light_level = light_level        
               return [True , "light"]  
            
            self.current_light_level = light_level   

        elif self.os == "OSX":
            
           if self.counter  >= self.args["max"]:
               self.counter = 0
               return [True, "timeout"]

        
        return [False, ""]
     

if __name__ == "__main__":
    """ 
     python3 light.py -r number_2 -m test
    
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
 
    light  = Light(robot, nerves, config, settings )
    if mode == "serve":
        light.serve_forever()

    elif mode =="test":
        light.debug  = True
        light.serve_forever()