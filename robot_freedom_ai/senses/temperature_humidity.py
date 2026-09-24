# -*- coding: utf-8 -*-
"""
Description: Sensor daemon for temperature and humidity.
Author: HipMonsters.com 
License: MIT License
https://www.electronicshub.org/raspberry-pi-dht11-humidity-temperature-sensor-interface/
"""
import json  
import time, datetime
try:
   from ._sense  import SenseBase
except:
   from _sense  import SenseBase

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode")  
parser.add_argument("-r", "--robot") 
parser.add_argument("-a", "--args")     
 

class  TemperatureHumidity(SenseBase):

    def __init__(self, robot, nerves, config, settings, pins ={"pin_1":26}):
        """
        http://thezanshow.com/electronics-tutorials/raspberry-pi/tutorial-26
        """
        super().__init__(robot, nerves, config, settings, "temperature_humidity") 
        self.args["max"] = 20
        self.pins = pins
        if self.os == "LINUX":
            import board
            import adafruit_dht 
            #pip install adafruit-circuitpython-dht
            self.dhtDevice = adafruit_dht.DHT22(board.D26)
          #  self.dhtDevice = adafruit_dht.DHT11(board.D26)
               
        self.sense_1 = "temperature" 
        self.sense_2 = "humidity"  
        self.sense_3 = "pressure"  
        self.sense_4 = "vox"  
        self.counter = 0
        self.start_temp = 0
        self.start_humid  = 0
            
    def poll(self):
        """
        """ 
        self.debug = True
        response = {}
        response["temperature"] = [False, 0.0]
        response["humidity"]    = [False, 0.0]
        if self.os == "LINUX":
            #self.dhtDevice.trigger()
            try:
                temperature_c = self.dhtDevice.temperature
            except:
                temperature_c = 32.0
            
            if temperature_c is None:
                temperature_c = 0
            temperature_f = temperature_c * (9 / 5) + 32 
             
            try:
                 humidity      = self.dhtDevice.humidity
            except:
                 humidity     = 0

            if humidity is None:
                humidity = 0

            if self.debug:
                print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity))
                

            if abs(temperature_f - self.start_temp) > 10: 
               self.start_temp =    temperature_f                      
               response["temperature"] = [True, temperature_f]  
            else:       
               response["temperature"] = [False,temperature_f]
            
            if abs(humidity - self.start_humid) > 10:       
               self.start_humid =    humidity       
               response["humidity"]    = [True, humidity]
            else:
               response["humidity"]    = [False, humidity]
            
        elif self.os == "OSX":
            
           if self.counter  >= self.args["max"]:
               self.counter            = 0
               response["temperature"] = [True, 10 ]
               response["humidity"]    = [True, 50 ]
               return response 
           
        return response
    
    def serve_forever(self): 
        """
        
        """
        if self.debug:
            print("Testing " + self.sense)

        while True:
           ret = self.poll()
           for sense in ["temperature", "humidity"]:
             detected, val   = ret[sense]
             self.nerves.set(sense + "_reading", str(val))  
             
             if detected: 
                 if self.debug:
                      self._cnt    += 1 
                      current_time  = datetime.datetime.now() 
                      s_out = self.sense + " " + str(self._cnt) + " " + str(ret) + " " +str(val)  + "  " + str(current_time)
                      print("\r" + s_out, end= "")  
                 self.nerves.set(sense, str(val))  

              #else:
               #   self.nerves.set(sense, str(val))  
                 
 
           self.counter = self.counter + 1
           time.sleep(self.polling_rate) 
 
if __name__ == "__main__":
    """ 
     python3  temperature_humidity.py -r number_2 -m test
    
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
 
    temperature_humidity  = TemperatureHumidity(robot, nerves, config, settings )
    if mode == "serve":
        temperature_humidity.serve_forever()

    elif mode =="test":
        temperature_humidity.debug  = True
        temperature_humidity.serve_forever()
