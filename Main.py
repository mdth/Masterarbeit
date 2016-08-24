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
#parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/bscale_test.rdf")
#parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/persons.rdf")
parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/locations.rdf")
#pos_tagging()
PROTOTYPE.get_snippets(keyword="Petersburg", constraint="voller", position=-2)  # Sentence mode
#PROTOTYPE.get_snippets()
PROTOTYPE.aggregation()

print("End: " + str(time.time()))
