import spacy
import functools
from collections import namedtuple
import treetaggerwrapper


class Parser:
    """A parser that ..."""

    NOUNS = ["NOUN","PROPN"]
    OBJECTS = ["pd", "mo", "oa", "da", "oc"]
    SUBJECT = ["sb"]
    VERBS = ["VERB", "AUX"]
    NOUN_ADJECTIVES = NOUNS + ["ADJ", "PRON"]

    svo_obj = namedtuple('svo_object', ['subject', 'object', 'verb'])

    def __init__(self):
        """Initialize a ...."""
        print('Initializing Spacy...')
        self.nlp = spacy.load('de')
        print('Spacy was successfully initialized.')
        self.lemmatizer = treetaggerwrapper.TreeTagger(TAGLANG='de')

    def get_correlating_nouns_and_adjectives(self, tokens):
        """This functions returns a list of all nouns and adjectives in a text snippet."""
        return list(item.string.strip() for item in tokens if item.pos_ in self.NOUN_ADJECTIVES)

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
                    ent.append(self.lemmatize_word(i.string))
                else:
                    yield self.lemmatize_word(i.string)
        if ent:
            yield functools.reduce(lambda x, y: x + " " + y, ent)

    def nouns_adj_spacy(self, doc):
        """
        using the noun_phrase chunked in spacy we get the chunk extract all related adj to the noun in the chunk
        :param doc:
        :return:
        """
        for chunk in doc.noun_chunks:
            adjs = []
            chunk_list = [i.string for i in chunk]
            chunk_text = ''
            for item in chunk_list:
                chunk_text = " " + chunk_text + str(item)
            ind = 0
            for chunk_part in chunk:
                if chunk_part.pos_ == 'ADJ':
                    lemma = self.lemmatize_chunk(chunk_text)
                    adjs.append(lemma[ind])
                ind += 1
            if adjs:
                for noun in self.get_related_noun(chunk):
                    for adj in adjs:
                        yield {"noun": noun, "adj": adj}

    def lemmatize_chunk(self, doc):
        tags = self.lemmatizer.tag_text(doc)
        tags2 = treetaggerwrapper.make_tags(tags)
        return [item.lemma for item in tags2]

    def lemmatize_word(self, doc):
        tags = self.lemmatizer.tag_text(doc)
        tags2 = treetaggerwrapper.make_tags(tags)
        if tags2:
            return tags2[0].lemma
        else:
            return ""

    def get_SVO(self, tokens):
        """ this function return the main SVO of the sentence """
        svo_pairs = []
        # search svo for the root verb
        roots = list(item for item in tokens if item.dep_ == "ROOT" and item.pos_ in self.VERBS)
        for root in roots:
            if self.is_passive(root):
                svo_pairs.append(self.extract_passive_SVO(root))
            else:
                svo_pairs.append(self.svo_searcher(root))
                dependencies = [item.dep_ for item in tokens]
                item_tokens = [item for item in tokens]
                if ("cj" in dependencies) and ("cd" not in dependencies):
                    # more than one main clause
                    second_verb = next(item for item in tokens if item.dep_ == "cj")
                    svo_pairs.append(self.svo_searcher(second_verb))
                if "cd" in dependencies:
                    conj_word = next((item for item in tokens if item.dep_ == "cj"), None)
                    if conj_word is not None:
                        if conj_word.pos_ in self.VERBS:
                            svo_pairs.append(self.svo_searcher(conj_word))
                        else:
                            verb = self.lemmatize_word(root.string)
                            verb_index = item_tokens.index(root)
                            if item_tokens[verb_index - 1].dep_ == "cj":
                                # root verb is next to conjunction word
                                subject = conj_word.string.strip()
                                object = svo_pairs[0].object
                                svo_pairs.append(self.svo_obj(subject=subject, object=object, verb=verb))
                            else:
                                object = conj_word.string.strip()
                                subject = self.extract_subject(root, self.SUBJECT)
                                svo_pairs.append(self.svo_obj(subject=subject, object=object, verb=verb))
        return svo_pairs

    def svo_searcher(self, verb):
        if verb.pos_ in self.VERBS:
            predicate = self.lemmatize_word(verb.string)
            subject = self.extract_subject(verb, self.SUBJECT)
            object = self.extract_object(verb, self.OBJECTS)
            return self.svo_obj(subject=subject, object=object, verb=predicate)
        else:
            print("Dependecy error. No verb root found.")
            return None

    def extract_object(self, verb, object_criteria):
        object = None
        objects = [item for item in verb.rights if item.dep_ in object_criteria]
        possible_objects = [obj for obj in objects if obj.head.string == verb.string]
        if len(possible_objects) == 1:
            if possible_objects[0].dep_ == 'oc':
                object_temp = list(possible_objects[0].lefts)
                if object_temp:
                    if len(object_temp) == 1:
                        object = object_temp[0]
            else:
                object = possible_objects[0]
        elif len(possible_objects) > 1:
            if possible_objects[0].dep_ == 'da' and possible_objects[1].dep_ == 'oa':
                object = possible_objects[1]
            elif possible_objects[0].dep_ == 'oa' and possible_objects[1].dep_ == 'mo':
                object = possible_objects[1]
        else:
            pass

        if object is not None:
            if object.ent_type:
                object = self.find_long_ne(object)
            else:
                object = self.lemmatize_word(object.string)
        else:
            object = ''
        return object

    def extract_subject(self, verb, subject_criteria):
        subject = ''
        subjects = [item for item in verb.lefts if item.dep_ in subject_criteria]
        for sub in subjects:
            if sub.head.string == verb.string:
                if sub.ent_type:
                    subject = self.find_long_ne(sub)
                    break
                else:
                    subject = self.lemmatize_word(sub.string)
        return subject

    def find_long_ne(self, noun):
        nounright = [item for item in noun.rights]
        nounleft = [item for item in noun.lefts]
        noun = noun.string.strip()
        # found middle word of multi-word subject
        if len(nounright) > 0 and len(nounleft) > 0:
            for sub_noun in nounright:
                if sub_noun.ent_type:
                    noun = noun + ' ' + sub_noun.string.strip()
            for sub_noun in nounleft:
                if sub_noun.ent_type:
                    noun = noun + ' ' + sub_noun.string.strip()
            noun = " ".join(item for item in self.lemmatize_chunk(noun))
        elif len(nounright) > 0:
            for sub_noun in nounright:
                if sub_noun.ent_type:
                    noun = noun + ' ' + sub_noun.string.strip()
            noun = " ".join(item for item in self.lemmatize_chunk(noun))
        elif len(nounleft) > 0:
            for sub_noun in nounleft:
                if sub_noun.ent_type:
                    noun = sub_noun.string.strip() + ' ' + noun
            noun = " ".join(item for item in self.lemmatize_chunk(noun))
        elif len(nounright) == 0 and len(nounleft) == 0:
            noun = self.lemmatize_word(noun)
        else:
            noun = ''
        return noun

    def extract_passive_SVO(self, verb):
        subject = self.extract_object(verb, self.SUBJECT)
        object = self.extract_subject(verb, self.OBJECTS)
        verb = self.lemmatize_word(verb.string)
        return self.svo_obj(subject=subject, object=object, verb=verb)

    def is_passive(self, verb):
        """Checks if sentence or part-sentence is in passive form by looking for a subject right from the verb."""
        if len(list(item for item in verb.rights if item.dep_ in self.SUBJECT)) == 0:
            return False
        else:
            return True