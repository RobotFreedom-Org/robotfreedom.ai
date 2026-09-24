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

####    Libraries   ################  
import json
import sys   
import datetime  
import time   
import argparse
from responders.chat_responder import MoodDisplay

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode")  
parser.add_argument("-r", "--robot"        , default="")    
parser.add_argument("-p", "--params"       , default="{}")  
parser.add_argument("-c", "--command_style", default="sequence")  
parser.add_argument("-v", "--verbose"      , default=False)   
 
sys.path.append("..")
from  errors import handle_exceptions, ERRORCNT
    
class Protocol(object):
    """
    
    """
    
    def __init__(self, protocol, agent ):
        """ 

        """ 

        self.protocol     = protocol  
        self.agent        = agent  
        self.voice_active = True
        self.os           = agent.config.OS
        self.config       = agent.config.CONFIG   
        self.verbose      = agent.config.VERBOSE 
        self.LAST_MOVE_TIME =  datetime.datetime.now()   
        self.LAST_COMMAND   =  datetime.datetime.now()   
        self.chat           = agent.chat
        self.networked      = agent.networked
        self.robot          = self.agent.robot  
        self.polling_rate        = self.agent.polling_rate
        self.polling_rate_listen = self.agent.polling_rate_listen
        self.low_memory_mode     = self.agent.low_memory_mode
        self.speaking            = False
        self.receiving_commands  = False 
        
        self.locomotion_cmds = []

        self.nerves          = agent.nerves
        self.behavior        = agent.behavior 
       
        self.locomotion      = agent.locomotion
        self.movement        = agent.movement

        self.communication   = self.agent.communication
        self.interactions    = self.agent.interactions 
 
        self.current_states  = self.agent.current_states 
            
        self.get_chat_response   = self.agent.responders["ChatResponder"].get_chat_response
        self.speak_and_wait      = self.agent.responders["ChatResponder"].speak_and_wait
        self.speak               = self.agent.responders["ChatResponder"].speak
        self.discussion_response = self.agent.responders["ChatResponder"].discussion_response
        self.respond_to_request  = self.agent.responders["CommandResponder"].respond_to_request 
        self.send_command        = self.agent.handlers["MovementHandler"].send_command
          

        self.prompts = ["robot", "robotics", "hello", 
                        "ai", "ok", "okay",
                        "number", "three", "two"]
        
        self.self_reflection_threshold = 2
        self.prior_response    = {}    
        self._space            = " ".join(['' for v in range(40)]) 
        self.epoch             = 0
        self.cnt_remote_cds    = 0
        self.last_remote_cd    = datetime.datetime.now()
        self.last_stimuli      = datetime.datetime.now()
        self.current_cycle     = datetime.datetime.now() 
        self.last_update       = datetime.datetime.now() 
        self.last_movement     = datetime.datetime.now() 
        self.last_spoke        = datetime.datetime.now() 
        self.last_self_reflect = datetime.datetime.now()  
      
        __t = self.nerves.get("stimuli_cnts")
        _t = {}
        if __t is not None:
            if __t != "":
               _t = json.loads(self.nerves.get("stimuli_cnts")) 
 
        _s = list( self.behavior.cognitive_control.sense_types["physical"].keys()) + ["speech","noise", "voice"]
        for sense in _s:
            if sense not in _t:
                _t[sense] = 0

        for sense in  ["temperature", "humidity", "light" ,"compass"]:
            sense = sense + "_reading"
            if sense not in _t:
                _t[sense] = 0

        self.nerves.set("stimuli_cnts", json.dumps(_t))

        self.discussion_partner = None 
        self.self_reflection_threshold = 4
        self.prior_response   = {}

        self.quiet_in_secs    = 60
        self.last_moved       = 99
        self.last_talked      = 99 
        self.sensor_pause     = .1 #.01 

    def log_sense(self,sense, amplitude, responses, direction =None):

        _t = {}
        _t["stimuli"]        = sense   
        _t["amplitude"]      = amplitude   
        _t["responses"]      = responses   
        _t["objective"]      = str(self.behavior.objective)
        _t["objectives"]     = self.behavior.objectives 
        _t["sentiment"]      = self.behavior.scrs 
        _t["situation"]      = self.behavior.situation
        _t["goals"]          = {}
        _t["goals"]["met"]   = self.behavior.met   
        _t["goals"]["umet"]  = self.behavior.umet   
        _t["goals"]["indif"] = self.behavior.indif     
        _t["stimuli_goal_factors"] = self.behavior.motivations.stimuli_goal_factors(sense) 
        _t["strategy"]             = self.behavior.experience.current_strategy  
        _t["nonverbal_strategy"]   = self.behavior.experience.current_nonverbal_strategy  
        _t["strategies"]           = self.behavior.experience.current_strategies
        _t["emotions"]             =  {k: v for k,v in self.behavior.emotions.moods.items()}
        _t["mood"]                 =  self.behavior.emotions.mood()  

        self.nerves.set("stimuli", json.dumps(_t))   

        _t = json.loads(self.nerves.get("stimuli_cnts")) 
        _t[sense]   = _t[sense] + 1
        _t["robot"] = self.robot
        _t["said"]  = "" 

       

        for  _sense in ["temperature", "humidity", "light"] : #, "compass"]:
                reading = self.nerves.get(_sense + "_reading") 
                try:
                    _t[_sense + "_reading" ] = str(round(float(reading),1))   
                except:
                    _t[_sense + "_reading" ] = str(0)   

        if direction :
            _t["direction"] = direction
        else:
            _t["direction"] = ""

        if sense == "speech":
            _t["heard"] = amplitude[:15]
        else:
            _t["heard"] = ""

        if self.agent.safty_overide:
            _t["safty_overide"] = "1"
            self.nerves.set("safty_overide",  "1")
        else:
            _t["safty_overide"] = "0"
            self.nerves.set("safty_overide",  "-1")

        self.nerves.set("stimuli_cnts", json.dumps(_t))

    
    @handle_exceptions 
    def check_remote_commands(self, i_quiet):  
  
            for label in ["left", "right", "forward", "backward", "stop", "center"]: 
                detected, protocol = self.nerves.pop("cmd:" + label)  
              
                if detected: 
                    print("###########################")
                    print("###### " +  label[0] +  " ######") 
                    print("###########################") 

                    self.locomotion_cmds.append([label[0], 1,1])  
                    self.receiving_commands  = True 
                    self.LAST_COMMAND =  datetime.datetime.now() 
                    self.last_remote_cd = datetime.datetime.now() 

            for cmd in ["snapshot", "reset", "vocal", "change_protocol", "intro", "auto", "diagnostics"]: #"safty", 
               
               detect, protocol = self.nerves.pop("cmd:" +cmd)
               if detect:   

                   self.last_remote_cd = datetime.datetime.now() 
                   self.cnt_remote_cds +=1 
                   print("###########################")
                   print("###### " +  cmd +  " " + protocol +   " ######") 
                   print("###########################") 


                   if cmd == "diagnostics":
                       res ={}
                       res["generation_dt"] = str( datetime.datetime.now() )
                       res["movement"]      = str(self.agent.movement.connected)
                       res["locomotion"]    = str(self.agent.locomotion.connected)
                       res["device_connections"]    = str(self.agent.device_connections)
                       res["cmds_cnt"]      = str(self.cnt_remote_cds)
                       res["protocol"]      = str(self.agent.protocol) 
                       res["errors"]        = str(ERRORCNT  )
                       self.nerves.set("response:diagnostics", json.dumps(res))   
                       
                   elif cmd == "snapshot":
                       self.agent.camera.capture()

                   elif cmd == "vocal": 
                       self.voice_active =   self.voice_active *-1    

                   elif cmd == "change_protocol":
                       self.agent.change_protocol(protocol)

                   elif cmd == "reset":
                       self.agent.reset() 
                    
                   elif cmd == "safty":     
                          
                          if self.agent.safty_overide:  
                               self.agent.safty_overide = False
                               self.nerves.set("safty_overide", "-1")  
                          else: 
                               self.nerves.set("safty_overide", "1")  
                               self.agent.safty_overide = True  


            ### Update clocks 
            if self.low_memory_mode or self.networked == -1:
                have_message, commands = False , ""
            else:  
                have_message, commands = self.communication.check_messages() 


            if have_message:   
                
                if commands.find("@" + self.robot ) > -1:   
                       commands =  commands.find("@" + self.robot   , "")
                       self.respond_to_request(commands) 
                       return False 
                
                elif commands.find("remote_cmd") > -1:  
                    self.respond_to_request(commands) 
                    return False  

                elif commands.find("direct_cmd") > -1:  
                     by_pass =True 
                     acommands = commands.split(":")[1].split(',')
                     if len(acommands) == 1:
                         self._detected(acommands[0], i_quiet, "")
                     else:    
                         self._detected(acommands[0], i_quiet, acommands[1])
                     return False  

                elif commands.find("announcement") > -1:  
                     return False 
                else:
                    print("UNKNOWN COMMAND", commands)
        
            detect, commands = self.nerves.pop("remote_cmd") 
            if detect:
                self.respond_to_request(commands) 
                return False 
            
            return True   
    
    @handle_exceptions     
    def obstacle_avoidance(self, res , x,y,z, time_since_last_change): 

        i = 0

        while res  == "BLOCKED":   
             
             self.nerves.set("expression_vocal", 'surprised' ) 
             self.behavior.wayfinder.sense(["wall", x, y, z]) 
             self.behavior.wayfinder.reasoning(self.current_direction, 
                                                  time_since_last_change, 
                                                  []) 
             locomotion  = self.behavior.wayfinder.pop()    

             for action in locomotion:
                 self.current_direction, self.speed, self.duration = action[0], action[1]  ,action[2] 
                 x,y,z,dist = self.behavior.wayfinder.calc_x_y_z(time_since_last_change, 1, 1, 0, 1) 
                 pulse_modulation = 1
                 if self.current_direction in ["l", "r", "b"]:
                     pulse_modulation = 4
                     
                 for i in range(pulse_modulation):
                      res = self.agent.handlers["LocomotionHandler"].move(self.current_direction , self.speed, self.duration )  
                      res = res.strip() 

                      if res  == "BLOCKED":   
                          i += 1
                          if i > 2:
                              self.nerves.set("expression_vocal", 'disgust' )  
                
        return res
    
            
    @handle_exceptions     
    def locomotion_request(self, start_action , x,y,z, time_since_last_change): 

        i_blocked = 0
        queue = []
        queue.append(start_action)
        self.locomotion_goals = start_action
        while len(queue) > 0:  
            action = queue.pop() 
            self.current_direction, self.speed, self.duration = action[0], action[1]  ,action[2] 
            pulse_modulation = 1
            if self.current_direction in ["l", "r", "b"]:
                pulse_modulation = 4

            for i in range(pulse_modulation):
                res = self.agent.handlers["LocomotionHandler"].move(self.current_direction , self.speed, self.duration )  
                res = res.strip()  
                if res  == "BLOCKED":  
                    i_blocked  += 1  
                    self.behavior.wayfinder.sense(["wall", x, y, z]) 
                    self.behavior.wayfinder.reasoning(self.current_direction, 
                                                      time_since_last_change, 
                                                      self.locomotion_goals)  
            
                    self.nerves.set("expression_vocal", 'surprised' )  
                    locomotion  = self.behavior.wayfinder.pop()    
                    for new_action in locomotion:
                        queue.append(new_action)

                    if i_blocked > 5:
                         self.nerves.set("expression_vocal", 'disgust' )   
                         return res
                
        return res
    

    @handle_exceptions 
    def locomotion_directives(self,  time_since_last_change):
        b_moved      = False
        self.verbose = True
        if self.verbose:
           if len(self.locomotion_cmds) > 0 :
              print("########################")
              print("########################")
              print("########################")
              print(self.locomotion_cmds) 

        for action in self.locomotion_cmds:  
            b_moved = True
            self.current_direction, self.speed, self.duration = action[0], action[1]  ,action[2] 
            locomotion_goals = []
            if self.verbose:
                 print("Moving " + self.current_direction)

            res = self.agent.handlers["LocomotionHandler"].move(self.current_direction , 
                                                                       self.speed, 
                                                                       self.duration )   
            #if self.verbose:            
            #     print("results " + res)
                   
            x,y,z,dist = self.behavior.wayfinder.calc_x_y_z(time_since_last_change, 1, 1, 0, 1)

            if self.verbose:            
                 print("Wayfinder ", x, y, z, dist)

            if res.strip() == "BLOCKED":  
                b_moved = False
                self.behavior.wayfinder.sense(["wall", x, y, z]) 
                self.behavior.wayfinder.reasoning(self.current_direction, 
                                                  time_since_last_change, 
                                                  locomotion_goals) 
                locomotion  = self.behavior.wayfinder.pop()      

                self.nerves.set("expression_vocal", 'disgust' )   

                if self.verbose:
                    print("########################")
                    print("#########"  + str(locomotion) + "########")
                    print("########################") 
                
        self.locomotion_cmds = [] 
        self.verbose = False 
        return b_moved
    
    @handle_exceptions 
    def quick_chat(self, prompt):

                answer =  self.agent.expressions.write("expression lights 0;",  self.robot)
                #self.respond_to_request(commands, self)  
                user_detected = 1
                self.agent.behavior.stimuli("sense", 
                                            "speech", 
                                            prompt,  
                                            1,
                                            self.prior_response ,
                                            user_detected, 
                                            self.epoch, 
                                            datetime.datetime.now(), 
                                            self.last_moved,
                                            self.last_talked, 
                                            self.interval,
                                            self.chat)   
                

                response  = self.agent.interactions.responses("sense",
                                                              "speech", 
                                                               prompt, 
                                                               self.agent.behavior,
                                                               True, 
                                                               self.agent.responders["ChatResponder"].get_chat_response)   
                #self.speak( response["speech"][0]) 
                self.nerves.set("chat_responses_2","respond>"+ response["speech"][0]) 
            
                responses = {"speech":[response], "movement": ["random"], "locomotion":[]}  
                self.log_sense("speech", prompt, responses)
                mood = self.behavior.emotions.mood()  
                #self.speak_and_wait(response, 
                #                    self.behavior.emotions.mood() )  

                if mood in MoodDisplay: 
                    answer =  self.agent.expressions.write("expression lights " +str(MoodDisplay[mood] ) + ";" ,  self.robot) 
                    self.nerves.set("expression_vocal", mood)  
                else:
                    answer =  self.agent.expressions.write("expression lights 7;",  self.robot)
                    self.nerves.set("expression_vocal", mood ) 
                  
    @handle_exceptions 
    def _detected(self, sense, i_quiet, amplitude):
        """

        """  
        interval              = (datetime.datetime.now() - self.last_stimuli).total_seconds()   
        self.last_moved       = (datetime.datetime.now() - self.last_movement).total_seconds() 
        self.last_talked      = (datetime.datetime.now() - self.last_spoke).total_seconds()   
        last_cmd_any           = (datetime.datetime.now() - self.last_remote_cd).total_seconds()  
        
        user_detected = 0
        if last_cmd_any > 120:
             user_detected  = 1
        else:
             user_detected  = 0
 

        if i_quiet >= self.self_reflection_threshold: 
            if  self.low_memory_mode is False: 
                    print("\r" + "Initiating Sleep Cycle..."     +     self._space )  
                    print("\r" + "Dreaming....            "      +     self._space )   
                    self.behavior.reflection()
                    self.last_self_reflect  = datetime.datetime.now()

            print("\r" + "Starting Wakeup Sequence..." + self._space, end="")  
            self.chat = False 


        self.behavior.stimuli("sense", sense, amplitude,  1, 
                               self.prior_response ,
                               user_detected,
                               self.epoch, 
                               datetime.datetime.now(), 
                               self.last_moved,  
                               self.last_talked, 
                               interval, 
                               self.chat)  
        
        pounderings    = self.agent.sub_conscious.pounderings(self.behavior.emotions.mood() ,  
                                                              sense,
                                                              amplitude,
                                                              self.agent.behavior ) 
 
        if sense == "speech" and  self.chat is False:  
            amplitude = self.agent.ethics.filter_bad_words(amplitude)
            prompts = [k for k in amplitude.lower().split(' ') if k in self.prompts]  
            if len(prompts) > 0:
                self.chat = True  

        if self.chat:  
            if type(amplitude) is float:
                responses = {"speech":[], "movement": ["random"], "locomotion":[]} 

            elif amplitude.strip() == "":
                responses = {"speech":[], "movement": ["random"], "locomotion":[]}

            elif sense == "speech":  
                amplitude = self.agent.ethics.filter_bad_words(amplitude)
                print("Heard   :", amplitude) 
                responses = self.interactions.responses("sense", 
                                                 sense, 
                                                 amplitude,  
                                                 self.behavior,
                                                 self.chat, #True
                                                 self.get_chat_response) 
                responses["locomotion"]  = [] 
                _t = []
                for response in responses["speech"]:   
                   if type(response) == str:
                       _t.append(self.agent.ethics.filter_bad_words(response))
                   
                responses["speech"] = _t

                print("Said   :", responses)
            else:
              #  responses = {"speech":[], "movement": ["random"], "locomotion":[]}

                responses = self.interactions.responses("sense", 
                                                     sense, 
                                                     amplitude,  
                                                     self.behavior,
                                                     self.chat,
                                                     self.get_chat_response,
                                                     b_just_move = True)  
                
        else:
            responses = self.interactions.responses("sense", 
                                                     sense, 
                                                     amplitude,  
                                                     self.behavior,
                                                     self.chat,
                                                     self.get_chat_response) 
            responses["locomotion"]  = [] 
                        
        self.log_sense(sense, amplitude, responses)  

        for response in responses["movement"]: 
            self.send_command(response, self.robot) 

        response = "" 
        if self.voice_active and self.speaking is False:
          for response in responses["speech"]:  
            if response != "":

                self.nerves.set("speach_start", str(datetime.datetime.now()) )  
                self.nerves.set("ongoing_conversation", "true")  
                self.nerves.set("ignore_speech", "true")  

                self.speak_and_wait(response, 
                                    self.behavior.emotions.mood() )   
                self.prior_response  =  responses 
                self.speaking        =  True  
                 
                

        self.last_stimuli  = datetime.datetime.now()   
        time.sleep(self.sensor_pause) 
        self.nerves.set(sense, "")  
  

        return True
     
if __name__ == "__main__": 
    """
    
    """
    args =  parser.parse_args()  
    mode    = args.mode    
    robot   = args.robot    
