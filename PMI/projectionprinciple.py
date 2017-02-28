import spacy
import itertools


SUBJECTS = ["sb", "oa"]
OBJECTS = ["oa", "nk", "pd", "sb"]
#@ TODO find a function to detect a question...
#@ TODO test this module on german text
# a parser that eliminates all modifiers and complement or relative
# clause included in one sentence


def get_SVO(tokens):
    """ this function return the main SVO of the sentence """
    # active sentence
    #@TODO examin the case where there is a conjuction CC related to verbs !!! (two main clauses in one sentence)
    subject = ''
    object = ''
    predicate = ''
    verb = next(item for item in tokens if item.dep_ == "ROOT")
    if (verb.pos_ == "VERB") or (verb.pos_ == "AUX"):
        predicate = verb.lemma_
    else:
        print("dependecy error")

    subs = [item for item in verb.lefts if item.dep_ in SUBJECTS]
    objs = [item for item in verb.rights if item.dep_ in OBJECTS]

    for sub in subs:
        if sub.head.string == verb.string:
            subject = sub.string
            break
    for obj in objs:
        if obj.head.string == verb.string:
            object = obj.string
            break

    return (subject, object, predicate)

#testset :
#"the boy eats banana" ->('boy ', 'banana', 'eats ')
# "the father opens the door to his sister "('father ', 'door ', 'opens ')
# passive form is not correct
# check conjunctions in subject


def get_subject(root):
    subs = [item for item in root.lefts if item.dep_ in SUBJECTS]
    # check 6 dependecies related to subject :
    correct = True
    subs1 = [item for item in subs if item.dep_ == "nsubj" and item.head.string == root.string]
    subs2 = [item for item in subs if item.dep_ == "nsubjpass" and item.head.string == root.string]
    if subs1 :
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


def get_object(tokens,root):
    """
    thus function returns ( if the sentence is passive or active and the object or the passive subject)
    :param root:
    :return:    """
    objs = [item for item in  tokens[root.i+1:] if item.dep_ in OBJECTS]
    if len(objs) > 0:
        for i in objs:
            if i.dep_ == "attr" or i.dep_ == "dobj" and i.head.string == root.string:
                return False, i.string
            if i.dep_ == "pobj" :
                if i.head.dep_ == "agent":
                 return True, i.string
                else :
                    return False, i.string

    return False,""


def compound(tokens, so):
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


def compound_last(tokens, so):
    # for Mr. Bingley and for video camera example
    if tokens[so.i - 1].dep_ == "compound":
        return tokens[so.i - 1].string + '' + so.string
    else :
        return so.string
# check output for both compound and possessive compound can be the input of the poss !!!

# is it necessary ? because any one the verb and the subject refer to the same noun
# about possessive in case John's mother equivalent to mother


def possessive(tokens, so):
    if tokens[so.i-1].string == "'s":
        return tokens[so.i -1].head.string + """'s""" + tokens[so.i]
    else:
        return so.string

# works fine !


def findconjso(so):
        # PRECONJ: pre-correlative conjunctions
        #return a generator with yield !!! attention !!!
        rights = [item for item in so.rights if item.dep_ == "conj"]
        while (rights):
         for i in rights:
             if i.head.string == so.string:
                yield i
                so = i
                rights = [item for item in so.rights if item.dep_ == "conj"]


def extractcompso(tokens, so):
    conj = findconjso(so)

    for sub in itertools.chain([so], conj):
        yield compound(tokens, sub)


# do the same to the object compound !!

def extractsvo(tokens,verb):
    print(verb)
    subj = get_subject(verb)
    if subj:
        subs = extractcompso(tokens, subj)
        if not get_object(tokens, verb)[1] or not subj:
            print("no object in this sentence")
            return ("", "", "")
        else:
            for subject in subs:
                passive, obj = get_object(tokens, verb)

                if passive:
                    yield (obj, subject, verb.lemma_)
                else:
                    yield (subject, obj, verb.lemma_)
    else:
        print("no subject")


#(obj, subject, verb.lemma_)


def svo(tokens):
    gen = getsvo(tokens)
    for a in gen:
      if a.__next__():
        for b in a:
          yield b


def getsvo(tokens):
    root = next(item for item in tokens if item.dep_ == "ROOT")
    print(root.string, root.pos_)
    if root.pos_ != "VERB":
        print("dependency error getsvo")
    else:
        subverbs = main_clause_split(tokens)
        subverbs.append(root)
        for verb in subverbs:
            yield extractsvo(tokens,verb)

# for and check the head of the and conj if it is situated just the


def main_clause_split(tokens):
    """
    this function should returns two or more than one main clause
    :param tokens:
    :return:
    """
    # starting from a subordination conjunction that enclose a new clause you
    # can find the clauses included in one sentence
    #and -cc or punctuation  or mark to detect a second clause punct
    #returns just the subverbs not the root !!
    #coordination conjuction with verb as head
    cc = [item.head for item in tokens if item.dep_ == "cc" and item.head.pos_ == "VERB"]
    print(cc)
    # head is the verb coordinated with !!
    subcc = [item for item in tokens if item.dep_== "conj" and item.head in cc]
    print(subcc)
    marks = [item for item in tokens if item.dep_ == "mark"]
    print(marks)
    subverbs = [item.head for item in marks]
    return subverbs + subcc





    ##################################UNIT TEST#########################################################################
    ####################################################################################################################
    ####################################################################################################################
    # from these new head get the subject and the object with the same
    # thechniques just assign to the root the new head !!
""""   # case with 'and' the head of head is the root verb
Mr.  compound Bingley
Bingley  nsubj danced
had  aux danced
danced  ROOT danced
with  prep danced
her  poss twice
twice  advmod danced
and  cc danced
she  nsubjpass distinguished
had  aux distinguished
been  auxpass distinguished
distinguished  conj danced
by  agent distinguished
his  poss sisters
sisters pobj by
"""
"""nlp = English()
#doc = nlp("I hope Mr. Bingley will like it, Lizzy.")
for i in doc :
    print(i.string,i.dep_,i.head)
gen = getsvo(doc)
for i in gen:
    for j in i:
        print(j)
        #the father bring flowers for the house"('father ', 'flowers ', 'bring ')
#"I bought a new bed "('I ', 'bed', 'bought ')
#The girls stared at their father('girls ', 'father', 'stared ')"""

nlp = spacy.load('de')
doc1 = nlp("Ich fahre mein Auto.")
doc2 = nlp("Ich wünsche mir einen Tannenbaum.")
doc3 = nlp("Den Mann biss der Hund.") #passive
doc4 = nlp("Ich bin Berliner.")
doc5 = nlp("Ich hasse dich!")
doc6 = nlp("Ich bin alt geworden.") #adj als objekt
doc7 = nlp("Ich bin Deutscher und Vietnamese.")
doc8 = nlp("Rosen sind rot und Veilchen sind blau.")
doc9 = nlp("Dieser Hund gehört mir und er heißt Lola.") #passive + conjunction
doc10 = nlp("Das Haus ist grün.")
doc11 = nlp("Das Haus ist grün und die Dachziegel sind rot.")

#for i in doc:
    #print("DOC: " + i.string, i.dep_, i.head)

print(get_SVO(doc1))
print(get_SVO(doc2))
print(get_SVO(doc3))
print(get_SVO(doc4))
print(get_SVO(doc5))
print(get_SVO(doc6))
print(get_SVO(doc7))
print(get_SVO(doc8))
print(get_SVO(doc9))
print(get_SVO(doc10))
print(get_SVO(doc11))

for i in doc6:
    print("DOC: " + i.string, i.dep_, i.head)
for i in doc7:
    print("DOC: " + i.string, i.dep_, i.head)
for i in doc8:
    print("DOC: " + i.string, i.dep_, i.head)
for i in doc9:
    print("DOC: " + i.string, i.dep_, i.head)
for i in doc11:
    print("DOC: " + i.string, i.dep_, i.head)

"""for i in gen:
    for j in i:
        print("GEN: " + j)
"""
#testset :
#"the boy eats banana" ->('boy ', 'banana', 'eats ')
# "the father opens the door to his sister "('father ', 'door ', 'opens ')
# passive form is not correct
# check conjunctions in subject