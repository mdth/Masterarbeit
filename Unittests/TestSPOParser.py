import unittest
from collections import namedtuple
from PMI.Parser import Parser


class TestGermanParser(unittest.TestCase):
    parser = Parser()
    svo_obj = namedtuple('svo_object', ['subject', 'object', 'verb'])

    def test1(self):
        doc = self.parser.nlp("Ich fahre mein Auto.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='ich', object='Auto', verb='fahren')]
        self.assertListEqual(expected_result, result_spacy)

    def test2(self):
        doc = self.parser.nlp("Ich wünsche mir einen Tannenbaum.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='ich', object='Tannenbaum', verb='wünschen')]
        self.assertListEqual(expected_result, result_spacy)

    def test3(self):
        doc = self.parser.nlp("Ich bin Berliner.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='ich', object='Berliner', verb='sein')]
        self.assertListEqual(expected_result, result_spacy)

    def test4(self):
        doc = self.parser.nlp("Ich hasse dich!")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='ich', object='du', verb='hassen')]
        self.assertListEqual(expected_result, result_spacy)

    def test5(self):
        doc = self.parser.nlp("Das Haus ist grün.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Haus', object='grün', verb='sein')]
        self.assertListEqual(expected_result, result_spacy)

    def test6(self):
        doc = self.parser.nlp("Ich bin alt geworden.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='ich', object='alt', verb='sein')]
        self.assertListEqual(expected_result, result_spacy)

    def test7(self):
        doc = self.parser.nlp("Anna isst einen Apfel und eine Birne.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Anna', object='Apfel', verb='essen'),
                           self.svo_obj(subject='Anna', object='Birne', verb='essen')]
        self.assertListEqual(expected_result, result_spacy)

    def test8(self):
        doc = self.parser.nlp("Den Mann biss der Hund.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Hund', object='Mann', verb='beißen')]
        self.assertListEqual(expected_result, result_spacy)

    def test9(self):
        doc = self.parser.nlp("Ich bin Informatiker und Musiker.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='ich', object='Informatiker', verb='sein'),
                           self.svo_obj(subject='ich', object='Musiker', verb='sein')]
        self.assertListEqual(expected_result, result_spacy)

    def test10(self):
        doc = self.parser.nlp("Dieser Hund gehört mir und er ist ein Terrier.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Hund', object='ich', verb='gehören|hören'),
                           self.svo_obj(subject='er', object='Terrier', verb='sein')]
        self.assertListEqual(expected_result, result_spacy)

    def test11(self):
        doc = self.parser.nlp("Rosen sind rot und Veilchen sind blau.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Rose', object='rot', verb='sein'),
                           self.svo_obj(subject='Veilchen', object='blau', verb='sein')]
        self.assertListEqual(expected_result, result_spacy)

    def test12(self):
        doc = self.parser.nlp("Anna ist meine Schwester, Robert ist mein Bruder.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Anna', object='Schwester', verb='sein'),
                           self.svo_obj(subject='Robert', object='Bruder', verb='sein')]
        self.assertListEqual(expected_result, result_spacy)

    def test13(self):
        doc = self.parser.nlp("Anna ist meine Schwester, aber Anna verachtet mich.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Anna', object='Schwester', verb='sein'),
                           self.svo_obj(subject='Anna', object='ich', verb='verachten')]
        self.assertListEqual(expected_result, result_spacy)

    def test14(self):
        doc = self.parser.nlp("Ich fühle mich gesund und munter.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='ich', object='gesund', verb='fühlen'),
                           self.svo_obj(subject='ich', object='munter', verb='fühlen')]
        self.assertListEqual(expected_result, result_spacy)

    def test15(self):
        doc = self.parser.nlp("Ich esse gut und viel.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='ich', object='gut', verb='essen'),
                           self.svo_obj(subject='ich', object='viel', verb='essen')]
        self.assertListEqual(expected_result, result_spacy)

    def test16(self):
        doc = self.parser.nlp("Hannah und Sarah sind jung.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Hannah', object='jung', verb='sein'),
                           self.svo_obj(subject='Sarah', object='jung', verb='sein')]
        self.assertListEqual(expected_result, result_spacy)

    def test17(self):
        doc = self.parser.nlp("Hannah, Lisa und Sarah sind jung.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Hannah', object='jung', verb='sein'),
                           self.svo_obj(subject='Lisa', object='jung', verb='sein'),
                           self.svo_obj(subject='Sarah', object='jung', verb='sein')]
        self.assertListEqual(expected_result, result_spacy)

    def test18(self):
        doc = self.parser.nlp("Herr Paul war ein einsamer Einsiedler.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Herr Paul', object='Einsiedler', verb='sein')]
        self.assertListEqual(expected_result, result_spacy)