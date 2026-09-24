
import os, time
# define constants  
import musicpy as mp
from   musicpy  import   C,  chord, play, note, rest, volume #,  get_cord 
 
 #import pygame as py  
"""
sudo apt-get install timidity freepats
"""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode")  
parser.add_argument("-r", "--robot")  
 
class Chirp(object):

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
        self.module   = "speak"
        self.log      = True 
        
        # a nylon string guitar plays broken chords on a chord progression
        self.phone_2_snds = {}
        self.set_up(robot, {})

    def set_up(self,robot, params ):
        """
        
        """  
 
        self.robot = robot 

        self.base_pitch = 2 #5 #4
        self.chord_speed = .05 
 
        self.a = note('A', self.base_pitch)  
        self.b = note('B', self.base_pitch)  
        self.c = note('C', self.base_pitch)  
        self.d = note('D', self.base_pitch)
        self.e = note('E', self.base_pitch)
        #self.r  = rest(.1) 
        self.au = note('A', self.base_pitch).up()  
        self.ad = note('A', self.base_pitch).down() 
        self.bu = note('B', self.base_pitch).up() 
        self.bd = note('B', self.base_pitch).down()  
        self.cu = note('C', self.base_pitch).up()  
        self.cd = note('C', self.base_pitch).down()  
        self.du = note('D', self.base_pitch).up() 
        self.dd = note('D', self.base_pitch).down()  
        self.eu = note('E', self.base_pitch).up() 
        self.ed = note('E', self.base_pitch).down()  
        self.g  = note('G', self.base_pitch)      
        self.gu = note('G', self.base_pitch).up() 
        self.gd = note('G', self.base_pitch).down()  
        self.f  = note('F', self.base_pitch)      
        self.fu = note('F', self.base_pitch).up() 
        self.fd = note('F', self.base_pitch).down()     
        self.emd  = C('Emaj', self.base_pitch).down() 
        self.cemd = chord('C5, E5, G6', self.base_pitch) # C('C5:maj7') 
        self.ac = chord('A2',  duration=self.chord_speed )  
        self.bc = chord('B3',  duration=self.chord_speed ) 
        self.cc = chord('C2',  duration=self.chord_speed )  
        self.dc = chord('D3',  duration=self.chord_speed )   
        self.ec = chord('E2',  duration=self.chord_speed )    
        self.fc = chord('F3',  duration=self.chord_speed )   
        self.r =  chord('r[.2]')

        self.tones = {}
        self.tones["AA"] = ["vowel",     "AC", 5]
        self.tones["AE"] = ["vowel",     "AC", 11]
        self.tones["AH"] = ["vowel",     "AC", 17]
        self.tones["AO"] = ["vowel",     "AC", 21]
        self.tones["AW"] = ["vowel",     "AC", 25]
        self.tones["AY"] = ["vowel",     "AC", 27]
        self.tones["B"]  = ["stop",      "BU", 31]
        self.tones["CH"] = ["affricate", "A" , 48]
        self.tones["D"]  = ["stop",      "C" , 31]
        self.tones["DH"] = ["fricative", "A" , 54]
        self.tones["EH"] = ["vowel",     "CC", 5]
        self.tones["ER"] = ["vowel",     "CC", 11]
        self.tones["EY"] = ["vowel",     "CC", 17]
        self.tones["F"]  = ["fricative", "BD", 54]
        self.tones["G"]  = ["stop",      "DU", 31]
        self.tones["HH"] = ["aspirate",  "A" , 10]
        self.tones["IH"] = ["vowel",     "CC", 21]
        self.tones["IY"] = ["vowel",     "CC", 25]
        self.tones["JH"] = ["affricate", "D" , 48]
        self.tones["K"]  = ["stop",      "E" , 31]
        self.tones["L"]  = ["liquid",    "E" , 57]
        self.tones["M"]  = ["nasal",     "A" , 72]
        self.tones["N"]  = ["nasal",     "DU", 79]
        self.tones["NG"] = ["nasal",     "F" , 72]
        self.tones["OW"] = ["vowel",     "DC", 5]
        self.tones["OY"] = ["vowel",     "DC", 17]
        self.tones["P"]  = ["stop",      "F" , 31]
        self.tones["R"]  = ["liquid",    "A" , 57]
        self.tones["S"]  = ["fricative", "BU", 87]
        self.tones["SH"] = ["fricative", "C" , 87]
        self.tones["T"]  = ["stop",      "A" , 31]
        self.tones["TH"] = ["fricative", "C" , 99]
        self.tones["UH"] = ["vowel",     "EC", 21]
        self.tones["UW"] = ["vowel",     "EC", 25]
        self.tones["V"]  = ["fricative", "DU", 109]
        self.tones["W"]  = ["semivowel", "FC", 114]
        self.tones["Y"]  = ["semivowel", "FC", 121]
        self.tones["Z"]  = ["fricative", "E" , 109]
        self.tones["ZH"] = ["fricative", "E" , 114]
        
        self.sound = {"A": self.a, 
                  "AU":self.au, 
                  "AD":self.ad,  
                  "B": self.b, 
                  "BU":self.bu, 
                  "BD":self.bd, 
                  "C": self.c, 
                  "CU":self.cu, 
                  "CD":self.cd, 
                  "D": self.d, 
                  "DU":self.du, 
                  "DD":self.dd, 
                  "E": self.e, 
                  "EU":self.eu, 
                  "ED":self.ed,
                  "F": self.f, 
                  "FU":self.fu, 
                  "FD":self.fd,
                  "R": self.r ,
                  "AC":self.ac, 
                  "BC":self.bc, 
                  "CC":self.cc, 
                  "DC":self.dc,
                  "EC":self.ec,
                  "FC":self.fc }
   
        self.phone_2_snds = {}
        for tn, vals in  self.tones.items():
             self.phone_2_snds[tn] = {"snd" :  vals[1] + "." + str(vals[2]) } 
  
        self.pronouce = {} 
        t = 0
        for line in open("./vocalization/pronouciation/cmudict.dict"):
            aline = line.strip().split(" ")
            snd = []
        
            for pro in aline[1:]:
                pro = pro.strip()
                if len(pro) > 2:
                    pro = pro[:2]
                if pro in self.phone_2_snds:
                    snd.append(self.phone_2_snds[pro])
                else:
                    print(pro)
            self.pronouce[aline[0]] =  snd

            """
            need to add these pronouce
            #
            fo
            fr
            ab 
            
            """
    
         
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
  
    def speak(self, message, b_simplify=False ): 
        """
        
        """
        message =  message.replace("`", "") 
        message =  message.replace("'", "").replace('"', "")
        message =  message.replace("[", "").replace("]", "")
        message =  message.replace("<", "").replace(">", "") 
        message =  message.replace("(", "").replace(")", "") 
        message =  message.replace("@", "").replace("%", "") 
        message =  message.replace("~", "").replace(":", "") 

        #if b_simplify:
        #    svo = svo_components(message)
        #    message = " ".join([v[0] for k, v in svo.items() if v[0] != "na"]) 

        snds = []
        for wrd in message.split(" "):
           if wrd in self.pronouce:
               snds.append(self.pronouce[wrd])
           else:
               t = [] 
               for letter in wrd: 
                   if letter in self.pronouce:
                      t.append(self.pronouce[letter][0]) 
                   else:
                       print(letter)    
               snds.append(t)   

           snds.append([{"snd":"R.1"}])   
 
        for wrds in snds:
           for wrd in wrds:
              scale,  instra = wrd["snd"].split(".")
              i = int(instra)

              if scale == "R":
                  time.sleep(.01)
              else:
                  snd_scale = self.sound[scale] 
                 # play(snd_scale, bpm=800, instrument=i, wait=True)     
                  # v = volume(90, start_time=0) 
                  play( snd_scale, bpm=10, instrument=i, wait=False )   
                  time.sleep(.08)
     
    
        play( self.r ,  wait=False )   

    def wait(self): 
        """
        
        """
        time.sleep(.1) 

   
    def serve_forever(self): 
       """
       
       """
       b_flip = True
       while True:
          
          if b_flip:
            #  print("\r listing | ", end = "")
              b_flip = False
          else:
             # print("\r listing - ", end = "")
              b_flip = True
          new, cmds = self.nerves.pop(self.module) 
          if new:
              acmds = cmds.split(";")   
              if len(acmds) < 2:
                  continue 
                  
              if  acmds[0] == "speak" and acmds[2] == "":
                  continue 
              if acmds[0] == "speak-w":
                  
                  found, val = self.nerves.pop("spoke" )
                  self.speak(acmds[2])  
                  self.wait()     
                  self.nerves.set("spoke", "Done")   
              elif acmds[0] == "speak": 
                  self.speak(acmds[2])   

          time.sleep(self.polling_rate)
 
 
 
if __name__ == "__main__":
    """ 
    
    """
    args =  parser.parse_args() 

    mode    = args.mode 
    robot   = args.robot   
    
    db   = {"speak":"how are you?"}

    config   = {} 
    settings = {} 

    class Nerves:

        def __init__(self, db):
            self.db = db

        def pop(self, module):
            return True, db[module]


    nerves = Nerves(db)
    voice  = Chirp(robot,  nerves, config, settings )

    voice.speak("how are you?")
    while True:
      mess = input("")
      voice.speak(mess)

   # if mode == "serve":
     
   # voice.serve_forever()

 