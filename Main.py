import time
import re
from RDFParser import RDFParser
from Prototype import Prototype
from MongoDBConnector import MongoDBConnector
from PostGreDBConnector import PostGreDBConnector
from HelperMethods import read_in_csv_file

MONGO_DB = MongoDBConnector()
POSTGRE_DB = PostGreDBConnector()

PROTOTYPE = Prototype(
    mongo_db=MONGO_DB, postagger="spacy-tagger", postgre_db=POSTGRE_DB, sentence_mode=True, window_size=0)
##parser = RDFParser(POSTGRE_DB)
##parser.get_pattern_and_push("persons.rdf")

# using constraints
#constraints = read_in_csv_file("C:/Users/din_m/PycharmProjects/Masterarbeit/constraints.csv")
#PROTOTYPE.get_snippets(constraints)

##PROTOTYPE.get_snippets(None)
##PROTOTYPE.aggregation()
##PROTOTYPE.find_spo_and_adjectives()
#PROTOTYPE.calculate_pmi()
PROTOTYPE.intersect_bscale("FemMainCharacter", "Character", "MainCharacter", "Female")


#m = re.search('willkommen', '"Hallo, willkommen."')
#print(m.start(), m.end())
#n = re.findall('willkommen', '"Hallo, willkommen."')