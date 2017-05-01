import spacy
from collections import defaultdict

nlp = spacy.load('de')
doc = nlp('"Ja, ich habe ein Anliegen ...«, begann der Fürst.')
doc1 = nlp("Herr Myschkin liebte Nadja.")
doc2 = nlp("Ich bin alt geworden.")
doc3 = nlp("Gawrila Ardalionowitsch nickte dem Fürsten zu und begab sich eilig in das Arbeitszimmer.")
doc4 = nlp("Dieser Hund gehört mir und er ist ein Terrier.")
doc5 = nlp("Helena, Anna und Tom gehen in den Park.")

# Finding a verb with a subject from below — good
def getverbnoun(doc):
    pairs = defaultdict(list)
    for possible_subject in doc:
        noun = possible_subject
        print(noun.string, noun.dep_, noun.pos_, noun.head, noun.ent_type_)
        if noun.dep_ == "sb":
            ent = get_entities(noun)
            print(ent)
            if noun.head.pos_ == "AUX":
                verb = next((item for item in doc if item.pos_ == "VERB" and item.head == noun.head), None)
                if verb is not None:
                    getverbnoun_helper(ent, pairs, verb.string, noun.string)
                else:
                    verb = noun.head.string
                    getverbnoun_helper(ent, pairs, verb, noun.string)
            elif noun.head.pos_ == "VERB":
                verb = noun.head.string.strip()
                getverbnoun_helper(ent, pairs, verb, noun.string)
    print(pairs)

def getverbnoun_helper(ent, pairs, verb, noun):
    if ent is not None:
        pairs[verb].append(ent)
    else:
        pairs[verb].append(noun)

def get_entities(possible_subject):
    # search for entities near related to subject
    entities = [item for item in possible_subject.rights]
    if entities:
        entity = ''
        for ent in entities:
            if ent.dep_ == "punct":
                return None
            if ent.ent_type_:
                entity += ent.string.strip() + " "
        return entity
    else:
        return None

def get_more_subjects(possible_subject):
    more_subjects = [item for item in possible_subject.rights]
    for ent in more_subjects:
        if ent.dep_ == "cj" and ent.head.dep_ == "cd":
            if ent.head.head_ == possible_subject:
                print("new sub: " + ent)
                return ent



getverbnoun(doc)
getverbnoun(doc1)
getverbnoun(doc2)
getverbnoun(doc3)
getverbnoun(doc4)
getverbnoun(doc5)