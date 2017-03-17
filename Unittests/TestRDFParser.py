import unittest
from PostGreDBConnector import PostGreDBConnector
from RDFParser import RDFParser


class TestRDFParser(unittest.TestCase):
    POSTGRE_DB = PostGreDBConnector()
    rdfparser = RDFParser(POSTGRE_DB)

    def test_get_pattern_from_rdf1(self):
        self.rdfparser.get_pattern_from_rdf()

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())

if __name__ == '__main__':
    unittest.main()