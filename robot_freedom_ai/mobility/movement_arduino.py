#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name 
#https://www.aranacorp.com/en/serial-communication-between-raspberry-pi-and-arduino/

import serial,time, queue
import threading 

try:
   from .sequences import RESETS, FLIPS
except:
   from sequences import RESETS ,FLIPS

arduino = None
arduinoThread = None
arduinoQueue = queue.Queue() 
agentQueue = queue.Queue()
waitingMessages = queue.Queue()


def listenToArduino():
    global arduino 
    message = b''
    while True:
        incoming = arduino.read()
        if incoming == b'\n':
            try:
                arduinoQueue.put(message.decode('utf-8').strip() )
             
            except UnicodeDecodeError as e:
                # Handle the error: log it, ignore the message, or take other action
                print(f"UnicodeDecodeError: {e}. Message skipped.")
            message = b''
        else:
            if incoming not in (b'', b'\r'):
                message += incoming 

class MOVEMENT(object):

    def __init__(self, default_device, config, strict=True):
        """
        
        """
        self.config  = config
        self.strict  = strict
        self.connections = {}
        self.default_device   = default_device

    def reset(self):    
        """
        
        """
        res = {}
        for cmd in RESETS:
            res[cmd] = True
            self.write(cmd)
        return res 
    
    def connect_to_devices(self,  devices):
       """

       """ 
       self.connected = False
       self.devices   = devices
       self.port      = "-1"
       self.baud      = "-1"

       global arduino 
       global arduinoThread 

       if "RF.Movement" not in self.devices:
           print("No devices found!")
           self.connected = False 
       try:
           port , baud =  self.devices["RF.Movement"]  
           arduino = serial.Serial(port, baudrate=baud, timeout=.1)
           arduinoThread = threading.Thread(target=listenToArduino, args=())
           arduinoThread.daemon = True
           arduinoThread.start() 
           self.connected = True
           self.port     = port
           self.baud     = baud 
           print("Connected to RF.Movement") 
       except: 
           print("failed to connect RF.Movement") 
             
       return self.connected
    
    def write(self, cmd, device = None): 
        """
 
        """  
        global arduino
        if self.connected is False:
             return {}
        agentQueue.put(cmd)

        if arduinoQueue.empty(): 
            cmd = agentQueue.get().encode('utf-8')  
            try:
                arduino.write(cmd)
                arduino.write(bytes('\n', encoding='utf-8')) 
            except:
                time.sleep(.5)
                port , baud =  self.devices["RF.Movement"]  
                arduino = serial.Serial(port, baudrate=baud, timeout=.1)
                time.sleep(.5)
                arduino.write(cmd)
                arduino.write(bytes('\n', encoding='utf-8'))

        try:
            reply = arduinoQueue.get(timeout =1) 
        except:
            reply = ""

        return reply
      
    
    def write_read(self, cmd, device = None): 
        """
 
        """  
        reply = None 
        arduino.write(cmd.encode('utf-8'))
        arduino.write(bytes('\n', encoding='utf-8')) 

        reply = arduinoQueue.get(timeout=5) 

        return reply
    
        
    def run(self, test=False):  
            try:
                while True:
                    cmd = input("Enter command : ") 
                    cmd = cmd.strip()
                    if test:

                        t = self.write_read(cmd )
                        print(t)
                    else:
                        self.write(cmd )
                    time.sleep(0.05) #wait for arduino to answer 
            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")

if __name__ == '__main__':
     
    name = "test"
    controller = MOVEMENT(name, {})   

    import os, sys
 
    os.chdir('../')
    sys.path.insert(0, os.path.abspath('./'))  
    from devices.tools       import scan_serial_ports  

    for i in range(10):
        rf_devs  = scan_serial_ports()   
        if controller.connect_to_devices(rf_devs) :
           break 
    
    for p in RESETS: 
       print("m p " + p  + ";" )
       answer = controller.write_read("m p " + p  + ";"  ) 
       print(answer)   

    for p in RESETS: 
       _p = FLIPS[p]
       print("m p " + _p  + ";" )
       answer = controller.write_read("m p " + _p  + ";"  ) 
       print(answer)   

    for cmd in ['5','0']: 
       print("e v " + cmd  + ";" )
       answer = controller.write_read("e v " + cmd  + ";"  ) 
       print(answer)  
       time.sleep(.5)  

    controller.run(True)