#!/usr/bin/python
# -*- coding: utf-8 -*- 
""" 
Author: HipMonsters.com  
License: MIT License  
""" 
 
import time  
import datetime     
from .utils.utils import dispatcher    


class DecisionTree:
    """A DecisionTree holds an attribute that is being tested, and a
    dict of {attrval: Tree} entries.  If Tree here is not a DecisionTree
    then it is the final classification of the example."""

    def __init__(self, attr, attrname=None, branches=None):
        self.attr     = None
        self.attrname = None
        self.branches = None
        "Initialize by saying what attribute this node tests."

        update(self, attr=attr, attrname=attrname or attr,
               branches=branches or {})

    def predict(self, example):

        "Given an example, use the tree to classify the example."
        ## Todo add logic for when vaule has not been seen before.

        if  self.attr  <  len(example):
            if example[self.attr] in  self.branches:
                child = self.branches[example[self.attr]]
                if isinstance(child, DecisionTree):
                    return child.predict(example)
                else:
                    return child
            else:
                favg = 0
                icnt = 0

                for key ,  child in self.branches.items():
                    if isinstance(child, DecisionTree) == False:
                        icnt = icnt +1
                        favg = favg + child

                if icnt == 0 :
                    return 0
                else:
                    return favg/icnt

        else:
            favg = 0
            icnt = 0

            for key ,  child in self.branches.items():
                if isinstance(child, DecisionTree) == False:
                    icnt = icnt +1
                    favg = favg + child

            if icnt == 0 :
                return 0
            else:
                return favg/icnt


    def add(self, val, subtree):
        "Add a branch.  If self.attr = val, go to the given subtree."
        self.branches[val] = subtree
        return self


    def display(self, indent=0):
        name = self.attrname
        print 'Test', name
        for (val, subtree) in self.branches.items():
            print ' '*4*indent, name, '=', val, '==>'
            if isinstance(subtree, DecisionTree):
                subtree.display(indent+1)
            else:
                print 'RESULT = ', subtree

    def display_array(self, indent = 0 , aout = None):
        if not  aout : aout = []
        name = self.attrname
        for (val, subtree) in self.branches.items():
            s1 = "%s %s %s %s %s"  % (' '*4*indent, name, '=', val, '==>')
            aout.append(s1  )
            if isinstance(subtree, DecisionTree):
                subtree.display_array(indent + 1 , )
            else:
                s2 = "%s %s"  % ('RESULT = ', subtree)
                aout.append(s2 )
        return aout

    def ret_branches(self):
        return  self.branches

    def ret_attrname(self):
        return  self.attrname

    def ret_attr(self):
        return  self.attr

    def __repr__(self):
        return '(%r, %r, %r)' % (
            self.attr, self.attrname, self.branches)
    
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
