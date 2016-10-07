import spacy
from nltk.chunk.regexp import RegexpParser
import functools
from nltk.tree import Tree
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
##### This module is for parsing german text using Spacy####
# universal tags :ADJ, ADP, ADV, AUX, CONJ, DET, INTJ, NOUN, NUM, PART, PRON, PROPN, PUNCT, SCONJ, SYM, VERB, X, EOL, SPACE.

NP_GRAMMAR_SIMPLE = """
NP: {<CD>?((<JJ.*><CC>|<,>))*(<JJ.*>|<N.*>)+}
"""
# use this regular expression for the chunking to get the different related ADJs with NLTK!!
Np_GRAMMAR_SIMPLE_UNIVERSAL = """
NP : {((<ADJ>(<PUNCT>)*(<CONJ>)*)*(<ADJ>(<NOUN>|<PROPN>))+|(<NOUN><AUX><ADJ>((<PUNCT>)*(<CONJ>)*<ADJ>))+)}
"""

# old grammar
#Np_GRAMMAR_SIMPLE_UNIVERSAL = """
#NP : {((<ADJ.*><CONJ>|<,>))*(<ADJ.*>|<NOUN|PROPN>)+}
#"""


parser_smp = RegexpParser(Np_GRAMMAR_SIMPLE_UNIVERSAL)

NP_Noun_Simple = """NP: {(<NOUN|PROPN>)+}
"""
parser_NP = RegexpParser(NP_Noun_Simple)
NAMED_ENTITIES_TAGS = ["GPE", "PERSON", "ORGANIZATION", "LOCATION", "DATE", "TIME", "MONEY", "PERCENT", "FACILITY"]
lem = WordNetLemmatizer()

# need to change the named entity chunker to germna one !!!


def related_noun(chunk):
    tree = parser_NP.parse(chunk.leaves())
    for chunk in tree:
        if isinstance(chunk, Tree) and chunk.label() == 'NP':
            rchunk = nltk.ne_chunk(chunk.leaves())
            named_en = []
            for subchunk in rchunk:
                if isinstance(subchunk, Tree) and subchunk.label() in NAMED_ENTITIES_TAGS:
                    for word, tag in subchunk:
                        named_en.append(word)
                    yield functools.reduce(lambda x, y: x + ' ' + y, named_en).strip()
                else:
                    yield subchunk[0]

# Extracting Adj related to nouns from a sentence #


def get_adjs(tags):
    """
    chunked with simple grammar
    get all adjectives related to a Noun using the chunks and sub chunks
    :return: generator of dictionaries of {("NN","adj"),...}
    """
    noun_adj_sub_list = []
    tree = parser_smp.parse(tags)
    for subchunk in tree:
        if isinstance(subchunk, Tree) and subchunk.label() == 'NP':

            adjs = []
            for word, tag in subchunk:
                if tag == 'ADJ':
                    adjs.append(lem.lemmatize(word, 'a'))
                nouns = related_noun(subchunk)
                if nouns and adjs:
                    for adj in adjs:
                        for noun in nouns:
                           yield {"noun":noun,"adj":adj}
                    adjs = []


def get_related_noun(chunk):
    """
    this function is used to get the noun in the chunk if it is a named entity or a simple noun
    :param chunk:
    :return:
    """
    ent = []
    for i in chunk:
        if i.pos_ in ["NOUN","PROPN"]:
            if i.ent_type:
                ent.append(i.string)
            else:
                yield i.string
    if ent:
        yield functools.reduce(lambda x, y: x + ' ' + y,ent).strip()


def nouns_adj_spacy(doc):
    """
    using the noun_phrase chunked in spacy we get the chunk extract all related adj to the noun in the chunk
    :param doc:
    :return:
    """
    for chunk in doc.noun_chunks:
        adjs = []
        for i in chunk:
            if i.pos_ == 'ADJ':
                adjs.append(lem.lemmatize(i.string, 'a'))
        if adjs:
            for i in get_related_noun(chunk):
                for j in adjs:
                    yield {"noun": i, "adj": j}

# with NLTK
def nouns_list(sent):
    """tree chunked with NP_Noun_Simple chunker
    this function create a couple of nouns from a giving list with a sliding window of size 2
    :return:generator
    """
    #tokens = nltk.word_tokenize(sent)
    tree = parser_NP.parse(nltk.pos_tag(sent))
    nouns = []
    for chunk in tree:
        if isinstance(chunk, Tree) and chunk.label() == 'NP':
           rchunk = nltk.ne_chunk(chunk.leaves())
           named_en = []
           for subchunk in rchunk:
               if isinstance(subchunk, Tree) and subchunk.label() in NAMED_ENTITIES_TAGS:
                   for word, tag in subchunk:
                       named_en.append(word)
                   nouns.append((functools.reduce(lambda x, y: x + ' ' + y, named_en).strip(), subchunk.label()))
               else :
                nouns.append((subchunk[0], "NNE"))
        #if noun_list and len(noun_list) > 1:
        #return  combinations(noun_list, 2)
    for i in range(len(nouns) - 1):
        yield {"noun": nouns[i], "rnoun": nouns[i + 1]}

# function returning the noun-noun using spaCy
def get_noun_noun(doc):
    """
    if u need to identify the noun as named entity or not
    you can just go back to the related_noun function and annotate every extracted noun
    nouns are already extracted depending if they are named entity or not
    in a way that we get for example New York instead of New and York !
    :param doc:
    :return:
    """
    nouns =[]
    for chunk in doc.noun_chunk:
        nouns.append(related_noun(chunk))
    for i in range(len(nouns)-1):
        yield {"noun":nouns[i],"rnoun": nouns[i+1]}




## Unit test
# german pos tagger is using universal tags !
# getting the format of NLTK pos tags !
#tags =[(t.orth_,t.pos_) for t in doc]


nlp = spacy.load('de')
doc1 = nlp("Schöne Mädchen und hübsche Jungen sitzen auf der gelben Bank.")
doc2 = nlp("Der kleine Hase heißt Max.")
doc3 = nlp("Mein kleiner Hase.")
doc4 = nlp("Der kleine, süße Hase war auf dem Weg nach Hause.")
doc5 = nlp("Der kleine und süße Hase war Marias Haustier.")
doc6 = nlp("Der kleine, aber freche Hase wusste wie er sich zu wehren hatte.")
doc7 = nlp("Der Hase ist klein, aber kein Kuscheltier.")
doc8 = nlp("Eine bahnbrechende physikalische Entdeckung wurde letztes Jahr auf der Messe X vorgestellt.")

print(list(doc2.noun_chunks))
print(list(doc3.noun_chunks))
print(list(doc4.noun_chunks))
print(list(doc5.noun_chunks))
print(list(doc6.noun_chunks))
print(list(doc7.noun_chunks))
print(list(doc8.noun_chunks))
print("-------------")

for i in nouns_adj_spacy(doc1):
    print(i)
for i in nouns_adj_spacy(doc2):
    print(i)
for i in nouns_adj_spacy(doc3):
    print(i)
for i in nouns_adj_spacy(doc4):
    print(i)
for i in nouns_adj_spacy(doc5):
    print(i)
for i in nouns_adj_spacy(doc6):
    print(i)
for i in nouns_adj_spacy(doc7):
    print(i)
for i in nouns_adj_spacy(doc8):
    print(i)


print("-------------------------------")


#gen2 = get_adjs(nlp(doc))
#for i in gen2:
#    print(i)
