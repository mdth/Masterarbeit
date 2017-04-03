import unittest
from collections import namedtuple
from PMI.Parser import Parser


class TestGermanParser(unittest.TestCase):
    parser = Parser()
    svo_obj = namedtuple('svo_object', ['subject', 'object', 'verb'])

    def test1(self):
        doc = self.parser.nlp("Ich fahre mein Auto.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Ich', object='Auto', verb='fahre')]
        self.assertListEqual(expected_result, result_spacy)

    def test2(self):
        doc = self.parser.nlp("Ich wünsche mir einen Tannenbaum.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Ich', object='Tannenbaum', verb='wünsche')]
        self.assertListEqual(expected_result, result_spacy)

    def test3(self):
        doc = self.parser.nlp("Ich bin Berliner.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Ich', object='Berliner', verb='bin')]
        self.assertListEqual(expected_result, result_spacy)

    def test4(self):
        doc = self.parser.nlp("Ich hasse dich!")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Ich', object='dich', verb='hasse')]
        self.assertListEqual(expected_result, result_spacy)

    def test5(self):
        doc = self.parser.nlp("Das Haus ist grün.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Haus', object='grün', verb='ist')]
        self.assertListEqual(expected_result, result_spacy)

    def test6(self):
        doc = self.parser.nlp("Ich bin alt geworden.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Ich', object='alt', verb='bin')]
        self.assertListEqual(expected_result, result_spacy)

    def test7(self):
        doc = self.parser.nlp("Anna isst einen Apfel und eine Birne.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Anna', object='Apfel', verb='isst'),
                           self.svo_obj(subject='Anna', object='Birne', verb='isst')]
        self.assertListEqual(expected_result, result_spacy)

    def test8(self):
        doc = self.parser.nlp("Den Mann biss der Hund.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Hund', object='Mann', verb='biss')]
        self.assertListEqual(expected_result, result_spacy)

    def test9(self):
        doc = self.parser.nlp("Ich bin Informatiker und Musiker.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Ich', object='Informatiker', verb='bin'),
                           self.svo_obj(subject='Ich', object='Musiker', verb='bin')]
        self.assertListEqual(expected_result, result_spacy)

    def test10(self):
        doc = self.parser.nlp("Dieser Hund gehört mir und er ist ein Terrier.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Hund', object='mir', verb='gehört'),
                           self.svo_obj(subject='er', object='Terrier', verb='ist')]
        self.assertListEqual(expected_result, result_spacy)

    def test11(self):
        doc = self.parser.nlp("Rosen sind rot und Veilchen sind blau.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Rosen', object='rot', verb='sind'),
                           self.svo_obj(subject='Veilchen', object='blau', verb='sind')]
        self.assertListEqual(expected_result, result_spacy)

    def test12(self):
        doc = self.parser.nlp("Anna ist meine Schwester, Robert ist mein Bruder.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Anna', object='Schwester', verb='ist'),
                           self.svo_obj(subject='Robert', object='Bruder', verb='ist')]
        self.assertListEqual(expected_result, result_spacy)

    def test13(self):
        doc = self.parser.nlp("Anna ist meine Schwester, aber Anna verachtet mich.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Anna', object='Schwester', verb='ist'),
                           self.svo_obj(subject='Anna', object='mich', verb='verachtet')]
        self.assertListEqual(expected_result, result_spacy)

    def test14(self):
        doc = self.parser.nlp("Ich fühle mich gesund und munter.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Ich', object='gesund', verb='fühle'),
                           self.svo_obj(subject='Ich', object='munter', verb='fühle')]
        self.assertListEqual(expected_result, result_spacy)

    def test15(self):
        doc = self.parser.nlp("Ich esse gut und viel.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Ich', object='gut', verb='esse'),
                           self.svo_obj(subject='Ich', object='viel', verb='esse')]
        self.assertListEqual(expected_result, result_spacy)

    def test16(self):
        doc = self.parser.nlp("Hannah und Sarah sind jung.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Hannah', object='jung', verb='sind'),
                           self.svo_obj(subject='Sarah', object='jung', verb='sind')]
        self.assertListEqual(expected_result, result_spacy)

    def test17(self):
        doc = self.parser.nlp("Hannah, Lisa und Sarah sind jung.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Hannah', object='jung', verb='sind'),
                           self.svo_obj(subject='Lisa', object='jung', verb='sind'),
                           self.svo_obj(subject='Sarah', object='jung', verb='sind')]
        self.assertListEqual(expected_result, result_spacy)

    def test18(self):
        doc = self.parser.nlp("Herr Paul war ein einsamer Einsiedler.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = [self.svo_obj(subject='Herr Paul', object='Einsiedler', verb='war')]
        self.assertListEqual(expected_result, result_spacy)