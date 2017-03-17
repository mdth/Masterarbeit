import spacy
import itertools
from nltk.chunk.regexp import RegexpParser
import functools
from nltk.tree import Tree
from textblob_de.lemmatizers import PatternParserLemmatizer
import nltk

class Parser:
    """A parser that ..."""

    NAMED_ENTITIES_TAGS = ["GPE", "PERSON", "ORGANIZATION", "LOCATION", "DATE", "TIME", "MONEY", "PERCENT",
                                "FACILITY"]
    NOUNS = ["NOUN","PROPN"]
    NP_Noun_Simple = """NP: {(<NOUN|PROPN>)+}"""

    SUBJECTS = ["sb"]
    OBJECTS = ["pd", "mo", "oa", "da"]

    def __init__(self):
        """Initialize a ...."""
        self.nlp = spacy.load('de')
        self.lemmatizer = PatternParserLemmatizer()
        self.parser_NP = RegexpParser(self.NP_Noun_Simple)
    
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

    def get_related_noun(self, chunk):
        """
        this function is used to get the noun in the chunk if it is a named entity or a simple noun
        :param chunk:
        :return:
        """
        ent = []
        for i in chunk:
            if i.pos_ in self.NOUNS:
                if i.ent_type:
                    ent.append(i.string)
                else:
                    yield i.string
        if ent:
            yield functools.reduce(lambda x, y: x + y, ent).strip()

    def nouns_adj_spacy(self, doc):
        """
        using the noun_phrase chunked in spacy we get the chunk extract all related adj to the noun in the chunk
        :param doc:
        :return:
        """
        for chunk in doc.noun_chunks:
            adjs = []
            chunk_list = [i.string for i in chunk]
            ind = 0
            for i in chunk:
                if i.pos_ == 'ADJ':
                    chunk_text = ''
                    for ch in chunk_list:
                        chunk_text = " " + chunk_text + str(ch)
                    print("chunktext" + chunk_text)
                    lemma = self.lemmatizer.lemmatize(chunk_text)
                    print(lemma)
                    adjs.append(lemma[ind][0])
                if not (i.dep_ == "punct"):
                    ind += 1
            if adjs:
                for i in self.get_related_noun(chunk):
                    for j in adjs:
                        yield {"noun": i.strip(), "adj": j}

    def lemmatize_text(self, doc):
        return self.lemmatizer.lemmatize(doc)

    def get_simple_sentence_SVO(self, tokens):
        """ this function return the main SVO of the sentence """
        subject = ''
        object = ''
        predicate = ''
        verb = next(item for item in tokens if item.dep_ == "ROOT")
        if (verb.pos_ == "VERB") or (verb.pos_ == "AUX"):
            predicate = verb.string.strip()
        else:
            print("Dependecy error.")

        subs = [item for item in verb.lefts if item.dep_ in self.SUBJECTS]
        objs = [item for item in verb.rights if item.dep_ in self.OBJECTS]

        # TODO debug
        text = [(item.string, item.dep_, item.head.string) for item in tokens]
        print(text)
        for sub in subs:
            if sub.head.string == verb.string:
                subject = sub.string.strip()
                break
        for obj in objs:
            if obj.head.string == verb.string:
                object = obj.string.strip()
                break

        return (subject, object, predicate)

    def getsvo(self, tokens):
        """This method get's sentences with conjunctions."""
        root = next(item for item in tokens if item.dep_ == "ROOT")
        print(root.string, root.pos_)
        if (root.pos_ != "VERB") and (root.pos_ != "AUX"):
            print("dependency error getsvo")
        else:
            items = [item.dep_ for item in tokens]
            print(items)
            if "cd" in items:
                subverbs = self.main_clause_split(root, tokens)
                subverbs.append(root)
                for verb in subverbs:
                    yield self.extractsvo(tokens, verb)

    # for and check the head of the and conj if it is situated just the

    def main_clause_split(self, root, tokens):
        """
        this function should returns two or more than one main clause
        :param tokens:
        :return:
        """
        # starting from a subordination conjunction that enclose a new clause you
        # can find the clauses included in one sentence
        # and -cc or punctuation  or mark to detect a second clause punct
        # returns just the subverbs not the root !!
        # coordination conjuction with verb as head

        subject = ''
        object = ''
        verb = ''
        text = [(item.string, item.dep_, item.head.string, item.head.pos_) for item in tokens]
        print(text)
        conj_word = next(item for item in tokens if item.dep_ == "cj")
        print(conj_word, conj_word.pos_)
        # conjunction but no second main clause
        if (conj_word.pos_ == "VERB") or (conj_word.pos_ == "AUX"):
            # TODO conj_word is the second verb
            verb = conj_word
            print(verb.lefts)
            print(verb.rights)
            subs = [item for item in verb.lefts if item.dep_ in self.SUBJECTS]
            objs = [item for item in verb.rights if item.dep_ in self.OBJECTS]
            print(subs)
            print(objs)
            for sub in subs:
                if sub.head.string == verb.string:
                    subject = sub.string.strip()
                    break
            for obj in objs:
                if obj.head.string == verb.string:
                    object = obj.string.strip()
                    break
            print(subject, object, verb)
        else:
            object = conj_word
            verb = root.string
            subs = [item for item in root.lefts if item.dep_ in self.SUBJECTS]
            print(subs)
            for sub in subs:
                if sub.head.string == verb:
                    subject = sub.string.strip()
                    break
            print(subject, object, verb)

        return None

    def extractsvo(self, tokens, verb):
        print(verb)
        subj = self.get_subject(verb)
        if subj:
            subs = self.extractcompso(tokens, subj)
            if not self.get_object(tokens, verb)[1] or not subj:
                print("no object in this sentence")
                return ("", "", "")
            else:
                for subject in subs:
                    passive, obj = self.get_object(tokens, verb)

                    if passive:
                        yield (obj, subject, verb.lemma_)
                    else:
                        yield (subject, obj, verb.lemma_)
        else:
            print("no subject")

    def extractcompso(self, tokens, so):
        conj = self.findconjso(so)

        for sub in itertools.chain([so], conj):
            yield self.compound(tokens, sub)

    def findconjso(self, so):
        # PRECONJ: pre-correlative conjunctions
        # return a generator with yield !!! attention !!!
        rights = [item for item in so.rights if item.dep_ == "conj"]
        while (rights):
            for i in rights:
                if i.head.string == so.string:
                    yield i
                    so = i
                    rights = [item for item in so.rights if item.dep_ == "conj"]

    def get_subject(self, root):
        subs = [item for item in root.lefts if item.dep_ in self.SUBJECTS]
        # check 6 dependecies related to subject :
        correct = True
        subs1 = [item for item in subs if item.dep_ == "nsubj" and item.head.string == root.string]
        subs2 = [item for item in subs if item.dep_ == "nsubjpass" and item.head.string == root.string]
        if subs1:
            return next(item for item in subs if item.dep_ == "nsubj" and item.head.string == root.string)
        elif subs2:
            return next(item for item in subs if item.dep_ == "nsubjpass" and item.head.string == root.string)
        """if subs1:
            return
        if  rsubs:
            nsubj = next(item for item in subs if item.dep_ == "nsubj" and item.head.string == root.string)
            print(nsubj,"nsubj")
            # check if nsubj is a correct nominal subject (comparing to 5 others dep on subjects)

            # for each nsubj
            for sub in nsubj.rights:
                if sub.dep == "csubjpass":
                    correct = False
                    pass
                elif sub.dep == "csubj":
                    correct = False
                    pass
        # we can check the right the second condition the real subject when it is related to the root :
            if correct :
                return nsubj
        elif next(item for item in subs if item.dep_ == "nsubjpass" and item.head.string == root.string):
            return  next(item for item in subs if item.dep_ == "nsubjpass" and item.head.string == root.string)"""

    # check conjunctions in subjects and objects !!
    # maybe we need to check conjunctions because lefts and rights will not get into depth more than one level remember !!


    def get_object(self, tokens, root):
        """
        thus function returns ( if the sentence is passive or active and the object or the passive subject)
        :param root:
        :return:    """
        objs = [item for item in tokens[root.i + 1:] if item.dep_ in self.OBJECTS]
        if len(objs) > 0:
            for i in objs:
                if i.dep_ == "attr" or i.dep_ == "dobj" and i.head.string == root.string:
                    return False, i.string
                if i.dep_ == "pobj":
                    if i.head.dep_ == "agent":
                        return True, i.string
                    else:
                        return False, i.string

        return False, ""

    def compound(self, tokens, so):
        # for Mr. Bingley and for video camera example
        index = so.i - 1
        comp = so.string
        while index > -1:
            if tokens[index].dep_ == "compound":
                comp = tokens[index].string + '' + comp
                index -= 1
            else:
                return comp
        return comp
