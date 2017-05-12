from RDFParser import RDFParser
from Prototype import Prototype
from MongoDBConnector import MongoDBConnector
from PostGreDBConnector import PostGreDBConnector
from HelperMethods import read_in_csv_file

MONGO_DB = MongoDBConnector()
POSTGRE_DB = PostGreDBConnector()

dostojewski = "dostojewski"
storm = "storm"
storm1 = "storm_word_window"
storm2 = "storm_punctuation"
PROTOTYPE = Prototype(
    mongo_db=MONGO_DB, postagger="spacy-tagger", postgre_db=POSTGRE_DB, sentence_mode=True, window_size=0)
parser = RDFParser(POSTGRE_DB)
#parser.get_pattern_and_push(dostojewski, "persons.rdf")
#parser.get_pattern_and_push(dostojewski, "locations.rdf")
#print("Done RDF parsing.")

## using constraints
##constraints = read_in_csv_file("C:/Users/din_m/PycharmProjects/Masterarbeit/constraints.csv")
##PROTOTYPE.get_snippets(constraints)

#PROTOTYPE.get_snippets(dostojewski, None)
#print("Extraction of snippets done.")
#PROTOTYPE.aggregation(dostojewski)
#print("Aggregation of q-calculus done.")
#PROTOTYPE.find_spo_and_adjectives(dostojewski)
#print("Extraction of SPO and adjective noun pairs done.")
#PROTOTYPE.calculate_pmi(dostojewski)
#print("Calculation of PMI done.")
#PROTOTYPE.get_result(dostojewski)
#print("Printed results.")
#PROTOTYPE.intersect_bscale(dostojewski, "FemMainCharacter", "Character", "MainCharacter", "Female")
#print("Added new bscale.")

###########
#PROTOTYPE.create_new_schema(storm1)
#PROTOTYPE.create_new_schema(storm2)
#parser.get_pattern_and_push(storm, "Ontologie_Farbe.rdf")
#parser.get_pattern_and_push(storm, "Ontologie_Natur.rdf")
#parser.get_pattern_and_push(storm, "Ontologie_Orte.rdf")
#parser.get_pattern_and_push(storm, "Ontologie_Sozial.rdf")

#parser.get_pattern_and_push(storm1, "Ontologie_Farbe.rdf")
#parser.get_pattern_and_push(storm1, "Ontologie_Natur.rdf")
#parser.get_pattern_and_push(storm1, "Ontologie_Orte.rdf")
#parser.get_pattern_and_push(storm1, "Ontologie_Sozial.rdf")

#parser.get_pattern_and_push(storm2, "Ontologie_Farbe.rdf")
#parser.get_pattern_and_push(storm2, "Ontologie_Natur.rdf")
#parser.get_pattern_and_push(storm2, "Ontologie_Orte.rdf")
#parser.get_pattern_and_push(storm2, "Ontologie_Sozial.rdf")
print(storm + ": Done RDF parsing.")


#PROTOTYPE.get_snippets(storm, None)
#PROTOTYPE.toggle_word_window_mode()
#PROTOTYPE.change_window_size(10)
#PROTOTYPE.get_snippets(storm1, None)
print("Extraction of snippets done.")
#PROTOTYPE.aggregation(storm)
#PROTOTYPE.aggregation(storm1)
#PROTOTYPE.aggregation(storm2)
print("Aggregation of q-calculus done.")

PROTOTYPE.find_correlating_pattern(storm)
print("Extraction of correlating pattern done.")
#PROTOTYPE.calculate_pmi(storm)
#PROTOTYPE.get_result(storm)

#m = re.search('willkommen', '"Hallo, willkommen."')
#print(m.start(), m.end())
#n = re.findall('willkommen', '"Hallo, willkommen."')