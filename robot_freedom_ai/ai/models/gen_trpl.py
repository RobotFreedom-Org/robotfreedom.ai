

#pkgutil --expand macOSUpd10.13.2.pkg High_Sierra
#pkgutil --flatten High_Sierra High_Sierra.pkg 
# sudo /Applications/Install\ macOS\ High\ Sierra.app/Contents/Resources/createinstallmedia --volume /dev/disk4
  
from os.path import abspath, dirname, exists    
import json    
 
def process_dialogue(trpl, folder,filename, db):
    import os
    try:
       os.mkdir(folder + "/" + db)
    except:
       pass

    ent            = open(folder + "/" + db +   "/entity2id.txt", "w")     
    relate         = open(folder + "/" + db +   "/relation2id.txt", "w")     
    gt2id          = open(folder + "/" + db +   "/gt2id.txt", "w")         
    question2id    = open(folder + "/" + db +   "/question2id.txt", "w")         
    query2id       = open(folder + "/" + db +   "/query2id.txt", "w")  

    ent.write("\n")   
    relate.write("\n")   
    gt2id.write("\n")   
    question2id.write("\n")   
    query2id.write("\n")   

    ents       = {}
    relation   = {}
    questions  = {} 

    triples = open(folder + "/" + filename)  
   
    for i, line in enumerate(triples):
      if i > 120:
        
        row = json.loads(line.strip()) 

        print(row)
        svo_q = trpl.triple_inference([row["prompt"]]) 
        svo   = trpl.triple_inference([row["completion"]])

        
        if svo["v"] == "" or  svo["o"] == "" or svo["s"] == "":
              continue   
        if svo_q["v"] == "" or  svo_q["o"] == "" or svo_q["s"] == "":
               continue 
     
        if svo_q["s"] in ents:
           s_id_q = ents[svo_q["s"] ]
        else:
           s_id_q = len(ents)
           ents[svo_q["s"]] = s_id_q
           ent.write(svo_q["s"] + "\t" + str(s_id_q) + "\n")
      
        if svo_q["v"] in questions:
            v_id_q = questions[svo_q["v"]]
        else:
            v_id_q = len(questions)
            questions[svo_q["v"]] = v_id_q 
            question2id.write(svo_q["v"] + "\t" + str(v_id_q) + "\n")
      
        if svo_q["o"] in ents:
           o_id_q =  ents[svo_q["o"]]
        else:
           o_id_q = len(ents)
           ents[svo_q["o"]] = o_id_q   
           ent.write(svo_q["o"] +"\t" + str(o_id_q) + "\n") 

        
        if svo["s"] in ents:
           s_id =  ents[svo["s"]] 
        else:
           s_id = len(ents)
           ents[svo["s"]] = s_id
           ent.write(svo["s"]+ "\t" + str(s_id) + "\n")
       
        if svo["v"] in relation:
           v_id = relation[svo["v"]]
        else:
           v_id = len(relation)
           relation[svo["v"]] = v_id 
           relate.write(svo["v"] +"\t" + str(v_id) + "\n")
       
        if svo["o"] in ents:
           o_id = ents[svo["o"]]
        else:
           o_id = len(ents)
           ents[svo["o"]] = o_id    
           ent.write(svo["o"] +"\t" + str(o_id) + "\n")
 
        
       # print((str(s_id) + " " + str(v_id) + " " + str(o_id) + "\n")   )

        gt2id.write(str(s_id) + " " + str(o_id) + " " + str(v_id) + "\n")    
        query2id.write(str(s_id_q) + " " + str(o_id_q) + " " + str(v_id_q) + "\n") 


if __name__ == '__main__': 
     """
     
     """
     import os, sys
     os.chdir('../../')
     sys.path.insert(0, os.path.abspath('./')) 
     import config  
     from ai.models.triples_parser.inference_bayes_triples  import TriplesParser
 
     trpl = TriplesParser(config)
     trpl.load()
     process_dialogue(trpl, "../data/chat", "norm_convo.json", "convo")
     process_dialogue(trpl, "../data/chat", "facts.json", "facts")

