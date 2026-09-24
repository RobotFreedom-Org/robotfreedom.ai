#!/usr/bin/python
# -*- coding: utf-8 -*- 
""" 
Author: RobotFreedom.org  
License: MIT License  
""" 
 
from .utils.utils import dispatcher    
    
class  IdentityTriples(object):
 
    def __init__(self:object):
        """
        Identity Functions - Stub
        """   
        pass


    @dispatcher
    def idenity(self: object, in_subjects :str = "", in_objects: str ="" )-> int: 
        """CRUD for user identity"""
        if in_subjects == "add":
            self.security_identity.add( "user", "name", in_objects, prop={})

        return in_subjects

    @dispatcher
    def security(self: object, in_subjects :str = "", in_objects: str ="" )-> int: 
        """privilages management"""
        if in_subjects == "authorized":
            in_objects = in_objects.split("->")
            self.security_identity.add( "authorized", in_objects[0], in_objects[1] , prop={})

        return in_subjects
        
       

