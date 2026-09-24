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
import sys   
import datetime  
import time  
from .protocol import Protocol
 
 
import argparse
parser = argparse.ArgumentParser() 
parser.add_argument("-r", "--robot"        , default="")    
parser.add_argument("-p", "--protocol"     , default="monitor")   
  

sys.path.append("..")
from  errors import handle_exceptions
    
class Monitor(Protocol):
    """
    
    """
    
    def __init__(self,  protocol,   agent  ):
        """ 

        """ 
        super().__init__(protocol, agent ) 
           
    @handle_exceptions  
    def initiate(self, directives):
        """ 
        monitor
        """ 
        self.last_time_user_spoke = datetime.datetime.now()
        i_quiet = 0
 

        while self.agent.protocol_continue:    

            self.epoch             += 1
            self.current_cycle     = datetime.datetime.now()
            time_since_last_change = (datetime.datetime.now() - self.LAST_MOVE_TIME).total_seconds()
            last_cmd               = (datetime.datetime.now() - self.LAST_COMMAND).total_seconds()  
            
            if self.speaking:
                speaking = self.nerves.get("communication_complete")  
                if speaking == "": 
                    self.speaking    =  False
                    self.last_spoke  =  datetime.datetime.now()  
             
            self.check_remote_commands(i_quiet)  
            if self.locomotion_directives(time_since_last_change): 
                 print("moved")

            if last_cmd > 30:
                self.receiving_commands  = False   

            if self.receiving_commands:   
               monitor_sense = ["distance", "motion", "speech", "touch"]  

            elif self.epoch  % 15 == 0: 
                monitor_sense = [  "speech"]  

            elif self.chat: 
               monitor_sense = list( self.behavior.cognitive_control.sense_types["physical"].keys())
              
            else: 
               monitor_sense = list( self.behavior.cognitive_control.sense_types["physical"].keys())  
 
            for sense in  monitor_sense:
            
                self.check_remote_commands(i_quiet)   
                if self.locomotion_directives(time_since_last_change): 
                    print("moved")

                if sense == "quiet": 
                    dur = self.current_cycle - self.last_stimuli 
                    if dur.total_seconds() > self.quiet_in_secs :
                        detect,  amplitude = True, .10* dur.total_seconds()  
                        i_quiet += 1
                    else:
                        detect, amplitude = False, "nothing" 
                else:
                    detect, amplitude = self.nerves.pop(sense)  
  
                slog =  sense.ljust(25, ' ') + " " + str(detect) + self._space   
               # print("\r" + slog,  end="") 

                if detect:  
                    if sense != "quiet":
                         i_quiet = 0  
                         
                    result  = self._detected(sense, i_quiet, amplitude) 

                    if i_quiet >= self.self_reflection_threshold:
                           i_quiet = 0
                

            time.sleep(self.polling_rate) 
 
if __name__ == "__main__":

    """ 

    """
    args =  parser.parse_args()  
    protocol    = args.protocol    
    robot       = args.robot    
