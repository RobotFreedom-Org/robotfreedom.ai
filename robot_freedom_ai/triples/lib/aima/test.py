
import learning
import ast

from  learning import DecisionTree
s_cmd = ''

for line in open('C:/1m/opmesh/__plugins/aima/iris_dectree_mdl.1.json'):
    s_cmd = s_cmd + line

dec =  ast.literal_eval(s_cmd)
# print dec['dec_tree']


def todict(obj, param = None ):

    if len(obj) == 0:
        return DecisionTree(param[0], param[1], obj)

    elif isinstance(obj, dict):
        for k in obj.keys():
            if isinstance(obj[k], tuple):
                obj[k] = todict(obj[k] )

        return DecisionTree(param[0], param[1] ,obj)

    elif isinstance(obj, DecisionTree):

        return DecisionTree(param[0], param[1], obj)

    elif param != None:

        return DecisionTree(param[0], param[1], {})

    elif isinstance(obj, tuple):
        val1, val2, val3  = obj
        return todict(val3, (val1, val2 ) )
    else:
        return obj

todict(dec['dec_tree'] ).predict()

def to_dec_tree(obj ):

    if isinstance(obj, dict):
        for k, val in obj.items():
            yield to_dec_tree(val)

    elif isinstance(obj, tuple):
        yield to_dec_tree(obj[2])

    elif isinstance(obj, DecisionTree):
        yield  obj
    else:
        yield obj


def listChildren(self):
    yield self
    for child in self.children:
        for c in child.listChildren():
            yield c

import json

def json_to_obj(s):
    def h2o(x):
        if isinstance(x, dict):
            return type('jo', (), {k: h2o(v) for k, v in x.iteritems()})
        else:
            return x
    return h2o(json.loads(s))
 

def json_to_obj(s):
    def h2o(x):
        if isinstance(x, dict):
            return type('jo', (), {k: h2o(v) for k, v in x.iteritems()})
        else:
            return x
    return h2o(json.loads(s))

#def gen_tree( attr, attrname, branches=None):
#   if branches == None:
#       return attr, attrname,  DecisionTree(attr, attrname)
#
#   elif type(branches) == DecisionTree:
#       return attr, attrname,  DecisionTree(attr, attrname ,branches)
#
#   else:
#       attr_c  , attrname_c, branches_c =  branches
#       attr, attrname, branches  = gen_tree(attr_c, attrname_c, branches_c)
#
#attr  , attrname, branches =  dec['dec_tree']
#
#gen_tree(attr  , attrname, branches)
