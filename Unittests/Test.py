import unittest
from RDFParser import RDFParser
from Prototype import Prototype
from MongoDBConnector import MongoDBConnector
from PostGreDBConnector import PostGreDBConnector
from HelperMethods import read_in_txt_file


class Test(unittest.TestCase):
    mongodb = MongoDBConnector()
    postgredb = PostGreDBConnector()

    def setUp(self):
        self.Prototype = Prototype(mongo_db=self.mongodb, postagger="spacy-tagger", postgre_db=self.postgredb,
                                   sentence_mode=True, window_size=0)

        parser = RDFParser(self.postgredb)
        parser.get_pattern_and_push("../persons.rdf")

    def test(self):
        self.Prototype.find_text_window(read_in_txt_file("Der Idiot - Zusammenfassung.txt"), 1, None)
        self.Prototype.aggregation()
        self.Prototype.find_spo_and_adjectives()

if __name__ == '__main__':
    unittest.main()