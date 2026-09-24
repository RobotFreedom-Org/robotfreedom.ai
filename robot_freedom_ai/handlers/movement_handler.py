#!/usr/bin/python
# -*- coding: utf-8 -*- 
""" 
Author: HipMonsters.com  
License: MIT License  
""" 
import time
 
try:
   from . handler import Handler, handle_exceptions
except:
   from   handler import Handler, handle_exceptions


class MovementHandler(Handler): 
    """
    
    """

    @handle_exceptions 
    def write(self, cmd, robot): 
       """
      
       """ 
       #t= open("movement_cmds.log", "a")
       #t.write(str(cmd) + " 0 \n")

       answer = self.agent.movement.write("movement torso " + cmd  + ";", robot) 
  
    @handle_exceptions 
    def send_command(self, cmds, robot="", seq=True): 
       """
      
       """ 
       #t= open("movement_cmds.log", "a")
       #t.write(str(cmds) + " 1 \n")


       verbose = False
       if verbose:
         t = open("movement_handler.log", "a")
         t.write(str(cmds)+ "\n")

       pcmd = cmds 
        
       if seq:
          dcmd  = ""
          _cmds = "" 
          if cmds  == "random":  
              _cmds,   current_states = self.agent.sequences({'part':"random"}, 
                                                              self.agent.current_states) 
              cmds = _cmds[:3]

          elif type(cmds ) == list:
              
              if len(cmds) == 3:
                  dcmd = {"action": cmds[0].strip(),
                          "side":   cmds[1].strip(),
                          "part":   cmds[2].strip()} 
              else:
                  dcmd = {"part":cmds[0].strip()}

              _cmds,   current_states = self.agent.sequences(dcmd,
                                                             self.agent.current_states) 
            
              cmds = _cmds[:2]

          else: 
              cmds = cmds.split(',')  
              if len(cmds) == 1:
                  _cmds,   current_states = self.agent.sequences({'part':"random"}, 
                                                              self.agent.current_states) 
                  cmds = _cmds[:2]
              else: 
                 dcmd = {"action": cmds[0].strip(),
                         "side":   cmds[1].strip(),
                         "part":   cmds[2].strip()} 
                 
                 cmds,  current_states = self.agent.sequences(dcmd, 
                                                              self.agent.current_states)   
                  
          
          for cmd in  cmds:
              cmd = cmd.strip()
              if cmd.startswith('p'): 
                  try:
                     i_len = float(cmd.replace('p','')) 
                  except:
                      i_len = .1 
              else:
                     answer = self.agent.movement.write("movement torso " + cmd + ";", robot)

                     self.agent.current_states[cmd]        = True

                     if cmd in ["hd.tl.1", "hd.tc.1", "hd.tr.1", "hd.pu.1","hd.pd.1","hd.pc.1"]:  
                         if cmd  in ["hd.tl.1",  "hd.tr.1"]:  
                             self.agent.current_states["hd.tc.1"] = False 
                         elif  cmd  in ["hd.pu.1",  "hd.pd.1"]:  
                             self.agent.current_states["hd.pc.1"] = False
                         elif cmd  in ["hd.pc.1"]:   
                             self.agent.current_states["hd.pd.1"] = False
                             self.agent.current_states["hd.pu.1"] = False 
                         else:  
                             self.agent.current_states["hd.tl.1"] = False
                             self.agent.current_states["hd.tr.1"] = False 
                     else:    
                         t_cmd = self.agent.FLIPS[cmd] 
                         self.agent.current_states[t_cmd] = False
                     time.sleep(.01)
          return cmds   
       
       else: 
         #  answer = self.mobility.write(cmd, robot)  
           for cmd in cmds:
               answer = self.agent.movement.write("movement torso " + cmd + ";", robot)


if __name__ == "__main__": 
    """
    
    """
    import os
    os.chdir("../")

    from mobility.sequences           import sequences  , FLIPS

    class AIAgent(object):

        def __init__(self): 

            
            self.polling_rate = 2
            self.robot = "squirrel"
            self.video           = None
            self.settings        = {}
            self.sequences       = sequences
            self.FLIPS           = FLIPS
            class Config():
                def __init__(self):
                    self.OS              = ""
                    self.CONFIG          = {}  
                    self.VERBOSE         = True
            self.config = Config()
            self.nerves          = {}

            class Move():
                def __init__(self):
                    self.OS              = "" 
                def write(self,c,r):
                   print(c) 

            self.movement = Move()
 

    args       = {}
    protocol   = "monitor" 
    robot      = "number_2"   
    networked  = -1  
    directives = {}

    command_style_sequence = True   
    
    
    agent = AIAgent() 
    move = MovementHandler(agent)
    
    
   #res =  move.send_command("random")
   # print(res)
    
    res = move.send_command(["random"])
    print(res)
    
    res = move.send_command(["random", "random", "random"])
    print(res)
