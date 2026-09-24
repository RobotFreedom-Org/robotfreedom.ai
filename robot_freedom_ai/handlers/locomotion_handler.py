#!/usr/bin/python
# -*- coding: utf-8 -*- 
""" 
Author: HipMonsters.com  
License: MIT License  
""" 
import time, datetime
import random
from . handler import Handler, handle_exceptions 

# List of valid movements for the robot
## not for makerfaire MOVEMENT_DIRECTIONS = ["f", "s", "r", "l","b"]
MOVEMENT_DIRECTIONS = ["f", "c", "r", "l", "b"]

# Define minium length of time to robot should go in any one direction
MOVE_LENGTH_MIN = 2


class LocomotionHandler(Handler): 
    """
    
    """
    def __init__(self, agent):
        super().__init__(agent) 
        
        self.current_direction = "s"
        self.b_forward_ok      = True   
        self.last_move_time = datetime.datetime.now()

        
    def random_move(self):
        """
        #if time_since_last_change  > MOVE_LENGTH_MIN: 
        """ 
        # Filter out current move from valid moves
        valid_moves = [v for v in MOVEMENT_DIRECTIONS if v != self.current_direction]
            
        # Pick a movement randomly
        self.current_direction = random.choice(valid_moves)
          
        rnd_pause = random.randint(0, 2)
                
        #Change direction
        self.move(self.current_direction,1, rnd_pause )
            
        # Set last movment time
        self.last_move_time = datetime.datetime.now()

    def detected_wall(self, time_since_last_change):
        """
        """
        global MOVE_LENGTH_MIN
        global MOVEMENT_DIRECTIONS
       
        self.current_direction = 'r' 
        self.move("s", 0 ,1)
        self.nerves.set("stimuli", "move_halted" + ":" +  "alert" )  
        time.sleep(.1)  
               
        self.b_forward_ok = False  
        #Back up
        for pause in [.1, .15, .2]:
            self.move('s', 1 , 1) 
            time.sleep(pause)  
 
        self.current_direction  = "f"
        self.random_move(self.current_direction )

        #Change direction
        #detect, amplitude = self.nerves.pop("distance") 
        #if detect is False:  
        self.b_forward_ok = True

        time.sleep(1)
        self.current_direction  = "f"  
        self.move(self.current_direction , 1, .1 )

    @handle_exceptions 
    def move(self, cmd,speed, wait_len): 
       """
      
       """  
       print("handler", cmd)
       answer = self.agent.locomotion.move(cmd,speed, wait_len) 
       return answer