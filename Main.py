import time
from RDFParser import RDFParser
from Prototype import Prototype
from MongoDBConnector import MongoDBConnector
from PostGreDBConnector import PostGreDBConnector


POSTGRE_DB = PostGreDBConnector()
MONGO_DB = MongoDBConnector()

PROTOTYPE = Prototype(mongo_db=MONGO_DB, postgre_db=POSTGRE_DB)
print("Begin: " + str(time.time()))
parser = RDFParser(POSTGRE_DB)
parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/persons.rdf")
parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/locations.rdf")
#global tagger
#tagger = POSTagger("tree-tagger")
#pos_tagging()
PROTOTYPE.get_db_text()  # Sentence mode


print("End: " + str(time.time()))


#print(PROTOTYPE.get_sentence_window("wie", "Hallo, wie geht es dir?"))