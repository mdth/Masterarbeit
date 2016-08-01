import time
from RDFParser import RDFParser
from Prototype import Prototype
from MongoDBConnector import MongoDBConnector
from PostGreDBConnector import PostGreDBConnector


MONGO_DB = MongoDBConnector()
POSTGRE_DB = PostGreDBConnector()

PROTOTYPE = Prototype(mongo_db=MONGO_DB, postgre_db=POSTGRE_DB)
print("Begin: " + str(time.time()))
parser = RDFParser(POSTGRE_DB)
parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/persons.rdf")
parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/locations.rdf")
#pos_tagging()
PROTOTYPE.get_snippets()  # Sentence mode
PROTOTYPE.aggregation()


print("End: " + str(time.time()))