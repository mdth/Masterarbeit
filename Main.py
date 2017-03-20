import time
import re
from RDFParser import RDFParser
from Prototype import Prototype
from MongoDBConnector import MongoDBConnector
from PostGreDBConnector import PostGreDBConnector
from HelperMethods import read_in_csv_file

#MONGO_DB = MongoDBConnector()
POSTGRE_DB = PostGreDBConnector()

#PROTOTYPE = Prototype(
   # mongo_db=MONGO_DB, postagger="spacy-tagger", postgre_db=POSTGRE_DB, sentence_mode=True, window_size=1)
parser = RDFParser(POSTGRE_DB)
parser.get_pattern_from_rdf("persons.rdf")
#parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/locations.rdf")

# using constraints
#constraints = read_in_csv_file("C:/Users/din_m/PycharmProjects/Masterarbeit/constraints.csv")
#PROTOTYPE.get_snippets(constraints)

#PROTOTYPE.get_sentence_window("Jumin Han", ["Hallelujah.", "Herr Jumin Han ist beliebt.", "Hahahaha."], [("Jumin Han","beliebt", +3)])
#PROTOTYPE.get_sentence_window("große Stadt", ["Hallo.", "Eine große Stadt.", "Leckere Schokolade."], None)
#PROTOTYPE.get_word_window("Han", ["Herr", "Jumin", "Han", "ist", "unglaublich", "beliebt."], [("Han", "Herr", -2)])

#PROTOTYPE.get_word_window("Jumin Han", ["Herr", "Jumin", "Han", "ist", "unglaublich", "beliebt."], [("Jumin Han", "Herr", -1)])

#PROTOTYPE.aggregation()

#PROTOTYPE.dummy('"Hallo, willkommen.')

m = re.search('willkommen', '"Hallo, willkommen."')
# TODO richtiger Offset
print(m.start(), m.end())
n = re.findall('willkommen', '"Hallo, willkommen."')