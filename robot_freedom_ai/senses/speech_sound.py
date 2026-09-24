# -*- coding: utf-8 -*-
  
"""
Description: Sensor daemon for speech.
Author: HipMonsters.com 
License: MIT License
""" 
import json 
import time   ,datetime
import struct
import queue
import math    
import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'
#https://stackoverflow.com/questions/72042826/alsa-couldnt-open-audio-device
#https://github.com/googlesamples/assistant-sdk-python/issues/219
"""
in ~
.asoundrc content:

pcm.!default {
  type asym
  capture.pcm "mic"
  playback.pcm "speaker"
}
pcm.mic {
  type plug
  slave {
    pcm "hw:0,0"
  }
}
pcm.speaker {
  type plug
  slave {
    pcm "hw:0,0"
  }
}
##while if I change the content of asoundrc file to use pulseaudio the Device unavailable goes a way and I can interact with the assistant with no problems

pcm.!default {
  type pulse
  fallback "sysdefault"
  hint {
    show on
    description "Default ALSA Output (currently PulseAudio Sound Server)"
  }
}

ctl.!default {
  type pulse
  fallback "sysdefault"
}


"""

import sounddevice as sd
from vosk import Model, KaldiRecognizer 
import argparse

try:
   from ._sense  import SenseBase
except:
   from _sense  import SenseBase

parser = argparse.ArgumentParser() 
parser.add_argument("-m", "--mode")  
parser.add_argument("-r", "--robot") 
parser.add_argument("-a", "--args", default="")  

INITIAL_TAP_THRESHOLD = 0.004
#FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 1
RATE = 44100 # 44100
INPUT_BLOCK_TIME = 0.1# 0.05
INPUT_FRAMES_PER_BLOCK =   int(RATE*INPUT_BLOCK_TIME) 
# if we get this many noisy blocks in a row, increase the threshold
OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME
# if we get this many quiet blocks in a row, decrease the threshold
UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME
# if the noise was longer than this many blocks, it's not a 'tap'
MAX_TAP_BLOCKS = (0.15/INPUT_BLOCK_TIME)*10 

def get_rms( block ):
    # RMS amplitude is defined as the square root of the
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into
    # a string of 16-bit samples...

    # we will get one short out for each
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768.
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )


def record_callback(indata, frames, time, status, q):
    """
    Callback for recording audio from the microphone.
    """ 
    q.put(bytes(indata))


class SpeechSound(SenseBase):

    def __init__(self,robot, nerves, config, settings, pins ={}):
        """
        
        """
        super().__init__(robot, 
                         nerves, 
                         config,  
                         settings,
                         "speech")
        _t, _n =self.nerves.pop("communication_complete")
        self.pins         = pins  
        self.last_message = -1
        self.b_adjusted   = False  
        self.polling_rate = .15
        self.log          = False

        self.quietcount    = 0 
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.noisycount    = MAX_TAP_BLOCKS + 1 


        self.device_info = sd.query_devices(sd.default.device[0], 'input')
        self.sample_rate = int(self.device_info['default_samplerate'])

        self.stt_model = Model(config.VOICES_PATH + "vosk-model-small-en-us-0.15" )
        #self.stt_model = Model(settings.VOICES_PATH + "vosk-model-en-us-0.22-lgraph" ) #lang='en-us')
        self.stt_recognizer = KaldiRecognizer(self.stt_model,
                                              self.sample_rate)
        self.stt_recognizer.SetWords(False) 
        print("initialized")

    def detect_noise(self, data):
        """
        
        """


        amplitude = get_rms( data )  

        if amplitude > self.tap_threshold: 
            self.quietcount = 0
            self.noisycount += 1
            if self.noisycount > OVERSENSITIVE: 
                self.tap_threshold *= 1.1  
            #if 1 <= self.noisycount <= MAX_TAP_BLOCKS: 
             #   self.noisycount = 0
            return True
        else: 

            if 1 <= self.noisycount <= MAX_TAP_BLOCKS: 
                self.noisycount = 0
                return True 
            
            self.noisycount = 0 
            self.quietcount += 1
            if self.quietcount > UNDERSENSITIVE: 
                self.tap_threshold *= 0.9

        return False
  
    def listen(self):
        """

        """ 
            
        data = None
        start_listen = datetime.datetime.now()

        _val = self.nerves.get("ongoing_conversation")  
        if _val != "":    
           return False , ""
                
        while True:
    
            try:
            
                result_text = ""
                q = queue.Queue()
                i_pauses = 0
                with sd.RawInputStream(
                    dtype='int16',
                    channels=1,
                    callback=lambda in_data, frames, time, status: record_callback(
                        in_data,
                        frames,
                        time,
                        status,
                        q
                    )
                ):
                    
                    # Collect audio data until we have a full phrase

                    _val = self.nerves.get("ongoing_conversation")  
                    if _val != "":    
                           return False , ""
                    
                    b_detected,  _val = self.nerves.pop("ignore_speech")  
                    if _val != "":    
                           return False , ""
                    
                    while True:
                        data = q.get()  
     
                        
                        if self.stt_recognizer.AcceptWaveform(data):
        
                            # Perform speech-to-text (STT) on the audio data
                            result = json.loads(self.stt_recognizer.Result())
                            result_text = result.get("text", "")
                            break

            except  Exception as e:
                print(str(e))
                t = open("speach_sound.log", "a")
                t.write(str(e) + "\n")
                t.close()
                         
            _val = self.nerves.get("speach_start")  
            if _val != "":   
                 start_convo =    datetime.datetime.strptime(_val, '%Y-%m-%d %H:%M:%S.%f')
                 if start_convo  >= start_listen:
                     return False , ""
            
            # Send the user's message to the LLM server
            if not result_text or result_text == "huh" or result_text == "": 

                if data is None:
                     return False , ""
                elif self.detect_noise(data):
                    return True , "<NOISE>" 
                else:
                    return False , ""
            else: 
                return True,  result_text 
     
    def serve_forever(self): 
        """
        
        """
        print("listening...")
        while True: 
           
           detected , dialog = self.listen() 
           if detected:    
            
                if self.log:
                    f_log = open(self.config.LOGS_PATH + "speech_vosk.log", "a")
                    f_log.write("### Detected       #####\n")
                    f_log.write(str(detected) + "\n")  
                    f_log.write("### dialog    #####\n")
                    f_log.write(dialog.replace("`","") + "\n")  

                if self.debug: 
                      self._cnt  += 1 
                      current_time = datetime.datetime.now() 
                      s_out = self.sense + " " + str( self._cnt ) + " " + str(dialog)  + "  " + str(current_time)
                   #   print("\r" + s_out, end= "")
                      print(  s_out )
 
               # found, prior_val  = self.nerves.pop("speech")  ##TDH changed from ge  
               # prior_val  = self.nerves.get(self.sense)  ##TDH changed from ge  
               # communicated, _val = False, ""# self.nerves.pop("communication_complete") 

                if dialog not in ["", "<NOISE>"]:  

                   # if prior_val != "" and communicated is False:
                    #    dialog = prior_val   + " " + dialog.strip() 
                    if 1 ==5:
                        _t = open("are_we_hearing_repeats.log", "a")
                        _t.write(dialog + "\n")
                        _t.close()
                    self.nerves.set(self.sense, dialog)  
                   # time.sleep(.5)

                elif  dialog == "<NOISE>": 
                    self.nerves.set("noise", dialog)  
                else: 
                    self.nerves.set("sound", "<HEARTBEAT>")   
           else: 
                self.nerves.set("sound", "<HEARTBEAT>")  
 
           time.sleep(self.polling_rate)
           self.counter = self.counter + 1

if __name__ == "__main__":
    """ 
     python3  speech_sound.py -r number_2 -m test
    
    """
    import os, sys
    os.chdir('../')
    sys.path.insert(0, os.path.abspath('./')) 
    import config
    from communication.nerves         import Nerves  

    args    = parser.parse_args()  
    mode    = args.mode 
    robot   = args.robot   
   # args    = json.loads(args.args  ) 

    with open( config.DATA_PATH  + robot + "/settings.json") as f:
        data = ''
        for row in f:
           data += row  

    settings = json.loads(data)

    nerves     = Nerves(robot) 

    args =  parser.parse_args() 

    mode    = args.mode 
    robot   = args.robot    
 
    sndspeach  = SpeechSound(robot, nerves, config, settings )
    if mode == "serve":
        sndspeach.serve_forever()

    elif mode =="test":
        sndspeach.debug  = True
        sndspeach.serve_forever()
