import unittest
from PMI.Parser import Parser


class TestGermanParser(unittest.TestCase):
    parser = Parser()

    def test1(self):
        doc = self.parser.nlp("Mein kleiner Hase.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        tags = [(t.orth_, t.pos_) for t in doc]
        result_regex = list(self.parser.get_adjs(tags))
        expected_result = [{'noun': 'Hase', 'adj': 'klein'}]
        self.assertListEqual(expected_result, result_spacy)
        #self.assertListEqual(expected_result, result_regex)

    def test2(self):
        doc = self.parser.nlp("Der kleine Hase heißt Max.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        tags = [(t.orth_, t.pos_) for t in doc]
        result_regex = list(self.parser.get_adjs(tags))
        expected_result = [{'noun': 'Hase', 'adj': 'klein'}]
        self.assertListEqual(expected_result, result_spacy)
        #self.assertListEqual(expected_result, result_regex)

    def test3(self):
        doc = self.parser.nlp("Schöne Mädchen und hübsche Jungen sitzen auf der gelben Bank.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        tags = [(t.orth_, t.pos_) for t in doc]
        result_regex = list(self.parser.get_adjs(tags))
        expected_result = [{'noun': 'Mädchen', 'adj': 'schön'}, {'noun': 'Jungen', 'adj': 'hübsch'}, {'noun': 'Bank', 'adj': 'gelb'}]
        self.assertListEqual(expected_result, result_spacy)
        #self.assertListEqual(expected_result, result_regex)

    def test4(self):
        doc = self.parser.nlp("Der kleine, süße Hase war auf dem Weg nach Hause.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        tags = [(t.orth_, t.pos_) for t in doc]
        result_regex = list(self.parser.get_adjs(tags))
        expected_result= [{'noun': 'Hase', 'adj': 'klein'}, {'noun': 'Hase', 'adj': 'süß'}]
        self.assertListEqual(expected_result, result_spacy)
        #self.assertListEqual(expected_result, result_regex)

    def test5(self):
        doc = self.parser.nlp("Der kleine und süße Hase war Marias Haustier.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        tags = [(t.orth_, t.pos_) for t in doc]
        result_regex = list(self.parser.get_adjs(tags))
        expected_result = [{'noun': 'Hase', 'adj': 'klein'}, {'noun': 'Hase', 'adj': 'süß'}]
        self.assertListEqual(expected_result, result_spacy)
        #self.assertListEqual(expected_result, result_regex)

    def test6(self):
        doc = self.parser.nlp("Der kleine, aber freche Hase wusste wie er sich zu wehren hatte.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        tags = [(t.orth_, t.pos_) for t in doc]
        result_regex = list(self.parser.get_adjs(tags))
        expected_result = [{'noun': 'Hase', 'adj': 'klein'}, {'noun': 'Hase', 'adj': 'frech'}]
        self.assertListEqual(expected_result, result_spacy)
        #self.assertListEqual(expected_result, result_regex)

    def test7(self):
        doc = self.parser.nlp("Der Hase ist klein, aber kein Kuscheltier.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        tags = [(t.orth_, t.pos_) for t in doc]
        result_regex = list(self.parser.get_adjs(tags))
        expected_result = [{'noun': 'Hase', 'adj': 'klein'}]
        self.assertListEqual(expected_result, result_spacy)
        #self.assertListEqual(expected_result, result_regex)

    def test8(self):
        doc = self.parser.nlp("Eine bahnbrechende physikalische Entdeckung wurde letztes Jahr auf der Messe X vorgestellt.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        tags = [(t.orth_, t.pos_) for t in doc]
        result_regex = list(self.parser.get_adjs(tags))
        expected_result = [{'noun': 'Entdeckung', 'adj': 'bahnbrechend'}, {'noun': 'Entdeckung', 'adj': 'pysikalisch'}]
        self.assertListEqual(expected_result, result_spacy)
        #self.assertListEqual(expected_result, result_regex)
