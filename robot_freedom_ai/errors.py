# -*- coding: utf-8 -*-
"""
 
""" 

####    Libraries   ################
 
import traceback
ERRORCNT = 0

def handle_exceptions(f):
    def wrapper(*args, **kw):
        global ERRORCNT
        try:
            return f(*args, **kw)
        except Exception as e:
            self = args[0] 
            print("ERROR   ")
            print(e)   
            print(args)
            print(kw)
            print(traceback.format_exc()) 
            print("END ERROR ")  
            ERRORCNT = ERRORCNT+ 1
            raise
            stop
            #exception_handler(self.log, True)

    return wrapper 
     