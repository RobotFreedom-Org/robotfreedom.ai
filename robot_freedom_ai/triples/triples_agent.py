#!/usr/bin/python
# -*- coding: utf-8 -*- 
""" 
Author: RobotFreedom.org  
License: MIT License  
"""   
import time  
import csv    
import psutil 
import json   

from .utils.utils import dispatcher   



def worker_s(name):
    """Function to be executed in a separate thread."""
    print(f"[{time.strftime('%H:%M:%S')}] Thread {name} started.")
    # Simulate some work
    for i in range(3):
        print(f"[{time.strftime('%H:%M:%S')}] Thread {name} working... ({i+1}/3)")
        time.sleep(1)
    print(f"[{time.strftime('%H:%M:%S')}] Thread {name} finished.")

def list_specific_processes(prefixes):
   """List processes starting with specific prefixes."""
   matching_processes = []
   for process in psutil.process_iter(['pid', 'name', 'cmdline']):
       try:
           # Check if process name starts with any of the given prefixes 
           if process.info['cmdline'] is not None:
            if len(process.info['cmdline'] ) > 1:
               cmds = ' '.join(process.info['cmdline'][1:] )
               if any(cmds.find(prefix) > -1 for prefix in prefixes):
                   matching_processes.append({
                   'pid': process.info['pid'],
                   'name': process.info['name'],
                   'cmdline': cmds
                   })
       except (psutil.NoSuchProcess, psutil.AccessDenied):
           continue
       
   return matching_processes
    
class AgentTriples(object):
 
    def __init__(self:object, networked:int =-1 ):
        """
        Functions related to a agent (robot)
        """  
        self.networked = networked
        if networked == 0:
            self.comm  = self._nerves 
        elif networked == 1:
            self.comm  = self.communication 

    def __send_cmd(self:object, key:str, param:str):
        """
        internal command for communicating with networked agent
        """ 

        if self.networked == 0: 
             self.memory["variables"].set(key, param)
        else: 
            if param.find("@") > 1:
                param , agent  = param.split('@', 1)
                param = param.strip()
            
                if param.find('"') > -1:
                    param += '"' 
             
                agent  = agent.replace('"', '')
            else:
                agent = self.agent 

            self.comm.send(agent,  key + ":" +  param )  

    def __get_messages(self:object, message:str, i_timeout:int = 10000):
        """ 
        internal command for communicating with networked agent
        """
        i_tot = 0 
        while True:
              b_message, s_message   = self.communication.check_messages( ) 
              if b_message: 
                 return  b_message, s_message
              
              if i_tot >=  i_timeout :
                  return False, ""
              i_tot += 1
            
              time.sleep(.1)

    def __wait_for(self:object, message:str, i_timeout:int = 100000):
        """ 
        internal command for communicating with networked agent
        """
        i_tot = 0 
        while True:
              b_message, s_message   = self.communication.check_messages_for(message ) 
              if b_message: 
                 return  b_message, s_message
              
              if i_tot >=  i_timeout :
                  return False, ""
              i_tot += 1
            
              time.sleep(.1)  

    def _end_plan(self:object, in_subjects :str = "", in_objects: str =""):
        """
        terminates a plan block
        """  
        s_if      =   self.active_blocks.pop()
        self.s_if = None
         
        if len(self.active_blocks) == 0:
             res = [] 
             for ipos, cmd in  enumerate(self.blocks[s_if[0]]["code"]): 
                    _res =   cmd[0]( cmd[1][0], cmd[1][1], cmd[1][2])   
                    res.append(_res)

             if len(res) == 0:
                 return None
             else:
                 return res 
        else:
             return None 

        
    def plan(self:object, in_subjects :str = "", in_objects: str ="start"):
        """ 
        defines a plan
        plan actions start

         move forward 10
         more left 10

        plan actions end 
        """ 
        if in_subjects == "actions":
             
            if in_objects == "start":

                parent , parent_type = None, None
                if len(self.active_blocks) > 0:
                    parent , parent_type  = self.active_blocks[-1]
                self.s_if = len(self.blocks)
                self.blocks[self.s_if] = {} 
                self.blocks[self.s_if]["parent"]      = parent
                self.blocks[self.s_if]["parent_type"] = parent_type
                self.blocks[self.s_if]["code"]        = [] 
                self.active_blocks.append([self.s_if, "if"])

            elif in_objects == "end": 
                return self._end_plan(in_subjects, in_objects)
 
    @dispatcher
    def settings(self:object, in_subjects :str = "", in_objects: str =""):
            """
            send updates to agent's setting
            setting chat rules;
            setting mood rude;
            """

            if in_subjects == "chat":
                 val = {"type":in_objects}
                 self._nerves.set("directive:ai_settings", json.dumps(val) )  
                 return "engine reset"  + str(val) 
                  
            elif in_subjects == "mood":       
                 val = {"setting":in_objects}
                 self._nerves.set("directive:ai_settings", json.dumps(val) )  
                 return "engine reset " + str(val) 
            
            return ""
 
    @dispatcher
    def asssign(self:object, in_subjects :str = "", in_objects: str =""):
        """
        sets default agent
        """ 
        self.agent = in_subjects   
         
   
    @dispatcher     
    def  status(self: object, in_subjects :str = "", in_objects: str ="" )-> str: 
          """ looks for running prcesses"""
          prefixes = ['launcher.py', 'agent.py', "daemon.py"]
          processes = list_specific_processes(prefixes)
          resp = "..." 
          for proc in processes: 
               s_name = proc['cmdline'].split("/")[-1]
               resp += str(proc['pid']) + " " + s_name + "\n"
               #resp +=  f"PID: {proc['pid']}, Name: {proc['name']}, Cmdline: {proc['cmdline']}" + " " 
          return resp
    
    @dispatcher  
    def chat(self: object, in_subjects :str = "", in_objects: str ="" )-> str:
        """" chat with a nextwork agent/robot """

        if in_objects.find("@") != -1:
            in_subjects = in_subjects + "@" + in_objects
        
        self.__send_cmd("remote_cmd",  "chat:" + in_subjects)  

        i   = 0
        val = "error"

        while True:
            done, val  = self._nerves.pop("chat_responses_2") 
            if i == 100 or done:
                break
            time.sleep(.2)
            i += 1

        return val  
    
    @dispatcher 
    def diagnostics(self: object, in_subjects :str = "", in_objects: str ="" )-> str: 
        """
            arp -a
            
        """
        if in_subjects == "full" or in_subjects =="":
            val = {"type":"full" }
            self._nerves.set("cmd:diagnostics", json.dumps(val) )  
            mess = ""
            for i in range(20):
                b, v = self._nerves.pop("response:diagnostics")
                if b:
                    rpt = json.loads(v)
                    for k, v in rpt.items():
                        mess += k + " " + v + "\n"
                    break
                time.sleep(.5)  



            return "Response :"  + str(mess) 
    
    @dispatcher 
    def safty(self: object, in_subjects :str = "", in_objects: str ="" )-> str: 
         """  
        Toggles agent/robot's safty override
         """ 
         self._nerves.set("cmd:safty", "1")

    @dispatcher 
    def nerves(self: object, in_subjects :str = "", in_objects: str ="" )-> str:
        """ 
        Functions to interacting with nerves
        """

        if in_subjects  == "" or in_subjects  == "list": 
            sigs =""
            for sig in  self._nerves.known_keys: 
               v = self._nerves.get(sig) 
               sigs += sig + " " + str(v)   + "\n"
            return sigs
        
        elif in_subjects == "stats":
            sigs =  self._nerves.all_signals( )   
            sigs = [str(sig).strip() for sig in sigs]
            return "\n".join(sigs)
        
        elif in_subjects == "get":
             return self._nerves.get(in_objects)
        
        elif in_subjects == "set":
             key, val = in_objects.split("<-")
             return self._nerves.set(key, val)

        elif in_subjects == "retrieve":
            val = {"request":"retrieve", "query":in_objects }
            self._nerves.set("directive:memory", json.dumps(val) )  
            v = "busy..."
            for i in range(20):
                b, v = self._nerves.pop("directive:memory")
                time.sleep(.5)   

            return "Restrived :"  + str(v) 
         
        elif in_subjects == "store":

            val = {"request":"store", "query":in_objects }
            self._nerves.set("directive:memory", json.dumps(val) )   
            res= self._nerves.get("directive:memory" )    

            return "Stored :"  + str(in_objects)  

        return ""
    
    @dispatcher
    def move(self: object, in_subjects :str = "", in_objects: str ="" )-> str: 
        """" sends a request to move """
        self.__send_cmd("remote_cmd",   "move:" + in_subjects)  
        return ""
                      
    @dispatcher
    def dialogue(self: object, in_subjects :str = "", in_objects: str ="" )-> str:
        """ Runs a dialogue""" 
        self.__wait_for("spoke", 10)
        b_random_movements = False
        with open(in_subjects, 'r') as DictReader: 
            
            in_data = csv.DictReader(DictReader, 
                                     delimiter=',', 
                                     quotechar =  '"',
                                     skipinitialspace=True,
                                     quoting=csv.QUOTE_ALL,
                                     doublequote = True)
          
            p_actor = ""
           
            for row in in_data: 
                actor = row["actor"]  
                row["command"] = row["command"].strip()

                if row["command"] == "set": 
                     
                    if  row["value"]  == "rnd_movements":
                        b_random_movements  = True 

                    elif  row["value"]  == "videos":
                       self.__send_cmd("remote_cmd" , "video_mode" + "@" + "ANYONE" )   

                elif row["command"] == "speak": 
               
                    if b_random_movements:
                       self.__send_cmd("remote_cmd" , "move:random" + "@" + actor )   

                    self.__send_cmd("remote_cmd" , "speak:" + row["value"] + "@" + actor)  
                          
                    self.__wait_for("spoke")

                elif row["command"] == "speak-no-wait": 
                     self.__send_cmd("remote_cmd" , "speak:" + row["value"] + "@" + actor)   
                     
                elif row["command"] == "sleep":  
                      time.sleep(float(row["value"])) 

                elif row["command"] == "move":  
                      self.__send_cmd("remote_cmd" , "move:" + row["value"] + "@" + actor )   
        return ""  
         
    @dispatcher
    def speak(self: object, in_subjects :str = "", in_objects: str ="" )-> str:
        """"commands a robot/agent to say passed message """
        cmd = {"cmd":"speak:" , "text" :in_objects.lower() }   
        if in_subjects.find("@") == -1:
            in_subjects += "@all"
 
        self.__send_cmd("remote_cmd" , "speak:" + in_objects +in_subjects)     

        return "" 
           

if __name__ == '__main__': 
     """
     
     """  
     pass
 