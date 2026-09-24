


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

    res = triples.access("context", "emotion")
    print(res)

    res = triples.define("definitions", "happy")
    print(res)
 