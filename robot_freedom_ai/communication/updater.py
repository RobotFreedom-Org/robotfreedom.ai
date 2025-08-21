#!/usr/bin/python
# -*- coding: utf-8 -*- 

"""
Description:  
Author: HipMonsters.com 
License: MIT License
""" 

import os  


class Updater(object):
     
     def __init__(self,ipaddr ):
          """
          
          """
          self.ipaddr = ipaddr
 

     def update(self, stype ):
          """
          """
          if stype == "code":
              cmds = """ 
curl %s/updates/code/ --output updates.zip

unzip -o updates.zip

rm updates.zip
""" % self.ipaddr  
 
          elif stype == "settings":
              cmds = """ 
cd ../settings

curl %s/updates/data/ --output settings.zip
  
unzip -o settings.zip

rm settings.zip
""" % self.ipaddr  

          os.system(cmds)

if __name__ == "__main__":
     NET_CONFIG = {}
     NET_CONFIG["robots"]    = {}
     NET_CONFIG["hubs"]        = {"192.168.1.72":"number_b"}
     NET_CONFIG["repositories"]= {"192.168.1.10": "number_a"}

     ips =  NET_CONFIG["repositories"]
     ip =  list(ips.keys())[0] 
     updater = Updater(ip+":8000")
     print(updater)
     updater.update("code")