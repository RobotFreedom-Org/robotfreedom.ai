 
replace_rules = {}   
replace_rules["hi"]     = "I give my greetings" 
replace_rules["hey"]    = "I give my greetings" 
replace_rules["hello"]  = "I give my greetings" 
replace_rules["howdy"]  = "I give my greetings" 

class TriplePreParser(object):

    def __init__(self):
        
         self.verbose = False

    def parse(self, text): 
        fin = []
        for word in text.lower().split():
            for key, val in replace_rules.items():
                 if word == key: 
                     word = val
                     break 
            word =  word 

            word = ' '.join(word)
            fin.append(word)   
         
        questions = ["why", "what", "where", "when", "who", "how"] 
        if self.verbose:
            print(fin)
        q = [1 for key in fin if key in questions]

        if len(fin) < 3 and 5==6:
            print(fin)
            dfb
            if fin[-1] not in("?",".","!"):
               fin.append("is")
            else:
               fin =fin[:-1] + ["is"] + fin[-1]

        text = " ".join(fin)
        if self.verbose:
            print(q)
        if len(q) > 0 and text[-1] != "?":
            if text[-1] in (".", "!"):
                text[-1] = "?"
            else:
                text += "?"  
        return text
    


if __name__ == "__main__": 
        
        tripe_pre_parser = TriplePreParser()

        for text in ["hi", "how are you", "lets go fishing", "where is the city's central area"]:
            print(text)
            res = tripe_pre_parser.parse(text)
            print(res)