import spacy
from nltk.chunk.regexp import RegexpParser
import functools
from nltk.tree import Tree
from textblob_de.lemmatizers import PatternParserLemmatizer
import nltk
##### This module is for parsing german text using Spacy####
# universal tags :ADJ, ADP, ADV, AUX, CONJ, DET, INTJ, NOUN, NUM, PART, PRON, PROPN, PUNCT, SCONJ, SYM, VERB, X, EOL, SPACE.


class Parser:
    """A parser that ..."""
    NP_GRAMMAR_SIMPLE = """NP: {<CD>?((<JJ.*><CC>|<,>))*(<JJ.*>|<N.*>)+}"""
    # use this regular expression for the chunking to get the different related ADJs with NLTK!!

    Np_GRAMMAR_SIMPLE_UNIVERSAL = """
             NP : {((<ADJ>(<PUNCT>)*(<CONJ>)*)*(<ADJ>(<NOUN>|<PROPN>))+|(<NOUN><AUX><ADJ>((<PUNCT>)*(<CONJ>)*<ADJ>))+)}
             """
    NAMED_ENTITIES_TAGS = ["GPE", "PERSON", "ORGANIZATION", "LOCATION", "DATE", "TIME", "MONEY", "PERCENT",
                                "FACILITY"]
    NP_Noun_Simple = """NP: {(<NOUN|PROPN>)+}"""

    def __init__(self):
        """Initialize a ...."""
        self.nlp = spacy.load('de')
        self.lemmatizer = PatternParserLemmatizer()
        self.parser_NP = RegexpParser(self.NP_Noun_Simple)
        self.parser_smp = RegexpParser(self.Np_GRAMMAR_SIMPLE_UNIVERSAL)
    
    def related_noun(self, chunk):
        tree = self.parser_NP.parse(chunk.leaves())
        for chunk in tree:
            if isinstance(chunk, Tree) and chunk.label() == 'NP':
                rchunk = nltk.ne_chunk(chunk.leaves())
                named_en = []
                for subchunk in rchunk:
                    if isinstance(subchunk, Tree) and subchunk.label() in self.NAMED_ENTITIES_TAGS:
                        for word, tag in subchunk:
                            named_en.append(word)
                        yield functools.reduce(lambda x, y: x + ' ' + y, named_en).strip()
                    else:
                        yield subchunk[0]
    
    # Extracting Adj related to nouns from a sentence #
    
    def get_adjs(self, tags):
        """
        chunked with simple grammar
        get all adjectives related to a Noun using the chunks and sub chunks
        :return: generator of dictionaries of {("NN","adj"),...}
        """
        noun_adj_sub_list = []
        tree = self.parser_smp.parse(tags)
        for subchunk in tree:
            if isinstance(subchunk, Tree) and subchunk.label() == 'NP':
    
                adjs = []
                for word, tag in subchunk:
                    if tag == 'ADJ':
                        adjs.append(word)
                    nouns = self.related_noun(subchunk)
                    if nouns and adjs:
                        for adj in adjs:
                            for noun in nouns:
                                yield {"noun": noun, "adj": adj}
                        adjs = []
    
    def get_related_noun(self, chunk):
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
            yield functools.reduce(lambda x, y: x + ' ' + y, ent).strip()

    def nouns_adj_spacy(self, doc):
        """
        using the noun_phrase chunked in spacy we get the chunk extract all related adj to the noun in the chunk
        :param doc:
        :return:
        """
        for chunk in doc.noun_chunks:
            adjs = []
            ind = 0
            for i in chunk:
                if i.pos_ == 'ADJ':
                    chunk_list = [i.string for i in chunk]
                    chunk_text = ''
                    for ch in chunk_list:
                        chunk_text = " " + chunk_text + str(ch)
                    print("chunktext" + chunk_text)
                    lemma = self.lemmatizer.lemmatize(chunk_text)
                    print(lemma)
                    adjs.append(lemma[ind][0])
                ind = + 1
            if adjs:
                for i in self.get_related_noun(chunk):
                    for j in adjs:
                        yield {"noun": i.strip(), "adj": j}
    
    # with NLTK
    def nouns_list(self, sent):
        """tree chunked with NP_Noun_Simple chunker
        this function create a couple of nouns from a giving list with a sliding window of size 2
        :return:generator
        """
        #tokens = nltk.word_tokenize(sent)
        tree = self.parser_NP.parse(nltk.pos_tag(sent))
        nouns = []
        for chunk in tree:
            if isinstance(chunk, Tree) and chunk.label() == 'NP':
               rchunk = nltk.ne_chunk(chunk.leaves())
               named_en = []
               for subchunk in rchunk:
                   if isinstance(subchunk, Tree) and subchunk.label() in self.NAMED_ENTITIES_TAGS:
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
    def get_noun_noun(self, doc):
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
            nouns.append(self.related_noun(chunk))
        for i in range(len(nouns)-1):
            yield {"noun":nouns[i],"rnoun": nouns[i+1]}

    def lemmatize_text(self, doc):
        return self.lemmatizer.lemmatize(doc)
