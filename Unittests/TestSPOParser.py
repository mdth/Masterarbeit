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
        doc = self.parser.nlp("Rosen sind rot und Veilchen sind blau.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = ('Rosen', 'rot', 'sind')
        self.assertEqual(expected_result, result_spacy)

    def test8(self):
        doc = self.parser.nlp("Ich bin Informatiker und Musiker.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = ('Ich', 'Informatiker', 'bin')
        self.assertEqual(expected_result, result_spacy)

    def test9(self):
        doc = self.parser.nlp("Den Mann biss der Hund.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = ('Hund', 'Mann', 'biss')
        self.assertEqual(expected_result, result_spacy)

    def test10(self):
        doc = self.parser.nlp("Dieser Hund gehört mir und er heißt Lola.")
        result_spacy = self.parser.get_SVO(doc)
        expected_result = ('Hund', 'mir', 'gehört')
        self.assertEqual(expected_result, result_spacy)

    def test10(self):
        doc = self.parser.nlp("Rosen sind rot und Veilchen sind blau.")
        result_spacy = self.parser.getsvo(doc)
        expected_result = ('Rosen', 'rot', 'sind')
        self.assertEqual(expected_result, result_spacy)