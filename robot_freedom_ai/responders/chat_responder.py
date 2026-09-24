import threading
import time 
from . responder import Responder, handle_exceptions 

import json 

MoodDisplay  = {"happy":     "0",
                "sad":       "1",
                "bored":     "2",
                "surprised": "3",
                "fear":      "4",
                "disgust":   "5",
                "anger":     "6" }

@handle_exceptions 
def speak_and_wait(robot, 
                   nerves, 
                   settings,
                   MovementHandler,
                   expressions, 
                   wait_length,
                   polling_rate ,
                   mood
                   ):
        """
        
        """   
        verbose = False
        if verbose: 
            t = open("thread.log", "a")
            t.write("started\n")
        i_cnt = 0
        state_a = ["q", "s"]
        state_b = ["a", "w"]

        nerves.set("ongoing_conversation", "True" ) 

        if  settings["robot_form"] in ["cat", "dog", "mouse"]:
           MovementHandler.send_command(state_b, robot)   

        flip = 0
        while True:  
            detect, val = nerves.pop("spoke")  
            i_cnt += 1 
            if i_cnt % 10 == 0:
               if settings["robot_form"] in ["cat", "dog", "mouse"]:  
                    if flip == 1:
                      state = state_a
                      flip=0
                    else:
                      state = state_b
                      flip =1 
                   # MovementHandler.send_command(state, self.robot) 
               else:
                  try:
                      MovementHandler.send_command(["random"], robot)   
                  except Exception as e: 
                     t = open("movment.error.log",  "a")
                     t.write("Error " + str(e) + "\n")
               
            if detect or i_cnt >  wait_length : 
                break    
             
            time.sleep( polling_rate) 

        if settings["robot_form"] in ["cat", "dog", "mouse"]:
             MovementHandler.write(["a"] ,  robot) 
             MovementHandler.write(["s"] ,  robot) 
 
        if mood in MoodDisplay: 
            answer =  expressions.write("expressions light " + str(MoodDisplay[mood]) + ";", 
                                        robot)
            
            nerves.set("expression_vocal", mood)  
        else:
            answer =  expressions.write("expressions light 7;",  robot)
            nerves.set("expression_vocal", mood ) 
        
        if verbose: 
             t.write("updating nerves\n")
        time.sleep(.5)
        _b,_v = nerves.pop("ongoing_conversation")   

        if verbose: 
           t.write("ended\n")
   
        return True 

class ChatResponder(Responder): 
    """
    
    """

    def response_error(self): 
 
            if  self.cannot_understand > 1:
                resp = "Yeah... I still cannot understand you." 
            elif  self.cannot_understand > 2:
                resp = "So... why not slow down and try again." 
            elif  self.cannot_understand > 3:
                resp = "I am not sure if anything meaningful is being said." 
            elif  self.cannot_understand > 4:
                resp = "So I cannot translate what is being said " + str(self.cannot_understand) + " times in a row so far." 
            else:
                resp = "I am sorry could you repeat what you said?" 
                self.cannot_understand  = 0

            self.cannot_understand = self.cannot_understand + 1 
            return resp
    
    @handle_exceptions 
    def get_chat_response(self, prompt, 
                          mood="happy",
                          tone="Appreciative", 
                          topics=["cat"], 
                          objective="engagement",
                          situation= {}):
        """
        
        """
        
        param = {}
        prompt = prompt.replace("'", "<aprostophy>").replace("`", "<aprostophy>")
        param["action"]     = "respond"
        param["prompt"]     = prompt.replace("'", "<aprostophy>")
        param["mood"]       = mood 
        param["tone"]       = tone 
        param["topics"]     = topics
        param["objective"]  = objective
        param["situation"]  = situation   
        self.nerves.set("chat" , json.dumps(param) )
 
        time.sleep(self.polling_rate)
        i_cnt = 0
        while True:
            detect, val = self.nerves.pop("chat_responses")  
            i_cnt += 1
            if detect:
                self.nerves.set("speech", "")   
                return val   
             
            elif i_cnt > self.chat_wait_length:

                #_f = open("chat_time_out.log", "a")
                #_f.write("time out " + json.dumps(param) +  "\n")

                self.nerves.set("speech", "")   
                return self.response_error()  
            
            time.sleep(self.polling_rate)
 
        nerves.set("speech", "")   
        return "" 
    
    @handle_exceptions 
    def discussion_response(self, resp):
        """
        send 
          
        """ 

        self.communication.send(self.discussion_partner, 
                                "discussion_start:" + resp.replace(":", " "))
         
        i_cnt = 0
        while True:
            detect = self.communication.check_for_a_message(self.robot, 
                                                            "discussion_done", 
                                                            self.discussion_partner)
            i_cnt += 1
            if detect :
                return resp  
            
            elif i_cnt > 300:
                return "I am sorry, could you repeat that."  
            time.sleep(self.polling_rate)

        return resp 
    
    @handle_exceptions 
    def speak(self,message):
        """
        
        """ 
        self.nerves.set("speak" ,";".join(["speak-w", "wait", message]))
    
    @handle_exceptions 
    def speak_and_wait(self, message, mood= "happy"):
        """
        
        """
        if message.strip() == "":
           return False 
        
        if self.settings["robot_form"] in ["cat", "dog", "mouse"]:
            self.movement.write("movment legs a;" , self.robot) 
            self.movement.write("movment legs s;" , self.robot) 

        answer = self.expressions.write("5", self.robot  ) 
        detect, val = self.nerves.pop("spoke")  
        self.speak(message)   
       # lock = threading.Lock()c
        x = threading.Thread(target=speak_and_wait, 
                             args=(self.robot, 
                                   self.nerves, 
                                   self.settings,
                                   self.agent.handlers["MovementHandler"],
                                   self.expressions, 
                                   self.wait_length,
                                   self.polling_rate ,
                                   mood)
                                   )
        verbose = False
        if verbose:
            t = open("thread.log", "a")
            t.write("launching..\n")
            t.close()
        
        x.start()

        return False
 