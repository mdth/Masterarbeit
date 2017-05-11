from RDFParser import RDFParser
from Prototype import Prototype
from MongoDBConnector import MongoDBConnector
from PostGreDBConnector import PostGreDBConnector
from HelperMethods import read_in_csv_file

MONGO_DB = MongoDBConnector()
POSTGRE_DB = PostGreDBConnector()

dostojewski = "dostojewski"
storm = "storm"
PROTOTYPE = Prototype(
    mongo_db=MONGO_DB, postagger="spacy-tagger", postgre_db=POSTGRE_DB, sentence_mode=True, window_size=0)
parser = RDFParser(POSTGRE_DB)
parser.get_pattern_and_push(dostojewski, "persons.rdf")
parser.get_pattern_and_push(dostojewski, "locations.rdf")
print("Done RDF parsing.")

## using constraints
##constraints = read_in_csv_file("C:/Users/din_m/PycharmProjects/Masterarbeit/constraints.csv")
##PROTOTYPE.get_snippets(constraints)

PROTOTYPE.get_snippets(dostojewski, None)
print("Extraction of snippets done.")
PROTOTYPE.aggregation(dostojewski)
print("Aggregation of q-calculus done.")
#PROTOTYPE.find_spo_and_adjectives()
#print("Extraction of SPO and adjective noun pairs done.")
#PROTOTYPE.calculate_pmi()
#PROTOTYPE.get_result()
#PROTOTYPE.intersect_bscale("FemMainCharacter", "Character", "MainCharacter", "Female")


###########
parser.get_pattern_and_push(storm, "Ontologie_Farbe.rdf")
parser.get_pattern_and_push(storm, "Ontologie_Natur.rdf")
parser.get_pattern_and_push(storm, "Ontologie_Orte.rdf")
parser.get_pattern_and_push(storm, "Ontologie_Sozial.rdf")
print("Done RDF parsing.")

## using constraints
##constraints = read_in_csv_file("C:/Users/din_m/PycharmProjects/Masterarbeit/constraints.csv")
#PROTOTYPE.get_snippets(constraints)

PROTOTYPE.get_snippets(storm, None)
print("Extraction of snippets done.")
PROTOTYPE.aggregation(storm)
print("Aggregation of q-calculus done.")

#PROTOTYPE.find_spo_and_adjectives()
#print("Extraction of SPO and adjective noun pairs done.")
#PROTOTYPE.calculate_pmi()
#PROTOTYPE.get_result()
#PROTOTYPE.intersect_bscale("FemMainCharacter", "Character", "MainCharacter", "Female")

#m = re.search('willkommen', '"Hallo, willkommen."')
#print(m.start(), m.end())
#n = re.findall('willkommen', '"Hallo, willkommen."')