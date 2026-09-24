# -*- coding: utf-8 -*-
"""
Description: The agent daemon that allows the Artificial Intelligence to process sensors signals and control the robot.
Author: Mood_Relate.org 
Date Created: Jan 1, 2023
Date Modified: Oct 10, 2024
Version: 4.0
Platform: RaspberryPi
License: MIT License 
"""
import json 
import time

####    Libraries   ################

import config   
from communication.nerves         import Nerves 
from communication.client         import Client
from communication                import network 
#from communication.network_scan   import scan
from devices.tools                import scan_serial_ports
#from devices.card_reader          import CardReader
from triples.core                 import Triples   
from triples.trpl_graph           import TrplGraph

from mobility.movement_arduino    import MOVEMENT  
from mobility.locomotion_arduino  import LOCOMOTION   
 
from mobility.sequences           import sequences, FLIPS, RESETS 

from senses.camera           import Camera 
from security.security       import Security
from assets.logo             import logo 
 
from ai.personality          import Personality
from ai.behavior             import Behavior
from ai.interactions         import Interactions
from ai.cognitive_control    import CognitiveControl
from ai.ethics               import Ethics      
from ai.sub_conscious        import SubConcious  

from memory.st_memory        import STMemory   
from memory.lt_memory        import LTMemory   

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--protocol"     , default="monitor")  
parser.add_argument("-r", "--robot"        , default="")    
parser.add_argument("-n", "--networked"    , type=int,  default=-1, required=False)     
parser.add_argument("-d", "--directives"   , default="{}")   
parser.add_argument("-v", "--verbose"      , default=False)   
 
from errors import handle_exceptions 
    
class AIAgent(object):
    """
    
    """
   
    def __init__(self, protocol ,  
                  robot = "",   
                  networked = None ):
        """ 

        """ 

        self.protocol  = protocol   

        if networked is None:
             networked =  config.DEFAULT_2_NETWORKED 

        self.networked     = networked 

        self.os        = config.OS
        self.config    = config  
        self.verbose   = config.VERBOSE
        self._space  = " ".join(['' for v in range(40)]) 
        self.error_cnt = 0

        #loop parameters 
        self.polling_rate        = .1 
        self.polling_rate_listen = .05  
        self.protocol_continue    = True
        self.safty_overide       = False 
          

        #movement parameters 
        self.sequences = sequences  
        self.FLIPS     =  FLIPS
        self.current_states       = {}
 

        if robot != "":
            self.robot = robot 
        else:
            self.robot = self.config.CONFIG["robot"]   
        
        with open(self.config.DATA_PATH + self.robot + "/settings.json") as f:
           data = ''
           for row in f:
              data += row  
           self.settings = json.loads(data)

        if self.config.CONFIG["low_memory_mode"] == 1:
            self.low_memory_mode   = True
        else:
            self.low_memory_mode   = False
 
        self.communication_ip   = list(config.NET_CONFIG["hubs"].keys())[0]   


        print("\r Loading Nerves                         " + self._space, end="")
        self.nerves     = Nerves(self.robot) 

        print("\r Loading Triples               " + self._space, end="")
        self.triples  = Triples(agent=self.robot, 
                                config= self.config,
                                communication=None,
                                nerves=self.nerves,
                                client=False)  
        
        print("\r Loading Short Term Memory                " + self._space, end="")
        self.st_memory       = STMemory(robot, config , self.triples, self.low_memory_mode ) 
        self.triples.graphs["context"]     = self.st_memory.memory["kb"]  

        print("\r Loading Long Term Memory                " + self._space, end="")
        self.lt_memory       = LTMemory(robot, config , triples=self.triples, load_all = False)  
        self.triples.graphs["definitions"]      = self.lt_memory.memory["definitions"]  
        self.triples.graphs["jokes"]            = self.lt_memory.memory["jokes"]   
        self.triples.graphs["moods"]            = self.lt_memory.memory["moods"]    


        print("\r Scanning for attached devices               " + self._space, end="")
    
          
        if self.os  == "LINUX":
             self.device_connections = scan_serial_ports()
        else: 
             self.device_connections = scan_serial_ports()
        
        print("\r devices " + str( self.device_connections) )

        self.security   = Security(self.robot,
                                   self.config, 
                                   self.nerves)
        
        for to_clear in ["chat_responses_details", "chat_responses"]:
            self.nerves.pop(to_clear)  
 
        print("\r Communication ..."  + self._space , end="")
        
        if self.low_memory_mode == False and self.networked ==1: 

            if self.communication_ip is not None:
                self.communication = Client(self.robot, self.communication_ip)
            else: 
                self.communication  = Client(self.robot)
            
            try:
                self.communication.connect()
                self.communication.send("WORLD", "AWAKE")
            except:
                print("Issue Connecting")  
        else:
                self.communication = self.nerves
 
    
        print("\r Initializing Controller ...."  + self._space , end="")
        
        gpio_mobility = "arduino"
        if gpio_mobility == "rpi":
           from mobility.locomotion_gpio     import LOCOMOTION 
        else: 
           from mobility.locomotion_arduino  import LOCOMOTION  

        if self.os  == "LINUX":
            self.locomotion   = LOCOMOTION(self.nerves, config) 
        else:
            self.locomotion   = LOCOMOTION(self.nerves, config, b_test=True) 
           

        self.movement     = MOVEMENT(self.robot, config)    

        if self.settings["robot_form"] in ["mouse"]: #["cat", "dog", "mouse"]:
            self.expressions  = self.locomotion  
        else:
            self.expressions  = self.movement  
 
        print("\r Initializing Camera."  + self._space , end="" ) 
        self.camera       =  Camera(self.robot, 
                                    self.nerves ,
                                    self.config) 
        self.chat     = False 
        self.video    = False   

        print("\r Spawning Vocalization...."  + self._space , end="")
        self.nerves.set("speak" ,"Waking up.")  
   
        print("\r Connecting devices.  " + self._space, end="")
        self.connect_devices()
        
        ## TODO set up actions (Should load from YAML) 
        self.handlers = {}
        """
        ,   ["handlers.memory_handler"  , "MemoryHandler"],  
                        ["handlers.nerves_handler"  , "NervesHandler"]
        """
        for module in [ ["handlers.movement_handler", "MovementHandler"], 
                        ["handlers.locomotion_handler","LocomotionHandler"]]: 
            classname = module[1]
            _mod      = __import__(module[0] , fromlist=[None] )  
            self.handlers[classname]  = getattr(_mod, classname )( self ) 
             
        self.responders = {}
        for module in [ ["responders.chat_responder"    ,  "ChatResponder"], 
                        ["responders.command_responder"  , "CommandResponder"]]: 
            classname = module[1]
            _mod     = __import__(module[0] , fromlist=[None] )  
            self.responders[classname]  = getattr(_mod, classname )( self )  
        
        print("\r Loading AI Personality               " + self._space, end="")
        
        self.personality    = Personality(self.robot, 
                                         self.config,
                                         self.settings,
                                         self.triples )
        
        print("\r Loading AI CognitiveControl               " + self._space, end="")
        self.cognitive_control            = CognitiveControl(self.robot, 
                                                  self.config,
                                                  self.settings ,
                                                  self.personality,
                                                  self.triples,
                                                  self.low_memory_mode)
        

        print("\r Loading AI Sub Consious               " + self._space, end="")   
        trpl_graph = TrplGraph() 
 
        trpl_graph.copy(self.cognitive_control.episodic_memory)

        self.sub_conscious =  SubConcious(robot, config, self.nerves, self.lt_memory, 
                                          self.cognitive_control, trpl_graph , self.triples ,
                                          self.low_memory_mode)

        print("\r Loading AI Behavior                " + self._space, end="")
        self.behavior      = Behavior(self.robot               , 
                                    self.config              ,
                                    self.settings            ,
                                    self.personality         ,
                                    self.cognitive_control   ,
                                    self.st_memory           , 
                                    self.lt_memory           ,
                                    self.triples             ,
                                    self.low_memory_mode) 
  
 
        print("\r Loading AI Interactions          " + self._space, end="")

 
        self.interactions             = Interactions(self.robot, 
                                                     config,
                                                     self.nerves ,
                                                     self.cognitive_control,
                                                     self.lt_memory,   
                                                     self.triples ,
                                                     self.low_memory_mode)

        self.ethics                   = Ethics(self.robot)

        print("\r Robot and AI setup is complete." + self._space + self._space, end="")   

        if self.low_memory_mode == False and self.networked == 1:
            print("Communicating IP    :"    + self.communication.ip  +  self._space )  
            tmp = open(self.config.LOGS_PATH + "inet_addr.log","a" )
            tmp.write(self.communication.ip  + "\n")
            tmp.close() 
 
        ip_addr = network.get_local_ip()
        self.ip_address = ip_addr
        print("Robot's IP Address  :"    + ip_addr) 

    def reset(self):

        print("Resetting..." ) 
        self.nerves.set("chat" ,json.dumps({"action":"clear_mem"}))   


    def connect_devices(self):
        """
        
        """  
        ## arms and head
        self.movement.connect_to_devices(self.device_connections)  
        self.movement.write("expression light 7;", self.robot)
        for sig in RESETS:
             self.movement.write("movement torso " + sig + ";", self.robot)
             self.current_states[sig] = True

        ## expression
        self.movement.write("expression light 0;", self.robot) 
           
        ## moving
        self.locomotion.connect_to_devices(self.device_connections)   
        for sig in ["s"]:
             self.locomotion.move(sig, 0, .5)
            # self.current_states[sig] = True  
        
    @handle_exceptions 
    def change_protocol(self, protocol): 
        """

        """

        self.protocol = protocol 
        self.protocol_continue   = False
        time.sleep(10)
        self.protocol_continue   = True
        self.initiate({})

    @handle_exceptions 
    def initiate(self, directives):
        """
        
        """ 

        module                  = "protocols." + self.protocol
        classname               = self.protocol.title()
        _mod                    = __import__(module , fromlist=[None] )  
        self.current_protocol   = getattr(_mod, classname )(self.protocol, self ) 

        self.current_protocol.initiate(directives)

        return True
      
     
if __name__ == "__main__":

    """ 
     python agent.py -r number_3  -p listen -d '{"mode":"discussion", "partners":"number_b"}'
    """
    args       = parser.parse_args()  
    protocol   = args.protocol    
    robot      = args.robot   
    networked  = args.networked   
    directives = json.loads(args.directives) 
    networked = -1
    agent = AIAgent(robot = robot,
                    protocol=protocol,   
                    networked=networked ) 
    agent.initiate(directives)
