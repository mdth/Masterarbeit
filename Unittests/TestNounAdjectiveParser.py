import unittest
from PMI.Parser import Parser


class TestGermanParser(unittest.TestCase):
    parser = Parser()

    def test1(self):
        doc = self.parser.nlp("Mein kleiner Hase.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        expected_result = [{'noun': 'Hase', 'adj': 'klein'}]
        self.assertListEqual(expected_result, result_spacy)

    def test2(self):
        doc = self.parser.nlp("Der kleine Hase heißt Max.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        expected_result = [{'noun': 'Hase', 'adj': 'klein'}]
        self.assertListEqual(expected_result, result_spacy)

    def test3(self):
        doc = self.parser.nlp("Schöne Mädchen und hübsche Jungen sitzen auf der gelben Bank.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        expected_result = [{'noun': 'Mädchen', 'adj': 'schön'}, {'noun': 'Jungen', 'adj': 'hübsch'}, {'noun': 'Bank', 'adj': 'gelb'}]
        self.assertListEqual(expected_result, result_spacy)

    def test4(self):
        doc = self.parser.nlp("Der süße, kleine Hase war auf dem Weg nach Hause.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        expected_result= [{'noun': 'Hase', 'adj': 'süsse'}, {'noun': 'Hase', 'adj': 'klein'}]
        self.assertListEqual(expected_result, result_spacy)

    def test5(self):
        doc = self.parser.nlp("Der kleine und süße Hase war Marias Haustier.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        expected_result = [{'noun': 'Hase', 'adj': 'klein'}, {'noun': 'Hase', 'adj': 'süsse'}]
        self.assertListEqual(expected_result, result_spacy)

    def test6(self):
        doc = self.parser.nlp("Der kleine, aber sehr freche Hase wusste wie er sich zu wehren hatte.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        # "kleinen" instead of "klein" <- it's tagged as noun
        # "freche" instead of "frech" <- it's lemmatized wrong
        expected_result = [{'noun': 'Hase', 'adj': 'kleinen'}, {'noun': 'Hase', 'adj': 'freche'}]
        self.assertListEqual(expected_result, result_spacy)

    def test7(self):
        # this adjective is a predicate, so this parser can't find it
        doc = self.parser.nlp("Der Hase ist klein, aber kein Kuscheltier.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        expected_result = []
        self.assertListEqual(expected_result, result_spacy)

    def test8(self):
        doc = self.parser.nlp("Eine bahnbrechende physikalische Entdeckung wurde letztes Jahr auf der Messe X vorgestellt.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        # thanks to the bad lemmatizer we get "bahnbrechende" instead of "bahnbrechend" <- it's tagged as noun
        expected_result = [{'noun': 'Entdeckung', 'adj': 'bahnbrechende'}, {'noun': 'Entdeckung', 'adj':
            'physikalisch'}, {'noun': 'Jahr', 'adj': 'letzt'}]
        self.assertListEqual(expected_result, result_spacy)

    def test9(self):
        doc = self.parser.nlp("Die unklare, angsteinflößende und unzumutbare Situation wurde unter Kontrolle gebracht.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        # thanks to the bad lemmatizer we get "bahnbrechende" instead of "bahnbrechend" <- it's tagged as noun
        expected_result = [{'noun': 'Situation', 'adj': 'unklaren'}, {'noun': 'Situation', 'adj':
            'angsteinflössende'}, {'noun': 'Situation', 'adj': 'unzumutbar'}]
        self.assertListEqual(expected_result, result_spacy)

    def test10(self):
        # this adjective is a predicate, so this parser can't find it
        doc = self.parser.nlp("Oh, wunderschönes New York.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        # thanks to the bad lemmatizer we get "wunderschön" instead of "wunderschönes" <- it's tagged as noun
        expected_result = [{'noun': 'New York', 'adj': 'wunderschönes'}]
        self.assertListEqual(expected_result, result_spacy)

    def test11(self):
        # this adjective is a predicate, so this parser can't find it
        doc = self.parser.nlp("Im warmen Playa de la Cruz gibt es viele deutsche Touristen.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        # thanks to the bad lemmatizer we get "wunderschön" instead of "wunderschönes" <- it's tagged as noun
        expected_result = [{'noun': 'Playa de la Cruz', 'adj': 'warm'}, {'noun': 'Touristen', 'adj': 'deutsch'}]
        self.assertListEqual(expected_result, result_spacy)