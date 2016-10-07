import time
from RDFParser import RDFParser
from Prototype import Prototype
from MongoDBConnector import MongoDBConnector
from PostGreDBConnector import PostGreDBConnector
from HelperMethods import read_in_csv_file


MONGO_DB = MongoDBConnector()
POSTGRE_DB = PostGreDBConnector()

PROTOTYPE = Prototype(mongo_db=MONGO_DB, postgre_db=POSTGRE_DB)
parser = RDFParser(POSTGRE_DB)
#parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/bscale_test.rdf")
#parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/persons.rdf")
parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/locations.rdf")

# using constraints
#constraints = read_in_csv_file("C:/Users/din_m/PycharmProjects/Masterarbeit/constraints.csv")
#PROTOTYPE.get_snippets(constraints)  # Sentence mode


PROTOTYPE.get_snippets()


PROTOTYPE.aggregation()

