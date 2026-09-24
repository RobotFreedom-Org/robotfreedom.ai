import os, time 
import pygame     
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode")  
parser.add_argument("-r", "--robot")  

class Rift(object):

    def __init__(self, robot, nerves, config, settings, polling_rate =.05):
        """
        
        """ 
       # self.os       = config.OS  
        self.robot    = robot  
        self.nerves   = nerves  
        self.settings = settings  
        self.config   = config    
        self.polling_rate = polling_rate
        self.robot     = robot
        self.devices  = {}  
        self.module   = "expression_vocal"
        self.log      = True 
         
        pygame.init()   
        self.set_up(robot, {})

    def set_up(self,robot, params ):
        """
        
        """  
 
        self.robot = robot     

        self.surprise_sound   = pygame.mixer.Sound("./vocalization/snds/dream-synth-pluck_120bpm_E_major.wav")  
        self.bored_sound      = pygame.mixer.Sound("./vocalization/snds/bass-808-shot-decaying-boomy_69bpm_C_major.wav")  
        self.sad_sound        = pygame.mixer.Sound("./vocalization/snds/gunna-type-harp-sad-thoughtful-melody_101bpm_A_minor.wav")  
        self.fear_sound       = pygame.mixer.Sound("./vocalization/snds/retro-bass-sunsoft_C.wav")   
        self.happy_sound      = pygame.mixer.Sound("./vocalization/snds/yum-yum-dark-cowbell_C#.wav")     
        self.anger_sound      = pygame.mixer.Sound("./vocalization/snds/dark-screech-uptempo_150bpm_C_minor.wav")  
        self.disgust_sound    = pygame.mixer.Sound("./vocalization/snds/loud-distorted-bass_C_minor.wav")   

        self.snds = {}
        self.snds["bored"]     =  self.bored_sound  
        self.snds["sad"]       =  self.sad_sound 
        self.snds["happy"]     =  self.happy_sound
        self.snds["surprised"] =  self.surprise_sound 
        self.snds["fear"]      =  self.fear_sound 
        self.snds["anger"]     =  self.anger_sound  
        self.snds["disgust"]   =  self.disgust_sound 

    
         
    def switch_robot(self, robot):
        """
        
        """  
        self.set_up(robot)
        self._switch_speaker(robot)

    def _switch_speaker(self, robot, speaker_config):
        """
        
        """  

        if self.os == "OSX": 
            os.system("SwitchAudioSource -i " + self.devices[robot][1]) 
            time.sleep(.1)
  
    def speak(self, message ): 
        """
        
        """ 

        pygame.mixer.Sound.play(self.snds[message ])
        pygame.mixer.music.fadeout(1) 
  
     
    
    def wait(self): 
        """
        
        """
        time.sleep(.1) 

   
    def serve_forever(self): 
       """
       
       """ 
       while True:
           
          new, cmds = self.nerves.pop(self.module) 
          if new: 
              self.speak(cmds)  
              self.wait()     
                    

          time.sleep(self.polling_rate)
 
 
 
if __name__ == "__main__":
    """ 
    
    """
    args =  parser.parse_args() 

    mode    = args.mode 
    robot   = args.robot   
    
    nerves   = {}
    config   = {} 
    settings = {} 

    voice  = Rift(robot,  nerves, config, settings )
    if mode == "serve": 
        voice.serve_forever()

 