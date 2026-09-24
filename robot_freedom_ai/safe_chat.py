import sys
import termios
import tty
from typing import Callable
import curses

 
from triples.triples     import Triples
from communication.nerves         import Nerves 
import config  
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--robot" , type=str,      default='', required=False)     

bad_words = []

#import pyautogui
# pip install PyAutoGUI
import os
# 

# Get the console window title
console_title = os.get_terminal_size().columns

#print(dir(pyautogui))
                        
#console_window = pyautogui.getWindowsWithTitle(console_title)[0] 


robot  = "number_3"
nerves = Nerves(robot)

import string

def contains_allowed_chars(s):
    allowed_punctuation = ['?','!', ",", ".", " "]
    return all(char.isalnum() or char in allowed_punctuation for char in s)


triples  = Triples(agent= robot, 
                   config=  config,
                   communication=None,
                   nerves= nerves,
                   client=True)   
 

with open("../data/lib/badwords.txt") as f:
    for line in f:
        if line.strip() not in ["hell", "ass", "M"]:
            bad_words.append(line.strip())

def main():
 #   console_window.activate()  # Bring the window to the front and focus it
   
    hinput("prompt: ", on_char)
    return 0 

def on_char(ch: str, line: str) -> bool:
    """
    
    """
    tmp = line+ch

    if tmp == 'go to sleep':
        sys.stdout.write('p\n')
        sys.stdout.write('Bye Bye\n')
        sys.stdout.flush()
        return True, ""
    
    _t = tmp.split(" ")[-1]
    if _t.lower() in bad_words:
        sys.stdout.write("*")
        sys.stdout.flush()
        return False, "*"
    
    return False, ch

"""
import pygetwindow as gw

win = gw.getWindowsWithTitle('Photoshop')[0]

win.focus()
"""

def hinput(prompt: str=None, hook: Callable[[str,str], bool]=None) -> str:
    """input with a hook for char-by-char processing."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    inpt = ""
    b_responded = False

    sys.stdout.write("\033[2J\033[H") 
    val = triples.clear_messages("chat_responses_2")


    while True:


        sys.stdout.write('\r') 
        if prompt is not None:
            sys.stdout.write(prompt)
        sys.stdout.write(inpt)
        sys.stdout.flush()
            
        ch = None

        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

        #if hook is not None and hook(ch, inpt):
        #    break
        b_exit, ch  = hook(ch, inpt)
        if b_exit:
            break  

        if  ord(ch)  in [0x1B,0x4B, 0xcb]: #left
            if len(inpt) > 0:
                sys.stdout.write('\b \b')
                inpt = inpt[:-1]
            continue
        elif ord(ch) in [0x1A, 0x4D]: #roight
            continue  
        elif ord(ch) ==  [0x19,0x50 ]: #down
            continue 
        elif ord(ch) == [0x1B,0x48 ]: #up
            continue

        if ord(ch) == 0x7f: #BACKSPACE
            if len(inpt) > 0:
                sys.stdout.write('\b \b')
                inpt = inpt[:-1]
            continue

        if ord(ch) == 0x0d: #ENTER
            sys.stdout.write('\n')

            val = triples.do_direct_chat(inpt)
            val = val.replace("respond>", "response: ")
            p_response = val
            sys.stdout.write(val +"\n")
            sys.stdout.flush()
            # break
            ch = None
            inpt = ""
            b_responded = True  
        else:
          #  if ch.isprintable():
         #   if contains_allowed_chars(ch): 

                if  b_responded: 
                   b_responded = False  
                   sys.stdout.write("\033[2J\033[H")
                   sys.stdout.write(val +"\n")
                inpt += ch
            
    return inpt

if __name__ == '__main__':
    sys.exit(main())