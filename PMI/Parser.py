import spacy
from nltk.chunk.regexp import RegexpParser
import functools
from nltk.tree import Tree
from textblob_de.lemmatizers import PatternParserLemmatizer
import nltk
from collections import namedtuple


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

    def get_SVO(self, tokens):
        """ this function return the main SVO of the sentence """
        svo_pairs = []
        # search svo for the root verb
        print([(item.string, item.dep_, item.pos_, item.head) for item in tokens])
        root = next(item for item in tokens if item.dep_ == "ROOT")
        if self.is_passive(root):
            print("passive")
            svo_pairs.append(self.extract_passive_SVO(root))
        else:
            svo_pairs.append(self.svo_searcher(root))

        dependencies = [item.dep_ for item in tokens]
        item_tokens = [item for item in tokens]
        if "cd" in dependencies:
            conj_word = next(item for item in tokens if item.dep_ == "cj")
            if (conj_word.pos_ == "VERB") or (conj_word.pos_ == "AUX"):
                svo_pairs.append(self.svo_searcher(conj_word))
            else:
                verb = root.string.strip()
                verb_index = item_tokens.index(root)
                if item_tokens[verb_index - 1].dep_ == "cj":
                    # root verb is next to conjunction word
                    subject = conj_word.string.strip()
                    object = svo_pairs[0].object
                    print(subject, object, verb)
                    svo_pairs.append(self.svo_obj(subject=subject, object=svo_pairs[0].object, verb=verb))
                else:
                    object = conj_word.string.strip()
                    subject = self.extract_subject(root, self.SUBJECTS)
                    print(subject, object, root)
                    svo_pairs.append(self.svo_obj(subject=subject, object=object, verb=verb))
        print(svo_pairs)
        return svo_pairs

    def svo_searcher(self, verb):
        if (verb.pos_ == "VERB") or (verb.pos_ == "AUX"):
            predicate = verb.string.strip()
            subject = self.extract_subject(verb, self.SUBJECTS)
            object = self.extract_object(verb, self.OBJECTS)
            print(subject, object, predicate)
            return self.svo_obj(subject=subject, object=object, verb=predicate)
        else:
            print("Dependecy error. No verb root found.")

    def extract_object(self, verb, object_criteria):
        object = ''
        objects = [item for item in verb.rights if item.dep_ in object_criteria]
        possible_objects = [obj for obj in objects if obj.head.string == verb.string]
        if len(possible_objects) == 1:
            if possible_objects[0].dep_ == 'oc':
                object_temp = possible_objects[0].lefts
                object = [item.string.strip() for item in object_temp][0]
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
                subject = sub.string.strip()
                break
        return subject

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
