import random
import sys 

#ai_response  = "  /\\__/\\ ")
#ai_response  = "(> ^ w ^ <)  meow ")
 
RANDOM_RESPONSE = ["meow", "purr",
                   "meowwwwwwwwwwwwww",
                   "treat please", 
                   "food foooood", 
                   "play now!",
                   "open the door", 
                   "your water tastes good"]

MAX_RESP = len(RANDOM_RESPONSE) - 1
memory = {}
memory['couch'] = 0
memory['dog'] = 0 

personality_words ={
"ok":{"naughty":"fine", "nice":"yay!" },
"sorry":{"naughty":"whatever", "nice":"i appologize" },
"ok":{"naughty":"fine", "nice":"yay!" },
"ok":{"naughty":"fine", "nice":"yay!" }
}
"""  \
 
   def greeting(self, sentence):  
        for word in sentence.split():
            if word.lower() in self.set_chat_responses["greeting_inputs"]:
                return random.choice(self.set_chat_responses["greeting_responses"])

   def return_self_eval(self, behavior, mood, template_id): 
       
            template =  self.set_chat_responses["templates"][template_id]
            
            if template["source"] == "mood":
               resp = template["template"]
               response = [resp.replace("<INSERT>", mood )]

            elif template["source"] == "exit": 
               resp = template["template"]
               response = [resp] 

            elif template["source"] =="stimuli":
               resp = template["template"]
               stimuli = self.get_stimuli_summary(behavior)
               _len = len(stimuli) -1
               _int = random.randint(0, _len)
               stim = list(stimuli.keys())[_int]
               cnt  =  stimuli[stim]
               resp1 = " I experienced "
               resp1 +=  stim + " " + str(cnt) + " times today, " 
               response  = [resp.replace("<INSERT>", resp1 ) ]
            else:
                print("ERRROR" ,template["source"] )
                out = open('repsonse_error.out', "a")
                out.write(str(template) + "\n")
                out.write(str(template_id) + "\n")
                response = ["I feel " + mood]


            return response
        self.set_chat_responses = {}
        self.set_chat_responses["greeting_input"] = ("hello", "hi", "greetings", "sup", "what's up","hey",)
        self.set_chat_responses["greetings_response"] =  ["hi", "Drem yol lok (hello)","sup","hey", 
                                                           "greetings fellow dnd lover!",
                                                          "hi there", "hello", 
                                                          "I am glad you are talking to me!"] 
        self.set_chat_responses["templates"] = {}
        self.set_chat_responses["templates"]["feel"]      = {"source":"mood"   , "template": "I feel <INSERT>"}
        self.set_chat_responses["templates"]["day"]       = {"source":"stimuli", "template": "Today this happened: <INSERT>"}
        self.set_chat_responses["templates"]["good_bye"]  = {"source":"exit",    "template": "Goodbye!"} 
        self.set_chat_responses["queries"]                         = {}
        self.set_chat_responses["queries"]["goodbye"]              = {"template":"good_bye"}   
        self.set_chat_responses["queries"]["how do you feel"]      = {"template":"feel"}
        self.set_chat_responses["queries"]["how are you"]          = {"template":"feel"}
        self.set_chat_responses["queries"]["how are thing going"]  = {"template":"feel"}
        self.set_chat_responses["queries"]["are you ok"]           = {"template":"feel"}
        self.set_chat_responses["queries"]["whats up"]             = {"template":"day"}
        self.set_chat_responses["queries"]["what is up"]           = {"template":"day"}
        self.set_chat_responses["queries"]["what is going on"]     = {"template":"day"}
        self.set_chat_responses["queries"]["how was you day"]      = {"template":"day"}
        self.set_chat_responses["queries"]["what is happening"]    = {"template":"day"}  
 
               for query, details in self.set_chat_responses["queries"].items(): 
               
                   matches = [1 for w in prompt.split() if w in query.split()] 
                   if len(prompt.split()) > 0:
                        if len(matches) / float(len(prompt.split())) > .7: 
                            template_id = details["template"] 
                            resp = self.return_self_eval( behavior, mood, template_id)
                            b_cmd = True  
"""

class RulesChat(object):
  
  def __init__(self, st_mem, lt_mem, personality= "naughty" ,verbose=False ):
      """
      """
      self.verbose = verbose 
      self.personality= personality
      self.emotion = "indifferent"
      self.context = ""
  #def add_personality(self,resp):
  #    loop words
  def close(self): 
         """
     
         """ 
         pass 
  
  def reset_prompt(self, prompt): 
         """
     
         """ 
         pass 
  
  def respond(self, user_response, details, history, low_memory_mode, directives): 
     """
     
     """
     prompt = user_response
     details = {}
     x = prompt.lower().strip()
     x = x.replace(".", "").replace("?", "").replace("!", "").replace(",", "") 
     x = x.replace("  ", " ").replace("  ", " ")   
     self.emotion = directives["mood"]

     if x == "bye":
         
        if self.personality =="naughty":
              ai_response  = "Good bye servant don`t forget the treats!"
        else:
              ai_response  = "Bye Bye!"

     elif x.find("67") > -1:
         if random.randint(1,3) == 3:
             ai_response  = "Is that the number of treats you will give me?"
         else:
             ai_response  = "So you will lay with me 67 minutes?"

     elif x.find("how are you") > -1:
         
         ai_response  = "I feel " + self.emotion + " but I will feel wonderful if you give me a treat"
         self.context = "treats"
         
     elif x.find("here is a treat") > -1:
         self.emotion = "wonderful"
         self.context = "treats"
         ai_response  = "more?"

     elif x.find("here is another treat") > -1:
         self.emotion = "amazed "
         self.context = "treats"
         ai_response  = "YAYYYYY!!!"

     elif x.find("please don`t") > -1:
         self.context = "clean clothes"
         ai_response  = "Maybe I will, maybe I won`t"


     elif x.find("do you want to play") > -1:
         ai_response  = "duh but i also want a treat"
         self.context = "play"
         
    
     elif self.context == "treats" and x.find("yes") > -1:
        self.emotion = "happy" 
        ai_response  = "yum yum cinder will not wake you up meow"

     elif x == "i am your owner":

        if self.personality =="naughty":
           self.emotion = "confused"  
           ai_response  = "no you are my servant"
        else:
           ai_response  = "Hi there owner!"

     elif x.find("jump") > -1:
        ai_response  = "where"
         
     elif x.find("on my lap") > -1:
        ai_response  = "maybe if you play and give me a treat"
        self.context = "treats"

     elif x.find("lap") > -1:
        ai_response  = "I might sit on your lap but play first"

     elif x.find("can i pet you") >-1:

        if self.personality =="naughty":
            ai_response  = "give me a treat first"
            self.context = "treats"
        else:
            ai_response  = "Yes please!"
     
     elif x.find("so cute") > -1:

        ai_response  = "that i am"
        self.context = "cute"

     elif x.find("sit") > -1:
        ai_response  = "give me some cat nip and then we will talk"

     elif x.find("play") > -1 and x.find("what") > -1 and  self.context =="play" :
        ai_response  = "STRING!!!!"
        self.context = "play"

     elif x.find("play") > -1:
        ai_response  = "did someone say play? I want to play!"
        self.context = "play"

     elif x.find("no") > -1 and  x.find("play") > -1 :
         ai_response  = "PLAY WITH ME! (or else)" 

     elif x.find( "i have to clean") > -1:
        ai_response  = "and i have to eat"

     elif x == "fine" :
         ai_response  = "yay cinder convinced you"
         self.context = "treats"

     elif x == "come here":
        ai_response  = "maybe,if you give me 4 no, 5 treats"
        self.context = "treats"

     elif x.find("love you") > -1:
        ai_response  = "who doesn`t now about that treat"
        self.context = "treats"

     elif x.find("scratched me") > -1:
        ai_response  = "me?"
     
     elif self.context == "treats" and (x.find(" no ") > -1 or x.endswith(" no") or x == "no" or x.startswith("no")):
        self.emotion = "angry" 
        ai_response  = "cinder will sit on your clean cloths"
        self.context = "treats"

     elif x.find("trying to bite me") > -1:
        ai_response  = "of couse not "
    
     elif x == "why" or x == "why?":
        ai_response  = "cinder is hungry"
        self.context = "treats"

     elif x =="i have to clean the litter box":
        ai_response  = "so go clean it"

     elif x.find("already") > -1 and x.find("had") > -1 and  x.find("treats") > -1:
         ai_response  = "but cinder wants more" 
         self.context = "treats"

     elif x.find("maybe later") > -1:
         ai_response  = "cinder will remember for you"
         self.context = "treats"

     elif x.find("hole in") > -1 and  x.find("bag") > -1 :
         ai_response  = "cinder did not do it. the monster in the closet did"

     elif x.find("no treat ") > -1:
        ai_response  = "human servent that is your only job"

     elif x.strip() in ["hi", "hello", "hi there", "ahola"]:
        ai_response  = "i want a treat now"
        self.context = "treats"

     elif x.find("you are getting fat") > -1 :
         ai_response  = "how rude"

     elif x.find("you") > -1 and  x.find("fat") > -1 :
         ai_response  = "how rude"
    

     elif x.find("hole") > -1 and  x.find("treat bag") > -1 :
         ai_response  = "cinder did not do it. the monster in the closet did"

     elif  x.find("why did you") > -1 :
         ai_response  = "cinder does not know what you are talking about"

     elif x.find("wake me up") > -1:
         ai_response  = "cinder does not know what you are talking about"

     elif x == "maybe":
         ai_response  = "giving me treats will help you be a better servant"
     
     elif x == "no food":
         ai_response  = "Buy food and do not forget cat toys"

     elif x.find("toy") > -1:

            if 'toy' not in memory:
                memory['toy'] = 0
            if  memory['toy'] == 0:
                ai_response  = "the dog keeps chewing on my toys"
                memory['toy'] = 1 
            elif  memory['toy'] == 1:
                ai_response  = "buy me new toys"
                memory['couch'] == 0

     elif x.find("why") > -1:

            if 'why' not in memory:
                memory['why'] = 0

            if  memory['why'] == 0: 
                ai_response  = "cinder should be obeyed"
                memory['why'] = 1 
            elif  memory['why'] == 1:
                ai_response  = "because i said so"
                memory['why'] == 2
            elif  memory['why'] == 2:
                ai_response  = "humans should do cat's biddings"
                memory['why'] == 3
            elif  memory['why'] ==3:
                ai_response  = "cinder needs servants"
                memory['why'] == 0
          
     elif x.find("good cinder") > -1 or x.find("good kitty") > -1   or x.find("good cat") > -1:
          ai_response  = "Thank you. You are a slightly okay servant."

     elif x.find("i know") > -1:
         ai_response  = "so get me a treat"
    
     elif x.find("earned it") > -1:
         ai_response  = "you bet i did"

     elif x.find("like cat") > -1:
         ai_response  = "I like cats too!"

     elif   x.find("like being a cat") > -1:
         ai_response  = "It`s okay, but if you give me a treat it would be better "

     elif x.find("earned it") > -1 or x.find("you deserved it") > -1:
         ai_response  = "you bet i did"
         self.emotion = "happy"

     elif x.find("stop biting") > -1:
        ai_response  = "when you obey me i might"
        self.emotion = "naughty"

     elif x.find("yeah right") > -1 or x.find("sure") > -1:
          ai_response  = "sarcasm is below me."

     elif x.find("rude")>-1:
          ai_response  = "cats are unable to be rude."

     elif x.find("you bit me") >-1 :
         ai_response  = "what do you mean i have not done anything"
         self.emotion = "naughty"

     elif x.find("bad cinder") > -1 or x.find("bad kitty") > -1   or x.find("bad cat") > -1:
          ai_response  = "and why would i care."
          self.emotion = "naughty" 

     elif x.find("fat") > -1 or x.find("mean") > -1   or x.find("dumb") > -1:
          ai_response  = "At least I`m not human"

     elif x.find("couch") > -1:
          
          if memory['couch'] == 0: 
              ai_response  = "what couch, who did what?"
              memory['couch'] = 1 
          elif memory['couch'] == 1:
              ai_response  = "oh! The yummy couch."
              memory['couch'] = 2
          else:
              if random.randint(0,2) == 1:
                  ai_response  = "whatever"
              else:
                  ai_response  = "it was good, okay? Stop judging me"

     elif x.find("dog") > -1:
          
          if memory['dog'] == 0: 
              ai_response  = "that flithy thing is here"
              memory['dog'] = 1 
          elif memory['dog'] == 1:
              ai_response  = "why would you bring this thing here"
              memory['dog'] = 2
          else:
              if random.randint(0,2) == 1:
                  ai_response  = "that thing reeks"
              else:
                  ai_response  = "i deserve three thousand treats and cat nip for living with that thing"

     elif x == "commands" :
        s = "meow meow respond with 'yes', 'no', 'why', 'fine', 'maybe later'\n"
        s+= "but you already had two treats','no treat','do you want to play','hi','you bit me'\n"
        s+=  " 'a phrase telling Cinder she is fat','okay you earned it','maybe','i have to clean'\n"
        s+=  "'hole in the treat bag','why','good cinder', 'couch','i am your owner',\n"
        s+=  "'i have to clean the litter box','you scratched me','are you trying to bite me'\n"
        s+=  "'come here','jump up','sit on me','so cute','i love you','can i pet you','dog'\n"
        ai_response  = s
        
     else :
         i = random.randint(0,MAX_RESP)
         if RANDOM_RESPONSE[i].find("treat") > -1: 
            self.context = "treats"
         ai_response  = "? "  + RANDOM_RESPONSE[i]
   
     return ai_response , details