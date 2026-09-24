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
import argparse

parser = argparse.ArgumentParser() 

sys.path.append("..")
from  errors import  handle_exceptions
 
    
class Responder(object):
    """
    
    """
    
    def __init__(self,   agent ):
        """ 
        'agent', 'config', 'nerves', 'os', 

        """ 
 
        self.agent         = agent  
        self.wait_length   = 8000 #6000 #4800 #2400 #800
        self.chat_wait_length   = 3000 #4800 #2400 #800
        
        self.polling_rate  = agent.polling_rate
        self.robot         = agent.robot
        self.video         = agent.video
        self.settings      = agent.settings
        self.os            = agent.config.OS
        self.config        = agent.config.CONFIG   
        self.verbose       = agent.config.VERBOSE   
        self.nerves        = agent.nerves
        self.communication = agent.communication  

        self.movement      = self.agent.movement
        self.expressions   = self.agent.expressions 

        self.cannot_understand  = 0
