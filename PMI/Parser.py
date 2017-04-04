import spacy
from nltk.chunk.regexp import RegexpParser
import functools
from nltk.tree import Tree
import nltk
from collections import namedtuple
import treetaggerwrapper


class Parser:
    """A parser that ..."""

    NAMED_ENTITIES_TAGS = ["GPE", "PERSON", "ORGANIZATION", "LOCATION", "DATE", "TIME", "MONEY", "PERCENT",
                                "FACILITY"]
    NOUNS = ["NOUN","PROPN"]
    NP_Noun_Simple = """NP: {(<NOUN|PROPN>)+}"""

    SUBJECTS = ["sb"]
    OBJECTS = ["pd", "mo", "oa", "da", "oc"]
    VERBS = ["VERB", "AUX"]

    svo_obj = namedtuple('svo_object', ['subject', 'object', 'verb'])

    def __init__(self):
        """Initialize a ...."""
        print('Initializing Spacy...')
        self.nlp = spacy.load('de')
        print('Spacy was successfully initialized.')
        self.lemmatizer = treetaggerwrapper.TreeTagger(TAGLANG='de')
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
                    lemma = self.lemmatize(chunk_text)
                    adjs.append(lemma[ind])
                ind += 1
            if adjs:
                for i in self.get_related_noun(chunk):
                    for j in adjs:
                        yield {"noun": i.strip(), "adj": j}

    def lemmatize(self, doc):
        tags = self.lemmatizer.tag_text(doc)
        tags2 = treetaggerwrapper.make_tags(tags)
        return [item.lemma for item in tags2]

    def get_SVO(self, tokens):
        """ this function return the main SVO of the sentence """
        svo_pairs = []
        # search svo for the root verb
        root = next(item for item in tokens if item.dep_ == "ROOT")

        if self.is_passive(root):
            svo_pairs.append(self.extract_passive_SVO(root))
        else:
            svo_pairs.append(self.svo_searcher(root))

        dependencies = [item.dep_ for item in tokens]
        item_tokens = [item for item in tokens]
        print([(item.string, item.dep_) for item in tokens])
        if ("cj" in dependencies) and ("cd" not in dependencies):
            # more than one main clause
            second_verb = next(item for item in tokens if item.dep_ == "cj")
            svo_pairs.append(self.svo_searcher(second_verb))
        if "cd" in dependencies:
            conj_word = next((item for item in tokens if item.dep_ == "cj"), None)
            if conj_word is not None:
                if (conj_word.pos_ == "VERB") or (conj_word.pos_ == "AUX"):
                    svo_pairs.append(self.svo_searcher(conj_word))
                else:
                    verb = root.string.strip()
                    verb_index = item_tokens.index(root)
                    if item_tokens[verb_index - 1].dep_ == "cj":
                        # root verb is next to conjunction word
                        subject = conj_word.string.strip()
                        object = svo_pairs[0].object
                        svo_pairs.append(self.svo_obj(subject=subject, object=svo_pairs[0].object, verb=verb))
                    else:
                        object = conj_word.string.strip()
                        subject = self.extract_subject(root, self.SUBJECTS)
                        svo_pairs.append(self.svo_obj(subject=subject, object=object, verb=verb))
        return svo_pairs

    def svo_searcher(self, verb):
        if (verb.pos_ == "VERB") or (verb.pos_ == "AUX"):
            predicate = verb.string.strip()
            subject = self.extract_subject(verb, self.SUBJECTS)
            object = self.extract_object(verb, self.OBJECTS)
            return self.svo_obj(subject=subject, object=object, verb=predicate)
        else:
            print("Dependecy error. No verb root found.")
            return None

    def extract_object(self, verb, object_criteria):
        object = ''
        objects = [item for item in verb.rights if item.dep_ in object_criteria]
        possible_objects = [obj for obj in objects if obj.head.string == verb.string]
        if len(possible_objects) == 1:
            if possible_objects[0].dep_ == 'oc':
                object_temp = possible_objects[0].lefts
                if list(item for item in object_temp):
                    object = [item.string.strip() for item in object_temp]
            else:
                object = possible_objects[0].string.strip()
        elif len(possible_objects) > 1:
            if possible_objects[0].dep_ == 'da' and possible_objects[1].dep_ == 'oa':
                object = possible_objects[1].string.strip()
            elif possible_objects[0].dep_ == 'oa' and possible_objects[1].dep_ == 'mo':
                object = possible_objects[1].string.strip()
        else:
            pass
        return object

    def extract_subject(self, verb, subject_criteria):
        #TODO maybe match subject like if length == 0 then could not find subject
        subject = ''
        subjects = [item for item in verb.lefts if item.dep_ in subject_criteria]
        for sub in subjects:
            if sub.head.string == verb.string:
                subject = self.find_long_ne(sub)
                break
        return subject

    def find_long_ne(self, noun):
        nounright = [item for item in noun.rights]
        if len(nounright) > 0:
            noun = noun.string.strip()
            for sub_noun in nounright:
                noun = noun + ' ' + sub_noun.string.strip()
        else:
            noun = noun.string.strip()
        return noun

    def extract_passive_SVO(self, verb):
        subject = self.extract_object(verb, self.SUBJECTS)
        object = self.extract_subject(verb, self.OBJECTS)
        return self.svo_obj(subject=subject, object=object, verb=verb.string.strip())

    def is_passive(self, verb):
        """Checks if sentence or part-sentence is in passive form by looking for a subject right from the verb."""
        if len([item for item in verb.rights if item.dep_ in self.SUBJECTS]) == 0:
            return False
        else:
            return True