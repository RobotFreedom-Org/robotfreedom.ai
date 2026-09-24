#!/usr/bin/python
# -*- coding: utf-8 -*- 
""" 
Author: HipMonsters.com  
License: MIT License  
""" 
 
import time  
import datetime     
from .utils.utils import dispatcher    


def words(text, reg=re.compile('[a-z0-9]+')):
    """Return a list of the words in text, ignoring punctuation and
    converting everything to lowercase (to canonicalize).
    >>> words("``EGAD!'' Edgar cried.")
    ['egad', 'edgar', 'cried']
    """
    return reg.findall(text.lower())

def canonicalize(text):
    """Return a canonical text: only lowercase letters and blanks.
    >>> canonicalize("``EGAD!'' Edgar cried.")
    'egad edgar cried'
    """
    return ' '.join(words(text))
    
def bigrams(text):
    """Return a list of pairs in text (a sequence of letters or words).
    >>> bigrams('this')
    ['th', 'hi', 'is']
    >>> bigrams(['this', 'is', 'a', 'test'])
    [['this', 'is'], ['is', 'a'], ['a', 'test']]
    """
    return [text[i:i+2] for i in range(len(text) - 1)]

class  TemporalTriples(object):
 
    def __init__(self:object):
        """
        Time and date functions
        """   
        pass
  
    @dispatcher          
    def datetime(self: object, in_subjects:str= "",in_objects: str ="" )-> str:
        """Return the current datetime """
        return  datetime.datetime.now()  
    
    @dispatcher
    def date(self: object, in_subjects:str= "",in_objects: str ="" )-> str:
        """Return current date in string format."""
 
        resp = "the date is " + datetime.datetime.now().strftime("%B %d %Y")
        return [resp] 
    
    @dispatcher
    def time(self: object, in_subjecst:str= "",in_objects: str ="" )-> str:
        """Return current time in string format."""
        resp = "the time is " + datetime.datetime.now().strftime("%H o clock and %M minutes")
        return [resp] 

    @dispatcher
    def temporal(self: object, in_subjects:str= "",in_objects: str ="" )-> str:
        """sleeps"""
        if in_subjects == "pause":
            time.sleep(1)
        return ""

alphabet = 'abcdefghijklmnopqrstuvwxyz'
     
def shift_encode(plaintext, n):
    """Encode text with a shift cipher that moves each letter up by n letters.
    >>> shift_encode('abc z', 1)
    'bcd a'
    """
    return encode(plaintext, alphabet[n:] + alphabet[:n])

def rot13(plaintext):
    """Encode text by rotating letters by 13 spaces in the alphabet.
    >>> rot13('hello')
    'uryyb'
    >>> rot13(rot13('hello'))
    'hello'
    """
    return shift_encode(plaintext, 13)

def encode(plaintext, code):
    "Encodes text, using a code which is a permutation of the alphabet."
    from string import maketrans
    trans = maketrans(alphabet + alphabet.upper(), code + code.upper())
    return plaintext.translate(trans)
