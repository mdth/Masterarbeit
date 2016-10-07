from spacy.en import English
import itertools
nlp = English()

#coordination in adjectives and coordination in nouns
#An adjectival complement is an adjective phrase that modiﬁes the head of a VP|SINV|SQ, that is usually a verb
#this word is based on the dependency acomp
# the dependency is giving wrong answers with the linking verb seem !!
def find_pairs(tokens):

    adjectives = [item for item in tokens if item.dep_ == "acomp" and item.pos_ == "ADJ"]
    verbs = [item.head for item in adjectives]
    for verb, adj in zip(verbs,adjectives):
        subject = next(item for item in verb.lefts if item.dep_ == "nsubj" and item.head == verb)
        subs = itertools.chain([subject], findconjso(subject))
        adjs = itertools.chain([adj], findconjadj(adj))
        for i, j in itertools.product(subs, adjs):
            yield (i.string, j.string)


def findconjso(so):
    """
    this function generates the subjects related by conjuction
    :param so:
    :return:
    """
    # PRECONJ: pre-correlative conjunctions
    # return a generator with yield !!! attention !!!
    rights = [item for item in so.rights if item.dep_ == "conj"]
    while (rights):
        for i in rights:
            if i.head.string == so.string:
                yield i
                so = i
                rights = [item for item in so.rights if item.dep_ == "conj"]


def findconjadj(adj):
    """
    this function generates the conjuction from a given adjectives
    :param adj:
    :return:
    """
    rights = [item for item in adj.rights if item.dep_ == "conj"]
    while (rights):
        for i in rights:
            if i.head.string == adj.string:
                yield i
                adj = i
                rights = [item for item in adj.rights if item.dep_ == "conj"]


######################UnitTest##########################################################################################
doc = nlp("the girl and the boy seem worried and anxious")



