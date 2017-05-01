import spacy
from collections import defaultdict

nlp = spacy.load('de')
doc = nlp('"Ja, ich habe ein Anliegen ...«, begann der Fürst.')
doc1 = nlp("Herr Myschkin liebte Nadja.")
doc2 = nlp("Ich bin alt geworden.")
doc3 = nlp("Gawrila Ardalionowitsch nickte dem Fürsten zu und begab sich eilig in das Arbeitszimmer.")
doc4 = nlp("Hans isst eine Torte und Hannah kocht Tee.")

# Finding a verb with a subject from below — good
def getverbnoun(doc):
    pairs = defaultdict(list)
    for possible_subject in doc:
        noun = possible_subject
        print(noun.string, noun.dep_, noun.pos_, noun.head, noun.ent_type_)
        if noun.dep_ == "sb":
            ent = get_entities(noun)
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
            if ent.ent_type_:
                entity += ent.string.strip() + " "
        return entity
    else:
        return None

getverbnoun(doc)
getverbnoun(doc1)
getverbnoun(doc2)
getverbnoun(doc3)