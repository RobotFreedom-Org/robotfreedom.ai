# -*- coding: utf-8 -*-
  
"""
/Users/theodoreharris/Desktop/MAKER25Data /chat/chat_ollama.train.log
Description: This builds and controls a simple chatbot design to run on a RaspberryPi.
Author: HipMonsters.com 
Date Created: Jan 1, 2021
Date Modified: Oct 10, 2024 
Version: 8.0
Platform: RaspberryPi
License: MIT License   

""" 
import   re 
import warnings  
 
warnings.filterwarnings("ignore")    

from llama_cpp  import Llama   
 
 
max_tokens  = 50  #20 #16
temperature = .15 #0.9  

parts_all = ['Object' , 
             'Verb' , 
             'Subject' , 
             'Complement' ,
             'Modifier' , 'Intent']

parts = ['Subject', 'Verb', 
         'Object', 'Complement',
         'Modifier'] 

Ideas = [ ["Idea"          , "Concept" ], 
              ["Question"      , "Self"],   
              ["Question"      , "Speaker" ],
              ["External_Idea" , "Concept"],
              ["Speaker_Idea"  ,  "Concept"   ]] 
     
Ideas_query = [ ["Idea"   , "Concept" ], 
                ["External_Idea", "Concept"] ]    

class RAGAdv(object):

    def __init__(self,  st_memory, lt_memory, build=False, verbose=False):
        """
        """ 

        self.verbose       = verbose 
        self.history       = []
        self.speaker_facts = {}
        self.lt_memory     = lt_memory 
        self.st_memory     = st_memory 
        build              = True
        self.current_user  = None 
        self.s_path = "../data/knowledge/"
        self.ai  = Llama("../data/llms/scripted_response.gguf",  
                                verbose=False)    
    
    def close(self):
         """
         """
         self.ai.close()   
 
    def reset_prompt(self, prompt): 
         """
     
         """ 
         pass 

    def respond(self, user_response, details, history,
                low_memory_mode,b_roll_switch,
                parse_response, messgae_simiarity_scrs,
                directives

                ):
          """
          Docstring for response
          
          :param prompt: Description
          :param ana: Description
          :param history: Description
          :param user_facts: Description
          """ 

          mood         = directives["mood"]       
          tone         = directives["tone"]       
          user_topics  = directives["user_topics"]
          objective    = directives["objective"]   
          objective_dsc = directives["objective_dsc"]  
          persona      = directives["persona"]   

          reason_cds = {}
          if low_memory_mode:  
              max_tokens  =  16
              temperature = 0.9
              max_attempts = 1
          else:
              max_tokens  = 20  
              temperature = 0.9
              max_attempts = 3 

          self.topics = details["lookup"]  
          self.motive = "command", "annoucements", "exclamations" 
          if  details["user_intent"][0] == "opinion":
              self.motive = "give advice."

          elif details["expected_response"][0] == "inquiry":
              self.motive = "learn" 
          else: 
              self.motive = "Ask questions about the " + self.topics[0] + "."
  
          persona =   persona + " You want to learn more."  
          #base_template = "You are a {mood} robot {tone}.   {persona} {objective_dsc} Your name is " + full_name +"." 
                       
          messages = []
          assistant_message = ""
          if b_roll_switch == False:
              messages.append( {"role": "system", "content": persona })
              messages.append( {"role": "system", "content": self.motive })

              for user_message, assistant_message in self.history:
                    messages.append({"role": "user", "content": user_message})
                    messages.append({"role": "assistant", "content": assistant_message})
              messages.append( {"role": "user", "content": user_response })

          else: 
             messages.append( {"role": "system", "content": "Imagine you are a human who is talking to a chatbot." })
             for user_message, assistant_message in self.history:
                   messages.append({"role": "user", "content": user_message})
                   messages.append({"role": "assistant", "content": assistant_message})
             messages.append( {"role": "user", "content": user_response })
             
          if self.verbose:
             print (messages)  
             
          attempts = []
          for i in range(max_attempts):
            
                output =self.ai.create_chat_completion(
                   messages= messages, 
                   max_tokens=max_tokens,  
                   temperature=temperature,
                )  
                if self.verbose:
                    print("raw", output["choices"][0]["message"]["content"] )

                response = output["choices"][0]["message"]["content"]  
                _response = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)(?=\s+)', response)
                if len(_response) > 1:
                    if _response[-1][-1] not in [".", "?", "!"]:
                        response = " ".join(_response[:-1]) 

                ai_response, quality  = parse_response(response, [])  

                src_repeat ,  on_topic = messgae_simiarity_scrs(assistant_message, 
                                                                     ai_response, 
                                                                     user_response)

                attempts.append([ai_response, src_repeat ,  on_topic, quality])  

                    
                messages = []   
                if len([]) > 0:
                   messages.append({"role": "user", "content": "please change the topic to cats after the following statement."})
                  
                  # messages.append({"role": "user", "content": "please let me explore this concept."})
                   messages.append({"role": "assistant", "content": "As you wish."})
                
                   messages.append( {"role": "user",  
                                    "content": user_response  })
                else:
                   
                   messages.append({"role": "user", "content": "please change the topic to cats after the following statement."})
                  
                   messages.append({"role": "assistant", "content": "As you wish."})
                   messages.append( {"role": "user",  
                                  "content":  user_response  })
                    
                max_tokens  = 15
                temperature = 0.9
 
          all = sorted(attempts, key = lambda x : -1*x[1] + x[2]  + x[3], reverse =True )
    
          if self.verbose:
              print(all) 
          ai_response = all[0][0]  
          return ai_response, reason_cds
           

if __name__ == "__main__":
    """ 


    """
                                  
    RESP={"stressed": ["I am sorry that you are stressed."],
              "grateful": ["I am grateful for being able to talk with you."],
              "lonely": ["When I feel lonely I reach out to my community."],
              "neutral": ["Today has so much potential."],
              "happy": ["Today is great!"],
              "sad": ["I find talking to others oftens works best."],
              "angry": ["I hear you. Take a deep breath."],
              "excited":["So cool!", "Tell me more!"],
              "calm":["I am feeling chill as well"],
              "awkward":["Best to shrug it off and start anew"],
              "thrilled":["Wow! Tell me more."],
              "nervous":["Take a deep breath."],
              "anxious":["Take a deep breath."],
              "depressed":["I recommend reaching out to others."],
              "furious":["I hear you. Take a pause and think of somethig yu like."],
              "content":["Totally agree."],
              "frustrated":["I hear you"],
              "serious":["I am listening."],
              "bored":["What do you like talking about?"],
              "tired":["Sound like you need a recharge. Maybe take a break?"],
              "irritated":["I am sorry."],
              "confused":["Lets walk through it together."],
              "hopeful":["Good approach"],
              "stressed":["Focus on what matters the most right now."],
              "grateful":["I feel awsome!"],   
              }    
     
             
                  
    prompts = {
           "Apologetic": ["I am upset", "I don't like you", "go away",
                          "that is not nice", "how rude"],
           "Amused": ["I like you", "you are cool", 
                      "u r cool", "i love robots", "neat"], 
           "Ardent": ["I like you", "you are cool", 
                      "u r cool", "i love robots", "neat"],
           "Inspirational":["What do you do.", "hi", "hello" , "hello how are u",
                          "hi! how are you doing?","helloooo","hi, are you there?",
                          "Hi I am human" ,"hello!", "hello AI"],            
           "Ambivalent": ["how do you feel","what are you thinking",
                          "what are your thoughts", "thoughts?"],
           "Altruistic": ["Who would you like to be?"] ,
           "Benevolent": ["u r cool", "i love u", "i like you",
                          "robots r cool", "hi"] , 
           "Candid":["You are a terrible AI", "I hate you",
                         "hate u", "that is stupid", "u r dumb", 
                         "you suck", "shut up","u suck"] ,
           "Diplomatic":["You are a terrible AI", "I hate you",
                         "hate u", "that is stupid", "u r dumb", 
                         "you suck", "shut up","u suck"] ,
           "Admiring": ["do you like me", "what do you think about me", "good bye" ],
           "Absurd" : ["Tell a joke.", "you are funny"],
        }
     

    for sent in  ["i like dogs", "i love dogs", 
                  "thank you! Did you know that turtles are all omnivours and tortoises are all", 
                  "i think i am sick", "what a great day", 
                  "what is your name"]:
        res = process(sent)
        print("\n",res)      

 