from pyparsing import *

NNPS = Literal('NNPS')
NNP = Literal('NNP')
NNS = Literal('NNS')
NN = Literal('NN')

VDB = Literal('VDB')
VBG = Literal('VBG')
VBN = Literal('VBN')
VBP = Literal('VBP')
VBZ = Literal('VBZ')
VB = Literal('VB')

JJ = Literal('JJ')
RB = Literal('RB')
RBR = Literal('RBR')
RBS = Literal('RBS') 

DT = Literal('DT')
AND = Literal('AND')
OF = Literal('OF')
POS = Literal('POS')

NOUN = Group(OneOrMore(NNPS|NNP|NNS|NN))
#PROPER_NOUN = Group(OneOrMore(NNP|NNPS))
VERB = OneOrMore(VDB|VBG|VBN|VBP|VBZ|VB)
ADJECTIVE = OneOrMore(JJ)
ADVERB = OneOrMore(RB)

ARTICLE_NOUN = Group(DT + NOUN)
ADJECTIVE_NOUN = Group(ADJECTIVE + NOUN)
VERB_NOUN = Group(VERB + NOUN)
POS_NOUN = Group((ARTICLE_NOUN | NOUN) + POS + (ADJECTIVE_NOUN | VERB_NOUN | NOUN)) 
ARTICLE_ADJECTIVE_NOUN = Group(DT + ADJECTIVE_NOUN)
NOUN_AND_NOUN = Group((NOUN | ARTICLE_NOUN) + AND + (POS_NOUN | ARTICLE_NOUN | NOUN))
NOUN_OF_NOUN = Group((NOUN_AND_NOUN | ARTICLE_NOUN | ARTICLE_NOUN) + OF + (NOUN_AND_NOUN | ARTICLE_NOUN | NOUN))

#TODO
expr = Forward()
expr << (POS_NOUN)

result = expr.parseString('DTNNPOSNN')
print result.asList()