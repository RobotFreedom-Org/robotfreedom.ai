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
import time  
from .protocol import Protocol
 
 
import argparse
parser = argparse.ArgumentParser() 
parser.add_argument("-r", "--robot"        , default="")    
parser.add_argument("-p", "--protocol"     , default="monitor")   
 

sys.path.append("..")
from  errors import handle_exceptions

class Scripted(Protocol):
    """
    
    """
    
    def __init__(self,  protocol,  agent  ):
        """ 

        """ 
        super().__init__(protocol, agent )
            
           
    @handle_exceptions 
    def initiate(self, directives, ):
        """ 
    
        """ 
        script = directives["script"]
        b_multi_actors = False

        if "multi_actors" in directives:
            b_multi_actors =  directives["multi_actors"]

        with open(script, 'r') as DictReader:

            in_data = csv.DictReader(DictReader, delimiter=',', quotechar='"')
            p_actor = ""
            for row in in_data:
  
                if self.robot  == row["actor"] and b_multi_actors is False: 

                  if row["command"] == "speak": 
                      
                      if b_multi_actors:
                          if row["actor"] != p_actor: 
                             self.nerves.put["speak"] = ";".join( ["switch_voice", "wait_for" , row["actor"]])
                          
                      self.speak(row["value"])
                     
                  elif row["command"] == "sleep":  
                      time.sleep(float(row["value"])) 

                  elif row["command"] == "move": 
                      self.send_command(row["value"] ,row["actor"])  
                      
                  elif row["command"] == "communicate": 
                       self.communication.send(row["value"]  ,row["param1"] )

                  elif row["command"] == "wait_for_signal":   
                       signal_val =  self.wait_for_signal[row["value"]] 
                       self.remember(row["value"], signal_val)

                  elif row["command"] == "wait_for_event":
                       
                       while True:
                          detect, val = self.nerves.pop(row["value"]) 
                          if detect:
                              break 

                          time.sleep(self.polling_rate)


                  elif row["command"] == "wait_for_a_message": 
                    
                      recipient      = "WORLD" 
                      expected_reply = "DONE"
                      sent_from      = row["value"]
                     
                      while True:
                          detect, val = self.communication.wait_for_a_message( recipient,  expected_reply , sent_from) 
                          if detect:
                              break  
     
if __name__ == "__main__":

    """ 

    """
    args =  parser.parse_args()  
    protocol    = args.protocol    
    robot       = args.robot    
