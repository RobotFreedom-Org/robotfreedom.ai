# -*- coding: utf-8 -*-
   
import datetime
import time
import random

try:
   import RPi.GPIO as gpio 
except:
   gpio = None

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode")  
parser.add_argument("-r", "--robot")  
parser.add_argument("-f", "--file"         , default="NA")  
parser.add_argument("-c", "--command_style", default="sequence")  
parser.add_argument("-v", "--verbose"      , default=False)  
 

# List of valid movements for the robot
## not for makerfaire MOVEMENT_DIRECTIONS = ["f", "s", "r", "l","b"]
MOVEMENT_DIRECTIONS = ["f",  "r", "l", "b"]

# Define minium length of time to robot should go in any one direction
MOVE_LENGTH_MIN = 2
 

class LOCOMOTION(object):
    """
    
    """
    
    def __init__(self, nerves,config): 
        """
         
        """  

        self.nerves     = nerves
        self.config     = config
        if self.config.OS != "OSX":
            gpio.setmode(gpio.BCM)
            gpio.setup(23, gpio.OUT)
            gpio.setup(24, gpio.OUT)
            gpio.setup(25, gpio.OUT)
            gpio.setup(16, gpio.OUT) 
 
        "Initiate robot as stopped"
        self.current_direction = "s"
        self.b_forward_ok      = True 

        # Set last time movement changed to now
        self.last_move_time = datetime.datetime.now()

    def reset(self):    
        """
        
        """
        pass
    
    def connect_to_devices(self,  devices):
        return True
 
    def move(self, direction, speed, wait_len):
        """
        Sends commands to the robot using gpio 
        
        """ 
        self.current_direction = direction

        if self.config.OS == "OSX":
            return None
        
        gpio.cleanup() 
        gpio.setmode(gpio.BCM)
        gpio.setup(27, gpio.OUT)
        gpio.setup(22, gpio.OUT)
        gpio.setup(23, gpio.OUT)
        gpio.setup(24, gpio.OUT)
        #if directions is "f"
        if direction == "f":
            # Send command False (off) to port 17.
            gpio.output(27, False) 
            gpio.output(22, True)
            gpio.output(23, True)
            gpio.output(24, False)
    
            # Print direction to screen for debug
            print("\r Forward", end ="")
           # self.nerves.set("stimuli", "move_forward" + ":" +  "focused" ) 
    
        elif direction == "b":
            gpio.output(27, True)
            gpio.output(22, False)
            gpio.output(23, False)
            gpio.output(24, True)
            print("\r Reverse" , end ="")
         #   self.nerves.set("stimuli", "move_backward" + ":" +  "focused" ) 
    
        elif direction == "l": 
            gpio.output(27, True)
            gpio.output(22, False)
            gpio.output(23, True)
            gpio.output(24, False)
            print("\r Left", end ="")
          #  self.nerves.set("stimuli", "move_left" + ":" +  "focused" ) 
    
        elif direction == "r": 
            gpio.output(27, False)
            gpio.output(22, True)
            gpio.output(23, False)
            gpio.output(24, True)
            print("\r Right" , end ="")
            #self.nerves.set("stimuli", "move_right" + ":" +  "focused" ) 
         
        elif direction == "s": 
            gpio.output(27, False)
            gpio.output(22, False)
            gpio.output(23, False)
            gpio.output(24, False)
            print("\r Right" , end ="")
            #self.nerves.set("stimuli", "move_halted" + ":" +  "alert" ) 
         
        # sleep before finishing up commands
        
        time.sleep(wait_len)
        # Release control
        gpio.cleanup()  

           
if __name__ == "__main__":
    """
   
     """
    args =  parser.parse_args() 

    mode    = args.mode 
    robot   = args.robot   
  
    mouse = MOBILITY_GPIO(robot)
    mouse.monitor()
