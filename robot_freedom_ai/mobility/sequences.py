# -*- coding: utf-8 -*-
  
"""
Description: this dictionary defines sequence of movements for a robot for a provided term.
Author: HipMonsters.com 
License: MIT License
""" 
import random  
 

MAPS = {}   
SEQ = {} 

SEQ["head"] = {}
SEQ["head"]["turn"] = {} 
SEQ["head"]["turn"]["left"]   =  ['hd.tl.1'] 
SEQ["head"]["turn"]["right"]  =  ['hd.tr.1']
SEQ["head"]["turn"]["center"] =  ['hd.tc.1'] 
"""  
SEQ["head"]["pivot"] = {} 
SEQ["head"]["pivot"]["up"]     =  ['hd.pu.1'] 
SEQ["head"]["pivot"]["down"]   =  ['hd.pd.1']
SEQ["head"]["pivot"]["center"] =  ['hd.pc.1']  
"""
"""  
SEQ["wrist"] = {}
SEQ["wrist"]["pivot_in"] = {} 
SEQ["wrist"]["pivot_in"]["left"]   =  ['wr.i.l'] 
SEQ["wrist"]["pivot_in"]["right"]  =  ['wr.i.r'] 

SEQ["wrist"]["pivot_out"] = {} 
SEQ["wrist"]["pivot_out"]["left"]   =  ['wr.o.l'] 
SEQ["wrist"]["pivot_out"]["right"]  =  ['wr.o.r'] 
"""
 
SEQ["finger_1"]  = {} 
SEQ["finger_1"]["open"] = {} 
SEQ["finger_1"]["open"]["left"]  =  ['f1.o.l'] 
SEQ["finger_1"]["open"]["right"] =  ['f1.o.r'] 
 
SEQ["finger_1"]["close"] = {}  
SEQ["finger_1"]["close"]["left"]   = ['f1.c.l']  
SEQ["finger_1"]["close"]["right"]  = ['f1.c.r']  


SEQ["finger_2"]  = {} 
SEQ["finger_2"]["open"] = {} 
SEQ["finger_2"]["open"]["left"]  =  ['f2.o.l'] 
SEQ["finger_2"]["open"]["right"] =  ['f2.o.r'] 
 
SEQ["finger_2"]["close"] = {}  
SEQ["finger_2"]["close"]["left"]   = ['f2.c.l']  
SEQ["finger_2"]["close"]["right"]  = ['f2.c.r']  

SEQ["thumb"]  = {} 
SEQ["thumb"]["open"] = {} 
SEQ["thumb"]["open"]["left"]  =  ['tm.o.l'] 
SEQ["thumb"]["open"]["right"] =  ['tm.o.r'] 
 
SEQ["thumb"]["close"] = {}  
SEQ["thumb"]["close"]["left"]   = ['tm.c.l']  
SEQ["thumb"]["close"]["right"]  = ['tm.c.r']  
                 

SEQ["bicept"]  = {}
SEQ["bicept"]["raise"] = {}  
SEQ["bicept"]["raise"]["left"]   = ['bc.r.l']  
SEQ["bicept"]["raise"]["right"]  = ['bc.r.r']  
     
SEQ["bicept"]["lower"] = {}  
SEQ["bicept"]["lower"]["left"]   = ['bc.l.l']  
SEQ["bicept"]["lower"]["right"]  = ['bc.l.r']   

SEQ["arm"]  = {}
SEQ["arm"]["raise"] = {}  
SEQ["arm"]["raise"]["left"]   = ['am.r.l']  
SEQ["arm"]["raise"]["right"]  = ['am.r.r']  
     
SEQ["arm"]["lower"] = {}  
SEQ["arm"]["lower"]["left"]   = ['am.l.l']  
SEQ["arm"]["lower"]["right"]  = ['am.l.r']  

SHORT_CUTS ={}
SHORT_CUTS["a"] = ""

SEQS_MAP = {}
SEQS_MAP["arm"] = {}
SEQS_MAP["arm"]["wave"] = {}  
SEQS_MAP["arm"]["wave"]["left"]   = ['a', 's' , 'p1', 'q', 'w']  
SEQS_MAP["arm"]["wave"]["right"]  = ['g', 'h', 'p1' , 't', 'y'] 
SEQS_MAP["arm"]["wave"]["both"]   = ['a', 's', 'g', 'h', 'p1', 't', 'y', 'q', 'w']  
 

RESETS = ["hd.tc.1" ]
FLIPS  = {"hd.tc.1":"hd.tr.1", 
          "hd.tr.1":"hd.tl.1", 
          "hd.tl.1":"hd.tc.1" }
CMDS   = {}


for part , moves in SEQ.items(): 

    i = 0
    p_cmd_r = None
    p_cmd_l = None
    for motion, sides in moves.items():
         for side,  cmd in sides.items():
            cmd = cmd[0]
            if i == 0:
                if part != "head":
                    RESETS.append(cmd)
                if side  =="right":
                    p_cmd_r = cmd
                else:
                    p_cmd_l = cmd
            else:
                if part != "head":
                    if side  =="right":
                        FLIPS[cmd]   = p_cmd_r
                        FLIPS[p_cmd_r] = cmd 
                    else:
                        FLIPS[cmd]   = p_cmd_l
                        FLIPS[p_cmd_l] = cmd  
            CMDS[cmd] = {"side":side, "part": part, "move" : motion}
         i +=1
    
 
  

def rand_cmds(current_cmds=[]):
   """
   
   """
   actions = []
   potential = [k for k in CMDS.keys() if k  in current_cmds]
   i_len = len(potential) - 1
   for i in range(0, random.randint(2, 6)):
       i_a = random.randint(0, i_len)
       a = potential[i_a]
       actions.append(a)
       actions.append("p.1")

   return actions

def rand_sequence(current_states={}):
   """
   
   """ 

   #parts = [k for k in SEQ.keys() if k not in "head"] 
   #i_len = len(parts) - 1
   cmds = []
   i_moveit = 0 
   rd_states = list(current_states.items())  
   random.shuffle(rd_states)    
   cut_off = random.randint(2, 5)
   for key,  val in rd_states: 
       if val: 
           i_moveit +=1  
           if key in ["hd.tl.1", "hd.tc.1", "hd.tr.1", "hd.pu.1","hd.pd.1","hd.pc.1"]:  
               if key  in ["hd.tl.1",  "hd.tr.1"]: 
                   cmds.append("hd.tc.1")   
               elif  key  in ["hd.pu.1",  "hd.pd.1"]: 
                   cmds.append("hd.pc.1")   
               elif key  in ["hd.pc.1"]:  
                   t = random.choice(["hd.pu.1",  "hd.pd.1"])
                   cmds.append(t)  
               else: 
                   t = random.choice(["hd.tl.1",  "hd.tr.1"])
                   cmds.append(t)  
           else:    
               cmds.append(FLIPS[key]) 

           if i_moveit > cut_off: 
                break   
   return cmds 

    

def flip_sequence(base="a"):
   """
   
   """
   actions = []
   potential = list(CMDS.keys())
   i_len = len(potential) - 1
   for i in range(0, random.randint(2, 6)):
       i_a = random.randint(0, i_len)
       a = potential[i_a]
       actions.append(a)
       actions.append("p.1")

   return actions

def sequences(sequence, current_states):
     """
     
     
     """
     if sequence['part'] == "random":
         
         cmds = rand_sequence(current_states )   
         return  cmds, current_states
     
     elif sequence['part'] == "light":
        if sequence['action'] == "color":
            if sequence['side'] == "red":
                 return ['l1'] , {}
            elif sequence['side'] == "green":
                 return ['l2'] , {}
            elif sequence['side'] == "blue":
                 return ['l3']  , {}
            elif sequence['side'] == "yellow":
                 return ['l4'] , {}
             
     #TODO system command like rest
     else:
         try:
             cmds = SEQ[sequence['part']][sequence['action'] ][sequence['side']]  

         except:
             print('Sequence missing', sequences) 
             t = open( './seq.error.log', 'a')
             t.write(str(sequence) + "\n")
             cmds  = rand_sequence(current_states)    
         
         return  cmds, current_states
     
     return [],  current_states