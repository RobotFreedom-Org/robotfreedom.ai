#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name 
#https://www.aranacorp.com/en/serial-communication-between-raspberry-pi-and-arduino/

import serial,time,datetime
import threading, queue
import serial.tools.list_ports

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


class LOCOMOTION(object):

    def __init__(self, default_device,config, strict=True, b_test = False):
        """
        
        """
        self.i_test   = 0
        self.b_test   = b_test
        self.config  = config
        self.strict  = strict
        self.connections = {}
        self.default_device   = default_device
        self.last_move_time = datetime.datetime.now()

 
            
    def connect_to_devices(self,  devices):
       """
       
       """
       self.connected = False
       self.devices   = devices
       self.port      = "-1"
       self.baud      = "-1"

       global arduino 
       global arduinoThread  

       if "RF.Locomotion" not in self.devices:
           print("No devices found!")
           self.connected = False 

       try:
           port , baud =  self.devices["RF.Locomotion"]  
           arduino = serial.Serial(port, baudrate=baud, timeout=.1)
           arduinoThread = threading.Thread(target=listenToArduino, args=())
           arduinoThread.daemon = True
           arduinoThread.start() 
           self.connected = True
           self.port     = port
           self.baud     = baud 
           print("Connected to RF.Locomotion") 
       except: 
           print("failed to connect RF.Locomotion") 
             
       return self.connected
    
    def move(self, cmd, speed, wait_len, b_read = False): 
        """
 
        """  
        if cmd.endswith(";") is False:
            cmd = "move body " + cmd + ";"

        print("received",  cmd, speed, wait_len, self.b_test)
 
        if self.connected is False:
            self.i_test +=1
            if  self.b_test:
                import random 
                if random.randint(0,4) >= 2:
                    return 'BLOCKED'
                else:
                    return ' '
            else:
                return 'Not connected'
            
        reply =  self.write_read(cmd)

        return reply
    
 
    def write(self, cmd, device = None): 
        """
  
        """   
        global arduino
        if self.connected is False:
            return ""
        
        if cmd.endswith(";") is False:
            cmd = "move body " + cmd + ";"

        print("##########")
        print("executing " + cmd)
        print("##########")
        agentQueue.put(cmd)
 
        if arduinoQueue.empty(): 
            cmd = agentQueue.get().encode('utf-8')  
            try:
                arduino.write(cmd)
                arduino.write(bytes('\n', encoding='utf-8'))
            except:
                time.sleep(.5)
                port , baud =  self.devices["RF.Locomotion"]  
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
        if self.connected is False:
            return ""  
        
        if cmd.endswith(";") is False:
            cmd = "move body " + cmd + ";"
        reply = None 
        arduino.write(cmd.encode('utf-8'))
        arduino.write(bytes('\n', encoding='utf-8'))  
        reply = arduinoQueue.get(timeout=5)  
        return reply
    
        
    def run(self):
       
            try:
                while True:
                    cmd  =input("Enter command : ") 
                    cmd = cmd.strip()
                    res= self.move(cmd,1,1)
                    print(res)
                    time.sleep(0.05)  

            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")


if __name__ == '__main__':
      
    name = "test"
    controller = LOCOMOTION(name,{}) 

    import os, sys
    os.chdir('../')
    sys.path.insert(0, os.path.abspath('./'))  
    from devices.tools       import scan_serial_ports  
     
    rf_devs  = scan_serial_ports()  

    controller.connect_to_devices(rf_devs) 
   
    for cmd in ["r", "l", "b", "f", "c", "s"]:
       print(cmd)
       answer = controller.move(cmd, 1,1 ) 
       print(answer) 

    controller.run()