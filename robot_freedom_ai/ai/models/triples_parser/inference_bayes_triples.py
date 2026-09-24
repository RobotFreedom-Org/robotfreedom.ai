
import re     
from nltk import pos_tag, word_tokenize, RegexpParser
from nltk.tree import Tree  
 
def svo_components(sentence, tagged):
    """
    Extract Subject, Verb, Object, Object Complement, and Modifiers from a sentence.
    This is a heuristic approach using POS tagging and chunking.
 
    """
    # Tokenize and POS-tag
    sentence = sentence.strip()
    sentence = sentence[0].upper() + sentence[1:]

    if sentence[-1] not in ['.', '!', '?']:
         sentence += "."
 

    # Define a chunk grammar for NP (noun phrase), VP (verb phrase), PP (prepositional phrase)
    grammar = r"""
        NP: {<DT|PRP\$>?<JJ.*>*<NN.*>+}   # Noun phrase
        VP: {<VB.*><NP|PP|CLAUSE>+$}      # Verb phrase
        PP: {<IN><NP>}                    # Prepositional phrase
        CLAUSE: {<NP><VP>}                # Clause
    """

    cp = RegexpParser(grammar)
    tree = cp.parse(tagged)

    subject = verb = obj = obj_comp = modifiers = 'na'
    res = {"s":"", "v":"", "o":"", "m":"", "oc":""}

    def extract(res, label, words): 
        #print (res, label, words)
        if label in ["NP" , "PRP", "NNS"] and res["s"]  == "":
              res["s"] = words.lower()

        elif label in ["VP"] and res["v"]   == "":
                # First word in VP is usually the main verb
                res["v"] = subtree.leaves()[0][0].lower()
                # Remaining words might be object or complement
                rest = " ".join(w for w, t in subtree.leaves()[1:])
                if rest:
                    res["0"] = rest  
        elif label in ( "VBZ", "VBP", 'VBD', 'VBG', 'VBN', 'IN'):
                res["v"] = words 

        elif label in ( "NNS", "NP", "PRP", 'MD', 'NN', 'NNP', 'NNPS'):
                res["o"] = words 

        elif label in ("PP", "JJ"):
                if res["m"]  == "":
                    res["m"] = words.lower()
        return res 
    # Heuristic extraction 
    for subtree in tree: 

        if isinstance(subtree, Tree):  
            #label = subtree.label()
           # words = " ".join(word for word, tag in subtree.leaves()) 
            for sub in subtree: 
               if len(sub) == 2:
                   word, label = sub 
               else: 
                   word, label = sub[0] 

               extract(res, label, word)
            
        else: 
            word, label = subtree 
            extract(res, label, word)   

    # Simple heuristic for object complement (adjective or noun after object)
    if obj:
        obj_tokens = word_tokenize(obj)
        obj_tags = pos_tag(obj_tokens)
        if len(obj_tags) > 1 and obj_tags[-1][1] in ("JJ", "NN", "NNS"):
            res["oc"] = obj_tags[-1][0]
 
    return res


def get_svo (sentence):
    tokens    = word_tokenize(sentence)  
    tags      = pos_tag(  tokens)
    tags_lkup = {k:v for k, v in tags}    
    svo       = svo_components(sentence, tags )  
    return svo
  
class TriplesParser():


    def __init__(self, config):
          self.config = config
          self.knowledge_base = {} 

    def load(self): 


        self.LOOKUP_BASE = {"CC": 1,
          "CD":    2,
          "DT":    3,
          "EX":    4,
          "IN":    5,
          "JJ":    6,
          "JJR":   7,
          "JJS":   8,
          "LS":    9,
          "MD":    10,
          "NN":    11 ,
          "NNP":   12 ,
          "NNS":   13 ,
          "PDT":   14 ,
          "POS":   15 ,
          "PRP":   16 ,
          "PRP$":  17 ,
          "RB":    18 ,
          "RBR":   19 ,
          "RBS":   20 ,
          "RP":    21 ,
          "TO":    22 ,
          "UH":    23 ,
          "VB":    24 ,
          "VBD":   25 ,
          "VBG":   26 ,
          "VBN":   27 ,
          "VBP":   28 ,
          "VBZ":   29 ,
          "WDT":   30 ,
          "WP":    31 ,
          "WRB":   32 ,
          "WDT":   33 ,
          "NNPS":  34 ,
          "FW":    35 ,
          "WP$":   36 , 
          "PUNCT": 37 ,
          "SYM":   38 ,
          ":":     39,
          "$":     40}  

        self.LOOKUP_STATS=   {"DT": 36945.0, "JJ": 13286.0, "NN": 69552.0, "VBZ": 22128.0,
           "TO": 14058.0, "VB": 11748.0, "IN": 23292.0, "CC": 3347.0, 
           "NNP": 34833.0, "VBD": 35497.0, "PRP$": 13440.0, "NNS": 13283.0, 
           "VBG": 6358.0, "PRP": 15991.0, "RB": 7003.0, "POS": 5012.0, 
           "WRB": 548.0, "VBP": 6501.0, "RP": 3200.0, "VBN": 3446.0, 
           "EX": 261.0, "JJR": 221.0, "CD": 1142.0, "MD": 1055.0, 
           "JJS": 204.0, "PUNCT": 121.0, "PDT": 116.0, "RBR": 99.0, 
           "WP": 232.0, "WDT": 137.0, "FW": 3000, 
           "NNPS": 16.0, "RBS": 16.0, "WP$": 1.0, "UH": 1.0 ,
           "SYM": 1.0 , ":": 1.0 , "$": 1.0 }
 
 
        self._LOOKUP = {key: value for key, value in sorted(self.LOOKUP_BASE.items(), key=lambda item: item[1])}

        self.LOOKUP = {} 
        i = 1
        for key, val in  self._LOOKUP.items():  
           if val > 1:
               self.LOOKUP[key] = i 
           else:
               self.LOOKUP[key] = len(self._LOOKUP)
           i += 1

    
    
    def remove_periods_from_abbreviations(self, text):
        """
        Removes periods from abbreviations (e.g., U.S.A. -> USA)
        without affecting normal sentence punctuation.
        """ 
    
        # Pattern explanation:
        # \b           → word boundary
        # (?:[A-Z]\.)+ → one or more occurrences of 'capital letter + period'
        # (?=\b)       → ensure it ends at a word boundary
        pattern = r'\b(?:[A-Z]\.)+(?=\b)'
    
        def replacer(match):
            # Remove all periods from the matched abbreviation
            return match.group(0).replace('.', '')
    
        return re.sub(pattern, replacer, text)

    def fix_abrev(self, text):
    
        if text.startswith("u "):
            text = "you " + text[1:]
        if text.endswith(" u"):
            text =  text[ :-1] + "you"
    
        if text.endswith(".") or text.endswith("?")  or text.endswith("!") :
            text =  text[ :-1] 
    
        text = text.replace("'s ", " is ")
        text = text.replace(" s ", " is ")
        text = text.replace(" r ", " are ")
        text = text.replace(" u ", " you ")
        text = text.replace(" ru ", " are you ")
        text = text.replace(" m ", " am ")
        text = text.replace("'m ", " am ")
        text = text.replace("im ", " I am ")
        text = text.replace("'s", '')
        text = text.replace("'ar", ' are ')
        text = text.replace("'ll", ' will ')
        text = text.replace("&", ' and ') 
        return text

    
    def clean_txt(self, sentence):
    
    
        string_encoded = sentence.encode("ascii", "ignore")
        sentence = string_encoded.decode()
        sentence = self.remove_periods_from_abbreviations(sentence)
        sentence = sentence.replace('\t', ' ')
        sentence = sentence.replace('\n', ' ') 
        sentence = sentence.replace('km.', 'km')
        sentence = sentence.replace('sq.', 'sq') 
        sentence = sentence.replace('"', ' ')
        sentence = sentence.replace('/', ' ')
        sentence = sentence.replace("'", ' ')
        sentence = sentence.replace(".", ' ')
        sentence = sentence.replace("?", ' ')
        sentence = sentence.replace("!", ' ')
        sentence = self.fix_abrev(sentence)
        sentence = " ".join(sentence.split()) 
    
        return  sentence.lower()
 

    def gen_feature_stats(self,sentence):
        pass


    def parts(self, sentence, verbose =False):
        """
        Extract subject-predicate-object triples from a sentence using spaCy's dependency parser.
        """ 
        out  = []
        tags = [ ] 
        toks = [0 for v in range(30)] 
    
        tokens = word_tokenize(sentence)
        tagged_tokens = pos_tag(tokens)  
        i   = 0 
        for word, tag in tagged_tokens:   
     
            if word in ["yes", "no", "maybe"]:
                tag = "UH"
            #   print("tagger ", word, tag)  
            if tag in self.LOOKUP:
                out.append(word)
                tags.append(tag)
                if i < len(toks):
                    toks[i]  = self.LOOKUP[tag] 
                    #print(tag, LOOKUP)
                i += 1   

            elif word in [".","(", ")", ",", "$", "`", ",","'", "#", "!", ";", "-", "?", "''","||"]:   
                pass
            else:
                print("tagger", word, tag) 

        return [out, tags , toks] 
        
    
    def get_implied_svo(self, sentence):

           svo = {"s":"",
                  "v":"",
                  "o":""}
             

           sentences = sentence.split(" ")    
           for i in range(0,len(sentences)):
               if sentences[i] in self.knowledge_base.adj_list["v_s"]:
                   svo["v"] = sentences[i] 
               if i < len(sentences)-1:
                  ngram =  sentences[i] + " " + sentences[i+1]
                  if ngram in self.knowledge_base.adj_list["v_s"]:
                       svo["v"] = ngram

           if svo["v"] != "":
              sentence = sentence.replace(svo["v"], "")

           sentences = sentence.split(" ")    
           for i in range(0,len(sentences)):
               if sentences[i] in  self.knowledge_base.adj_list["o_s"]:
                   svo["o"] = sentences[i] 
               if i < len(sentences)-1:
                  ngram =  sentences[i]  + " " + sentences[i+1]
                  if ngram in  self.knowledge_base.adj_list["o_s"]:
                       svo["o"] = ngram

           if svo["o"] != "":
              sentence = sentence.replace(svo["o"], "")

           sentences = sentence.split(" ")    
           for i in range(0,len(sentences)):
               if sentences[i] in self.knowledge_base.adj_list["s_v"]:
                   svo["s"] = sentences[i] 
               if i < len(sentences)-1:
                  ngram =  sentences[i] + " " +  sentences[i+1]
                  if ngram in self.knowledge_base.adj_list["s_v"]:
                       svo["s"] = ngram
 
           
           return svo
    
    def triple_inference(self, sentences):


           sentence = sentences[0] 
           implied  = self.get_implied_svo(sentence)
           prior    =  get_svo(sentence)

           fin = {"s":prior["s"],
                  "v":prior["v"],
                  "o":prior["o"]}
           
           if fin["s"] == "":
              fin["s"] == prior["m"]

           elif fin["o"] == "":
              fin["o"] == prior["m"]

           #print(implied, fin)

           if fin["s"] == "" and fin["v"] == "" and fin["o"] == "":
               if implied["s"] != "" or implied["v"] != "" or implied["o"] != "":
                 fin =  implied

           return fin  
     
if __name__ == '__main__':
    
        import csv  
          
        # print()
    
      