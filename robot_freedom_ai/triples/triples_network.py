#!/usr/bin/python
# -*- coding: utf-8 -*- 
""" 
Author: HipMonsters.com  
License: MIT License  
""" 

import json
 
try:
    from utils.utils import dispatcher  ,replace_sep, split_ignoring_quotes 
    from .. communication.network    import map_rf_ips_quick
    from .. devices.tools            import scan_serial_ports
    from .. devices.wearable_sync    import scan_for_ble

except:
    from .utils.utils import dispatcher  ,replace_sep, split_ignoring_quotes 
    from communication.network    import map_rf_ips_quick
    from devices.tools            import scan_serial_ports
    from devices.wearable_sync    import scan_for_ble

 
    
class  NetworkTriples(object):
 
    def __init__(self: object):
        """
        Functions for networked devices
        """   
        pass 
    
    
    @dispatcher
    def scan(self: object, in_subject:str= "", in_objects: str ="" )-> str: 
        """ Scans for networked devices """
        if in_subject == "ble":
           import asyncio 
           res = asyncio.run(  scan_for_ble())
           _res = [str(v[0]) + " " + v[2] for v in res] 
           res = "\n".join(_res)

        elif in_subject == "wifi":
           """pip install wifi""" 
           from communication.wifi_scanner import WiFiScanner
           scanner = WiFiScanner()
           _res = scanner.scan()
           print(_res) 
           res = "/n".join([d["SSID"]  + " " + d["Security"] + " " + d["Signal"] + " " + d["Quality"] for d in _res])

        elif in_subject == "serial":
           res = scan_serial_ports() 
           res = "\n".join([k + " " + v[0] + " "  + v[1] for k,v in res.items()])

        elif in_subject == "network": 
           _res =  map_rf_ips_quick()  
           res = "ROBOTS\n"
           res += "\n".join( [v + " " + k for k, v in _res["robots"].items()])
           res += "\nHUBS\n"
           res += "\n".join( [v + " " + k for k, v in _res["hubs"].items()])
           res += "\nREPOSITORIES\n"
           res += "\n".join( [v + " " + k for k, v in _res["repositories"].items()])

           print(_res)

        return res 

    
    @dispatcher
    def send(self: object, in_subject:str= "", in_objects: str ="" )-> str: 
        """ 
        Sends data to a network device
        """
        key , param = in_objects.split("|")
        self.communication.send(in_subject,  key + ":" +  param ) 
        return
    
    @dispatcher
    def check(self: object, in_subject:str= "", in_objects: str ="" )-> str: 
        """ 
        checks data on network device
        """
        key , param = in_subject.split("|")
        mess=  self.communication.check( )
        return mess
    
