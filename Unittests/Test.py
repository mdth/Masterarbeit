from nltk.stem.snowball import GermanStemmer
import functools
import spacy
from textblob_de import TextBlobDE
from textblob_de.lemmatizers import PatternParserLemmatizer


def get_related_noun(chunk):
    """
    this function is used to get the noun in the chunk if it is a named entity or a simple noun
    :param chunk:
    :return:
    """
    ent = []
    for i in chunk:
        if i.pos_ in ["NOUN", "PROPN"]:
            if i.ent_type:
                ent.append(i.string)
            else:
                yield i.string
    if ent:
        yield functools.reduce(lambda x, y: x + ' ' + y, ent).strip()


def nouns_adj_spacy(doc):
    for chunk in doc.noun_chunks:
        adjs = []
        for i in chunk:
            if i.pos_ == 'ADJ':
                adjs.append(i.lemma_)
        if adjs:
            for i in get_related_noun(chunk):
                for j in adjs:
                    yield {"noun": i, "adj": j}

#nlp = spacy.load('de')
#doc = nlp("Schöne Mädchen und hübsche Jungen sitzen auf der gelben Bank.")

lemmatizer = PatternParserLemmatizer()
stemmer = GermanStemmer()
doc = lemmatizer.lemmatize("Eine bahnbrechende physikalische Entdeckung wurde letztes Jahr auf der Messe X vorgestellt.")
print(doc)



#for i in nouns_adj_spacy(doc):
#    print(i)

#print("--------")
#for word in doc:
#    print(word.i, word.text, word.lemma_, word.pos)
