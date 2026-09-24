


import random  
import datetime
  

class Stratagy(object):
 
    def __init__(self,  available_directions, min_move_time):
        """
        
        """ 
        self.available_directions = available_directions
        self.min_move_time = min_move_time
        
    def random_move(self, current_direction, speed, duration): 
        """
        
        """
        # Filter out current move from valid moves
        
        #valid_moves = [v for v in self.available_directions if v !=  current_direction]

        valid_moves = [v for v in ["l", "r"] if v !=  current_direction]
            
        # Pick a movement randomly
        actions = [] 
        direction = random.choice(valid_moves) 
        actions.append( (direction, speed, duration )) 

        rnd_pause = random.randint(0, 2) 
        actions.append( ("f",  speed, rnd_pause ))  

        actions.append( ("s",   0, rnd_pause )) 
        
        rnd_pause = random.randint(0, 2)  
        actions.append( ("c",  speed, rnd_pause ))  

        rnd_pause = random.randint(0, 2)  
        actions.append( ("f",  speed, rnd_pause ))  

        return actions

    def avoid_obstacle(self, current_direction,  time_since_last_change, duration):
        """
        """  
        actions = []
        actions.append(["s", .5, .1])    
        actions.append(["b", .5, 1.5])   
        actions.append(["b", .5, 1.5])   

        ##.25 is % degrees
        for action in self.random_move(current_direction, .5, .25): 
            actions.append(action) 

        return actions
    
  
             
class WayFinder(object):
   
   def __init__(self,  x, y, z):
        """
        
        """  
        self.speed = 1 
        self.x = x
        self.y = y
        self.z = z

        self.prior_z = z  
        self.prior_x = x  
        self.prior_y = y  
        self.direction_x = 1
        self.direction_y = 1
        self.direction_z = 1
        self.obstruction = False
        
        self.map = {}
        self.actions  =  []
        self.events   =  []
        self.motive   =  {}
        self.memory   =  {}
        self.memory["locations"]  = {}
        self.memory["locations"]["wall"] = {}
        self.memory["locations"]["wall"]["x"] = set([])
        self.memory["locations"]["wall"]["y"] = set([])
        self.memory["locations"]["wall"]["z"] = set([])
        self.memory["locations"]["wall"]["prior_y"] = 10
        self.memory["locations"]["wall"]["prior_x"] = 10
        self.memory["locations"]["wall"]["prior_z"] = 10
                
        self.memory["locations"]["energy"] = {}
        self.memory["locations"]["energy"]["x"] = set([])
        self.memory["locations"]["energy"]["y"] = set([])
        self.memory["locations"]["energy"]["z"] = set([])
        self.memory["locations"]["energy"]["prior_y"] = 10
        self.memory["locations"]["energy"]["prior_x"] = 10
        self.memory["locations"]["energy"]["prior_z"] = 10

        self.max_move_length     = 2.5 #5 #10 ##20 
        self.valid_directions    = ["f", "s", "r", "l", "b", "c"]
        self.priors              = {"f":0, "r":0, "l":0, "b":0, "s":0, "c":0}
        self.actions             = []
        self.stratagy            = Stratagy(self.valid_directions,
                                            self.max_move_length)
 
   def calc_x_y_z(self, duration, vect_x, vect_y,  vect_z, speed):
       """

       """  
       if self.prior_x:
          x = self.prior_x - vect_x*duration*speed
       else:
          x =   vect_x*duration*speed
           
       if self.prior_y:
          y = self.prior_y - vect_y*duration*speed 
       else:
          y =   vect_y*duration*speed  

       if self.prior_z:
          z = self.prior_z - vect_z*duration*speed 
       else:
          z =   vect_z*duration*speed 

       self.prior_z = z  
       self.prior_x = x  
       self.prior_y = y  
       distance = duration*speed
       self.actions     = []
       return x,y,z, distance
   
   def map(self):
       return  self.memory["locations"]
   
   def reasoning(self, current_direction, time_since_last_change, goals=[]):
        """
        goals = [("type": "destimation", "y":1223, "x": 123, "d": 123}]
        
        """ 

  
        #if self.priors[current_direction] != 0:   
        #      last_changed =  (datetime.datetime.now() - self.priors[current_direction] ).total_seconds()
       # else:
        last_changed = time_since_last_change 
 
        if self.obstruction:
            self.actions =   self.stratagy.avoid_obstacle(current_direction, 
                                                          time_since_last_change,
                                                          1)
            self.obstruction = False

        elif last_changed  > self.max_move_length : 
          
            self.actions =   self.stratagy.random_move(current_direction, 
                                                       time_since_last_change,
                                                         1) 
        else:
            self.actions = [["c" , 1, .1], ["f" , 1, .1]]

        self.priors[self.actions[0][0]] = datetime.datetime.now()
 
    
                   
   def sense(self, event): 
       """
       """ 
       self.events.append(event )
       self.memory["locations"][event[0]]["x"].add(event[1])
       self.memory["locations"][event[0]]["y"].add(event[2])
       self.obstruction = True  
            
   def pop(self): 
           
       res = []
       for action  in self.actions:
          res.append(action) 
       self.actions = []
       return  res