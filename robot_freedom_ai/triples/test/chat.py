


if __name__ == '__main__': 
    """
     
    """
         
    import os, sys
    os.chdir('../../')
    sys.path.insert(0, os.path.abspath('./')) 
    import config
    from triples.core import Triples
    from memory.lt_memory import LTMemory
    from memory.st_memory import STMemory
    from communication.nerves import Nerves 

    s_robot       = "squirrel"
    nerves        = Nerves(s_robot) 
    triples       = Triples(agent=s_robot, 
                            config=  config,
                            communication=None,
                            nerves =nerves,
                            client=False)  

    st_mem        =  STMemory(s_robot, 
                              config, 
                              triples,
                              False) 
    
    lt_mem        =  LTMemory(s_robot, 
                              config, 
                              triples= triples, 
                              load_all=True) 


    
    triples.graphs["context"] = st_mem.memory["kb"]
    triples.graphs["definitions"] = lt_mem.memory["definitions"]
    triples.graphs["facts"] = lt_mem.memory["facts"]
    triples.graphs["moods"] = lt_mem.memory["moods"]
    triples.graphs["jokes"] = lt_mem.memory["jokes"] 
    triples.graphs["prior_conversations_base"]  =    lt_mem.memory["prior_conversations_base"]  
    triples.graphs["prior_conversations_rude"]  =    lt_mem.memory["prior_conversations_rude"]  

     
   # do one for  
   

    res = triples.define("word", "happy")
    print("api 1", res) 

    svo = {"s":"", "v":"", "o":"happy"}
    s_term  = svo["o"] 
    code = ""
    code += "define word "+ svo["o"] + "->research_1\n"
    code += "set v1\n"
    code += "flow if start\n" 
    code += "equal research_1 v1\n" 
    code += 'echo "explain ' +  s_term + '"\n'
    code += "flow if en;\n"  
    code += "flow if start"  
    code += "different research_1 v1\n"  
    code += "echo research_1\n" 
    code += "flow if end\n"    
    res = triples.run(code.split("\n"))
    print(" mood ", res)
 
    svo = {"s":"", "v":"", "o":"happy"}
    s_term  = svo["o"] 
    code = ""
    code += "define facts "+ svo["o"] + "->research_tmp\n"
    code += "element research_tmp 0 -> research_v\n"
    code += "element research_tmp 1 -> research_scr\n"
    code += "set v1 .3\n"
    code += "flow if start\n" 
    code += "less research_scr v1\n" 
    code += 'echo "explain ' +  s_term + '"\n'
    code += "flow if en;\n"  
    code += "flow if start"  
    code += "more research_scr v1\n"  
    code += "echo research_v\n" 
    code += "flow if end\n"    
    res = triples.run(code.split("\n"))
    print(" mood ", res)
 

    _question = "what you mean"
    _question = "why say"
    _question = "define"
    _question = "define"
    _question = "please  explain"
    svo = {"s":"", "v":"", "o":"happy"}
    s_term = svo["o"]
    for db in ["moods", "jokes", "word", "facts", "prior_conversations_base", "prior_conversations_rude"] :
        code = []
        code.append({"v":"define", "s":db , "o": s_term + "->research_tmp"} )
        code.append({"v":"element", "s":"research_tmp","o": "0 -> research_v"})
        code.append({"v":"element", "s":"research_tmp" ,"o": "1 -> research_scr"})
        code.append({"v":"set", "s":"v1" , "o": ".3"})
        code.append({"v":"flow", "s":"if" , "o": "start"})
        code.append({"v":"less", "s":"research_scr" , "o": "v1"})
        code.append({"v":"echo", "s": '"' + _question + " " + s_term + '"', "o":"" })
        code.append({"v":"flow", "s":"if" ,"o": "end"} )
        code.append({"v":"flow", "s":"if" , "o": "start"}  )
        code.append({"v":"more", "s":"research_scr" , "o": "v1"})
        code.append({"v":"echo", "s":"research_v", "o":""})
        code.append({"v":"flow", "s":"if" , "o": "end"}  )
        res = triples.run(code)
        print(db, " ", res)  
 
      

    #res = triples.access("context", "emotion")
    #print(res)

 
svo = {"s":"", "v":"", "o":"happy"}
s_term  = svo["o"] 
code = "" 
code += "set param1 1;\n"
code += "set param2 2;\n" 
code += "set v1 .3;\n"
code += "create function params\n"   
code += 'add param1 param2\n'  
code += "create function end\n"    
code += "execute params\n"    
res = triples.run(code.split("\n"))
print(" param function example ", res)
  