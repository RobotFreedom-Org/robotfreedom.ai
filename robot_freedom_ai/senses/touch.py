# -*- coding: utf-8 -*-
"""
Description: Sensor daemon for touch.
Author: HipMonsters.com 
License: MIT License
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
 
class  Touch(SenseBase):
    """
    
    """

    def __init__(self,robot, nerves, config, settings, pins ={"pin_1":40}):
        """
        
        """
      
        super().__init__(robot, nerves, config, settings, "touch")
             
        self.pins = pins
        if self.os == "LINUX":
               
            import RPi.GPIO as GPIO 
            GPIO.setwarnings(False) 
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.pins["pin_1"], GPIO.IN) 
            self.GPIO = GPIO 
             
        self.sense = "touch"   
             
     
if __name__ == "__main__":
    """ 
     python3  touch.py -r number_2 -m test
    
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
 
    touch  = Touch(robot, nerves, config, settings )
    if mode == "serve":
        touch.serve_forever()

    elif mode =="test":
        touch.debug  = True
        touch.serve_forever()
