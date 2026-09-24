#!/usr/bin/python
# -*- coding: utf-8 -*- 

"""
Description:  
Author: HipMonsters.com 
License: MIT License
""" 
import urllib
import urllib.request
import os  
import json

from robot_freedom_ai.communication.network          import map_rf_ips_quick
from robot_freedom_ai.communication.network_scan     import scan


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
     NET_CONFIG["hubs"]        = {"192.168.1.72": "number_b"}
     NET_CONFIG["repositories"]= {"192.168.1.10": "number_a"}

     s_line = ""
     for line in open("./data/config/net_config.json"):
          s_line += line 
     NET_CONFIG = json.loads(s_line) 
     print(NET_CONFIG)

     ips =  NET_CONFIG["repositories"]
     ip =  list(ips.keys())[0]  
     try:  
            contents = urllib.request.urlopen("http://" + ip + ":8000/whois/", timeout=1.5).read()
            contents = str(contents, 'utf-8')   
     except KeyboardInterrupt:
            contents = ""  
             
     except:
            contents = "" 

     if contents.startswith("repository:") is False: 
          NET_CONFIG = scan()   
          b_found = False
          if "repositories" in  NET_CONFIG: 
             if len(NET_CONFIG["repositories"]) > 0:
                 f_out =  open("./data/config/net_config.json", "w")  
                 f_out.write(json.dumps(NET_CONFIG) )  
                 b_found = True

          if b_found is False:
             print("No repro found on network.")
             print("Make sure the repro is running.")
             print(NET_CONFIG)

     if len(NET_CONFIG["repositories"]) > 0:
         ips =  NET_CONFIG["repositories"]
         ip =  list(ips.keys())[0] 
         updater = Updater(ip+":8000") 
         print(updater)
         updater.update("code") 
         print("complete")