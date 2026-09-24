#!/usr/bin/python
# -*- coding: utf-8 -*- 
""" 
Author: HipMonsters.com  
License: MIT License  
""" 
import time
from . handler import Handler, handle_exceptions


class ExpressionsHandler(Handler): 
    """
    
    """

    @handle_exceptions 
    def send_command(self, cmd, robot): 
       """
      
       """ 
       answer = self.mobility.write("expression light " + cmd + ";", robot)  