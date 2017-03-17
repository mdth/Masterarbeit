import unittest
from PMI.Parser import Parser


class TestGermanParser(unittest.TestCase):
    parser = Parser()

    def test1(self):
        doc = self.parser.nlp("Ich fahre mein Auto.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = ('Ich', 'Auto', 'fahre')
        self.assertEqual(expected_result, result_spacy)

    def test2(self):
        doc = self.parser.nlp("Ich wünsche mir einen Tannenbaum.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = ('Ich', 'Tannenbaum', 'wünsche')
        self.assertEqual(expected_result, result_spacy)

    def test3(self):
        doc = self.parser.nlp("Ich bin Berliner.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = ('Ich', 'Berliner', 'bin')
        self.assertEqual(expected_result, result_spacy)

    def test4(self):
        doc = self.parser.nlp("Ich hasse dich!")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = ('Ich', 'dich', 'hasse')
        self.assertEqual(expected_result, result_spacy)

    def test5(self):
        doc = self.parser.nlp("Das Haus ist grün.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = ('Haus', 'grün', 'ist')
        self.assertEqual(expected_result, result_spacy)

    def test6(self):
        doc = self.parser.nlp("Ich bin alt geworden.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = ('Ich', 'alt', 'bin')
        self.assertEqual(expected_result, result_spacy)

    def test7(self):
        doc = self.parser.nlp("Anna isst einen Apfel und eine Birne.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = ('Anna', 'Apfel', 'isst')
        self.assertEqual(expected_result, result_spacy)

    def test8(self):
        doc = self.parser.nlp("Den Mann biss der Hund.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = ('Hund', 'Mann', 'biss')
        self.assertEqual(expected_result, result_spacy)

    def test9(self):
        doc = self.parser.nlp("Ich bin Informatiker und Musiker.")
        result_spacy = list(self.parser.getsvo(doc))
        expected_result = [('Ich', 'Informatiker', 'bin'), ('Ich','Musiker', 'bin')]
        self.assertListEqual(expected_result, result_spacy)

    def test10(self):
        doc = self.parser.nlp("Dieser Hund gehört mir und er ist ein Terrier.")
        result_spacy = list(self.parser.getsvo(doc))
        expected_result = [('Hund', 'mir', 'gehört'), ('er', 'Terrier', 'ist')]
        self.assertEqual(expected_result, result_spacy)

    def test11(self):
        doc = self.parser.nlp("Rosen sind rot und Veilchen sind blau.")
        result_spacy = list(self.parser.getsvo(doc))
        expected_result = [('Rosen', 'rot', 'sind'),('Veilchen', 'blau', 'sind')]
        self.assertListEqual(expected_result, result_spacy)

    def test12(self):
        doc = self.parser.nlp("Anna ist meine Schwester, Robert ist mein Bruder.")
        result_spacy = list(self.parser.getsvo(doc))
        expected_result = [('Anna', 'Schwester', 'ist'),('Robert', 'Bruder', 'ist')]
        self.assertListEqual(expected_result, result_spacy)

    def test13(self):
        doc = self.parser.nlp("Anna ist meine Schwester, aber Anna verachtet mich.")
        result_spacy = list(self.parser.getsvo(doc))
        expected_result = [('Anna', 'Schwester', 'ist'),('Robert', 'Bruder', 'ist')]
        self.assertListEqual(expected_result, result_spacy)

    def test14(self):
        doc = self.parser.nlp("Ich fühle mich gesund und munter.")
        result_spacy = list(self.parser.getsvo(doc))
        expected_result = [('Ich', 'gesund', 'fühle'), ('Ich', 'munter', 'fühle')]
        self.assertListEqual(expected_result, result_spacy)

    def test15(self):
        doc = self.parser.nlp("Ich esse gut und viel.")
        result_spacy = list(self.parser.getsvo(doc))
        expected_result = [('Ich', 'gut', 'esse'), ('Ich', 'viel', 'esse')]
        self.assertListEqual(expected_result, result_spacy)

    def test16(self):
        doc = self.parser.nlp("Hannah und Sarah sind Freunde.")
        result_spacy = list(self.parser.getsvo(doc))
        expected_result = []
        self.assertListEqual(expected_result, result_spacy)