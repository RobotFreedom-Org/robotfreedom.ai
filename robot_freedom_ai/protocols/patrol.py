# -*- coding: utf-8 -*-
"""
Description: The agent daemon that allows the Artificial Intelligence to process sensors signals and control the robot.
Author: HipMonsters.com
Date Created: Jan 1, 2023
Date Modified: Oct 10, 2024
Version: 4.0
Platform: RaspberryPi
License: MIT License 
"""
import json
import sys  
import csv
import datetime  
import random
import time  
from .protocol import Protocol
 
 
import argparse
parser = argparse.ArgumentParser() 
parser.add_argument("-r", "--robot"        , default="")    
parser.add_argument("-p", "--protocol"     , default="monitor")   

sys.path.append("..")
from  errors import handle_exceptions


# List of valid movements for the robot
MOVEMENT_DIRECTIONS = ["f", "s", "r", "l","b"]
#MOVEMENT_DIRECTIONS = ["f",  "r", "l"] 
# Define minium length of time to robot should go in any one direction
MOVE_LENGTH_MIN = 2  
# Intial direction
CURRENT_DIRECTION = "f" 
# Set last time movement changed to now
LAST_MOVE_TIME = datetime.datetime.now()

    
class Patrol(Protocol):
    """
    
    """
    
    def __init__(self, protocol,   agent  ):
        """ 

        """ 
        super().__init__("patrol", agent )
        self.LAST_MOVE_TIME = datetime.datetime.now()
        self.current_direction = "f"
             
    def signal(self ):
        """
        Sends signals on direction and mood.
        
        """ 
        direction = self.current_direction  
        #if directions is "f"
        if direction == "f": 
            self.nerves.set("stimuli", "balance" + ":" +  "happy" ) 
    
        elif direction == "b": 
            self.nerves.set("stimuli", "temperature" + ":" +  "happy" ) 
    
        elif direction == "l":  
            self.nerves.set("stimuli", "noise" + ":" +  "happy" ) 
    
        elif direction == "r":  
            self.nerves.set("stimuli", "speech" + ":" +  "happy" ) 
         
        elif direction == "s":  
            self.nerves.set("stimuli", "quiet" + ":" +  "happy" ) 

           
    @handle_exceptions     
    def initiate(self, directives):
        """ 

        """   
        global MOVE_LENGTH_MIN
        global MOVEMENT_DIRECTIONS
        # Loop forever 
        while True:
           
         for sense in  ["distance", "distance-rear", 
                        "distance-left", "distance-right", 
                        "object"]:
           
           #goes foward unless see something ahead, turns in a direct with nothing in range

           detect, amplitude = self.nerves.pop(sense)  
           # Find the time in seconds since the last movement change
           time_since_last_change = (datetime.datetime.now() - self.LAST_MOVE_TIME).total_seconds()
     
           if detect:   
              self.memory[sense] = datetime.datetime.now()
 
           b_forward_ok = True  

           if detect and sense  == "distance" :   
                
                self.mobility.detected_wall(time_since_last_change)
          
                self.signal()

           elif time_since_last_change  > MOVE_LENGTH_MIN : 
                self.mobility.random_move()   
                self.signal()

           else:
                self.mobility.move(self.current_direction , 1 ) 

           time.sleep(.01)

         
if __name__ == "__main__":

    """ 

    """
    args =  parser.parse_args()  
    protocol    = args.protocol    
    robot       = args.robot    
