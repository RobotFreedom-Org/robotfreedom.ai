# -*- coding: utf-8 -*-
"""
Description: Sensor daemon for temperature and humidity.
Author: HipMonsters.com 
License: MIT License
https://www.electronicshub.org/raspberry-pi-dht11-humidity-temperature-sensor-interface/
"""
import json  
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
           
        if self.os == "LINUX":
            self.dhtDevice.trigger()
            try:
                temperature_c = self.dhtDevice.temperature
            except:
                return [False, "", ""]
            temperature_f = temperature_c * (9 / 5) + 32 
            try:
                 humidity      = self.dhtDevice.humidity
            except:
                return [False, "", ""]
            if self.debug:
              #  print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity))
                print("")
            if abs(temperature_f - self.start_temp) > 10: 
               self.start_temp =    temperature_f                      
               return [True ,temperature_f,  "temperature"]
            
            if abs(humidity - self.start_humid) > 10:       
               self.start_humid =    humidity       
               return [True , humidity, "humidity"]
            
        elif self.os == "OSX":
            
           if self.counter  >= self.args["max"]:
               self.counter = 0
               return [True, "timeout"]

        
        return [False, ""]
     


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
