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

from datetime import timedelta

 
import argparse
parser = argparse.ArgumentParser() 
parser.add_argument("-r", "--robot"        , default="")    
parser.add_argument("-p", "--protocol"     , default="monitor")   

sys.path.append("..")
from  errors import handle_exceptions
  
    
class Patrol(Protocol):
    """
    
    """
    
    def __init__(self, protocol,   agent  ):
        """ 

        """ 
        super().__init__("patrol", agent )
        self.LAST_MOVE_TIME         = datetime.datetime.now()
        self.time_since_last_change = 0
        self.current_direction      = "f"  
        self.speed                  = 1
        self.mobile                 = True
             
    def signal(self ):
        """
        Sends signals on direction and mood.
        
        """ 
        direction = self.current_direction  
        self.nerves.set("locomotion", direction ) 
        

           
    @handle_exceptions     
    def initiate(self, directives):
        """ 

        """    
        # Loop till receive stop command 
        while self.agent.protocol_continue: 

         """   
         for sense in  ["distance"             , "distance-rear", 
                        "proximity-foward-left", "proximity-foward-right",
                        "proximity-rear-left"  , "proximity-rear-right",
                        "proximity-left"       , "proximity-right",
                        "balance"              , "movement"]:
         """  
         
         i_quiet = 0
         for sense in  ["distance" , "balance", "movement"]:
           
           #goes foward unless see something ahead, turns in a direct with nothing in range

           time_since_last_change = (datetime.datetime.now() - self.LAST_MOVE_TIME).total_seconds()

           self.check_remote_commands(i_quiet)  
           if self.locomotion_directives(time_since_last_change):  
               pass
           
           detect, amplitude = self.nerves.pop(sense)  
           # Find the time in seconds since the last movement change 
     
           if detect:        
              
              last_cmd_any           = (datetime.datetime.now() - self.last_remote_cd).total_seconds()  
              user_detected = 0
              if last_cmd_any > 120:
                   user_detected  = 1
                   
              self.last_moved       = (datetime.datetime.now() - self.last_movement).total_seconds() 
              self.last_talked      = (datetime.datetime.now() - self.last_spoke).total_seconds() 
              self.behavior.stimuli("sense", sense, amplitude,  1, 
                               self.prior_response ,
                               user_detected,
                               self.epoch, 
                               datetime.datetime.now(), 
                               self.last_moved,  
                               self.last_talked, 
                               time_since_last_change,
                               self.chat,
                               self.mobile,
                               time_since_last_change,
                               self.current_direction  )  
 
                 
              ### Chat   ############################################ 
              if sense == "speech" and  self.chat is False: 
                  prompts = [k for k in amplitude.lower().split(' ') if k in self.prompts]  
                  if len(prompts) > 0:
                      self.chat = True  
    
              if self.chat:  
                  if type(amplitude) is float:
                      responses = {"speech":[], "movement": ["random"]} 
    
                  elif amplitude.strip() == "":
                      responses = {"speech":[], "movement": ["random"]}
    
                  elif sense == "speech":  
                      ##print("Heard   :", amplitude) 
                      responses = self.interactions.responses("sense", 
                                                       sense, 
                                                       amplitude,  
                                                       self.behavior,
                                                       self.chat,
                                                       self.get_chat_response) 
                      ##print("Said   :", responses)
                  else:
                      responses = {"speech":[], "movement": ["random"]}
              else:
                    responses = self.interactions.responses("sense", 
                                                         sense, 
                                                         amplitude,  
                                                         self.behavior,
                                                         self.chat,
                                                         self.get_chat_response)  
                 
              #### End Chat   ############################################
   
              self.log_sense(sense, amplitude,responses, self.current_direction) 
              
              #### Speak   ############################################
              response = "" 
              for response in responses["speech"]:  
                  if response != "":
                      
                     time_since_last_spoke = (datetime.datetime.now() - self.last_spoke).total_seconds()
                     if time_since_last_spoke > 30: 
                         self.nerves.set("speach_start", str(datetime.datetime.now()) )  
                         self.nerves.set("ongoing_conversation", "True" )  
                         self.nerves.set("ignore_speech", "true")  

                         self.speak(response)   
                         self.prior_response  =  responses  
                         #_b,_v = self.nerves.pop("ongoing_conversation") 
                          
           else:
               pass
           
           responses = {"speech":[], "movement": ["random"]}

           if detect and  sense in ["distance"]:
                x,y,z,dist = self.behavior.wayfinder.calc_x_y_z(time_since_last_change, 1, 1, 0, 1)
                self.behavior.wayfinder.sense(["wall", x, y, z])
           else:
                 x,y,z,dist = self.behavior.wayfinder.calc_x_y_z(time_since_last_change, 1, 1, 0, 1)
                 
           self.behavior.wayfinder.reasoning("f", time_since_last_change, []) 
           
           #### locotion   ############################################ 
           if len(self.locomotion_cmds) == 0:
               locomotion              = self.behavior.wayfinder.pop()   
           else:
               locomotion              = self.locomotion_cmds
                
           responses["locomotion"] = locomotion  

           if locomotion[0][0] in ["f"]: 
               pulse_modulation = 2
           else:
               pulse_modulation = 4
               self.LAST_MOVE_TIME =  datetime.datetime.now()  

           if self.agent.safty_overide == False:     
               self.locomotion_request(locomotion[0],x,y, z, time_since_last_change)

               """ 
               for action in locomotion:   
                   for i in range(pulse_modulation): 
                        self.current_direction, self.speed, self.duration = action[0], action[1]  ,action[2] 
                        res = self.agent.handlers["LocomotionHandler"].move(self.current_direction , self.speed, self.duration )  
                
                        if res.strip() == "BLOCKED":  
                            self.obstacle_avoidance(res , x,y,z, time_since_last_change) 
                        else:
                            self.current_direction = action[0]  
                """
           time.sleep(.1)  


         
if __name__ == "__main__":

    """ 

    """
    args =  parser.parse_args()  
    protocol    = args.protocol    
    robot       = args.robot    
