import random  
import datetime

class Hypoisis(object):

    def __init__(self, action , direction, speed, duration ):

        self.speed    = speed
        self.duration = duration \ 


class Problem


class Solution

class 

class Stratagy(object):

    mappes basic problem with hypythoiss to know steps

    problem-
         issue_identification
         impact
         root_cause
         prob_outome

    formulate_hypotheses
    execute

         

 
    def __init__(self,  available_directions, min_move_time):
        """
        
        """ 
        self.available_directions = available_directions
        self.min_move_time = min_move_time
        
    def random_move(self, current_direction, speed, duration): 
        """
        
        """
        # Filter out current move from valid moves
        valid_moves = [v for v in self.available_directions if v !=  current_direction]
            
        # Pick a movement randomly
        actions = []
 
        direction = random.choice(valid_moves)
        actions.append( (direction, speed, duration )) 

        rnd_pause = random.randint(0, 2) 
        actions.append( ("s",   0, rnd_pause )) 

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
    

    def change_cource(self):
       
       #### Rule  #####
 
       if self.direction_y == 1:
           action1 = self.Action("up", "up" )
           action2 = self.Action("down", "down" )
       else:
           action1 = self.Action("up", "down" )
           action2 = self.Action("down", "up" )
           
       self.direction_x = self.direction_x *-1 
       self.direction_y = self.direction_y *-1
       
       self.actions.append(action1)
       self.actions.append(action2)
        
       if random.randint(0,10) > 5:
           self.direction_x = self.direction_x *-1
           
       if random.randint(0,10) > 7:
           self.direction_y = self.direction_y *-1
           
             
class Reasoning(object):
   
   def __init__(self,  x, y, z):
        """
        
        """   
        
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
        """ 

   
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
            self.actions = [["f" , 1, .1]]

        self.priors[self.actions[0][0]] = datetime.datetime.now()
 
   
   def reasing_old(self):
       
      # print(self.memory["locations"]["energy"])
       near_walls_x = [(x, (x - self.x)) for x in self.memory["locations"]["wall"]["x"]]
       near_walls_y = [(y, (y - self.y)) for y in self.memory["locations"]["wall"]["y"]]
                   
       if len(near_walls_x) > 0:
           near_walls_x =  sorted(near_walls_x, key =lambda x :x[1])
           if abs( near_walls_x[0][1]) > abs( near_walls_x[-1][1]):
               closest_x = near_walls_x[-1][1]
           else:
               closest_x = near_walls_x[0][1]
               
         #  print(self.memory["locations"]["wall"]["prior_x"] , abs(closest_x) ,self.x)
           if self.memory["locations"]["wall"]["prior_x"] > abs(closest_x):
             if abs(closest_x) < 50:
                   self.direction_x = self.direction_x *-1
                   self.change_cource()
           self.memory["locations"]["wall"]["prior_x"] = abs(closest_x)
                       
       if len(near_walls_y) > 0:
           near_walls_y =  sorted(near_walls_y, key =lambda x :x[1])
           
           if abs( near_walls_y[0][1]) > abs( near_walls_y[-1][1]):
               closest_y = near_walls_y[-1][1]
           else:
               closest_y = near_walls_y[0][1]
                
           if self.memory["locations"]["wall"]["prior_y"] > abs(closest_y):
             if abs(closest_y) < 50:
                   self.direction_y = self.direction_y *-1
                   self.change_cource()
           self.memory["locations"]["wall"]["prior_y"] = abs(closest_y)
                   
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